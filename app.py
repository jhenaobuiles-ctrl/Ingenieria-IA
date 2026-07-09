import os
import socket
import streamlit as st
from pypdf import PdfReader

# 1. PARCHE DE RED: Forzar IPv4 seguro (evita caídas getaddrinfo en entornos Windows)
_orig_getaddrinfo = socket.getaddrinfo
socket.getaddrinfo = lambda *args, **kwargs: _orig_getaddrinfo(*args, **kwargs)[:1]

from google import genai
from google.genai import types
from dotenv import load_dotenv

# 2. CARGA HÍBRIDA DE API KEY (Busca en .env local o en Secrets de Streamlit Cloud)
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    try:
        GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)
else:
    st.error("No se encontró 'GEMINI_API_KEY'. Configúrala en tu archivo .env (local) o en los Secrets de Streamlit (nube).")
    st.stop()

# 3. MOTOR RAG OPTIMIZADO (Chunking inteligente por estructuras de párrafo y solapamiento)
def generar_respuesta_rag_inteligente(pregunta, texto_completo, chunk_size=2000, overlap=400):
    # 1. Segmentación del texto por párrafos lógicos
    bloques = texto_completo.split("\n\n")
    chunks = []
    chunk_actual = ""
    
    for b in bloques:
        if len(chunk_actual) + len(b) < chunk_size:
            chunk_actual += "\n\n" + b if chunk_actual else b
        else:
            if chunk_actual: chunks.append(chunk_actual)
            chunk_actual = chunk_actual[-overlap:] + "\n\n" + b if overlap < len(chunk_actual) else b
    if chunk_actual: chunks.append(chunk_actual)

    # 2. QUERY EXPANSION: Traducción + Sinónimos Conceptuales para el PDF
    keywords_ingles = []
    prompt_expansion = (
        f"Analyze this Spanish query: '{pregunta}'. Extract 8 English keywords, including direct translations, "
        "synonyms, and broad conceptual terms (e.g., if the query asks for 'riesgos', include terms like "
        "'uncertainty', 'challenges', 'policy', 'outlook', 'factors'). "
        "Return only the keywords separated by commas, nothing else."
    )
    
    try:
        res_kw = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_expansion)
        keywords_ingles = [k.strip().lower() for k in res_kw.text.split(",") if len(k.strip()) > 3]
    except Exception:
        pass # Si falla la expansión, el RAG continuará con las palabras en español

    # Combinación de palabras clave (Español + Inglés)
    palabras_clave = [w.lower() for w in pregunta.split() if len(w) > 4] + keywords_ingles
    
    # 3. Buscador de fragmentos por coincidencia expandida
    chunk_seleccionado = chunks[0] if chunks else ""
    max_coincidencias = 0
    for c in chunks:
        coincidencias = sum(1 for kw in palabras_clave if kw in c.lower())
        if coincidencias > max_coincidencias:
            max_coincidencias = coincidencias
            chunk_seleccionado = c

    # 4. Prompt final en español para el Analista
    prompt_rag = (
        "Eres un analista financiero experto. Responde la pregunta en ESPAÑOL utilizando el contexto provisto.\n"
        "Interpreta las tablas o cifras con rigurosidad. Si la información no está o está incompleta, "
        "di estrictamente: 'No encontré esa información'.\n\n"
        f"CONTEXTO:\n{chunk_seleccionado}\n\nPREGUNTA:\n{pregunta}"
    )
    
    try:
        res = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=prompt_rag, 
            config=types.GenerateContentConfig(temperature=0.0)
        )
        return res.text.strip()
    except Exception as e:
        return f"⚠️ Error al consultar el modelo: {str(e)}"


# 4. CONFIGURACIÓN Y MAQUETACIÓN DE LA INTERFAZ DE STREAMLIT
st.set_page_config(page_title="Analista RAG Financiero", page_icon="💼", layout="wide")
st.title("💼 Analista RAG Financiero Inteligente")

# Barra Lateral: Cargador de Reportes PDF
with st.sidebar:
    st.header("Configuración")
    archivo_cargado = st.file_uploader("Sube tu reporte financiero (PDF)", type=["pdf"])
    
    if archivo_cargado is not None:
        if "texto_contexto" not in st.session_state or st.session_state.get("nombre_archivo") != archivo_cargado.name:
            with st.spinner("Procesando y segmentando PDF estructuralmente..."):
                try:
                    reader = PdfReader(archivo_cargado)
                    texto_completo = ""
                    for pagina in reader.pages:
                        texto_extraido = pagina.extract_text()
                        if texto_extraido:
                            texto_completo += texto_extraido + "\n"
                    
                    # Almacenamiento persistente en la sesión web
                    st.session_state["texto_contexto"] = texto_completo
                    st.session_state["nombre_archivo"] = archivo_cargado.name
                    st.success(f"✅ Documento cargado: {len(reader.pages)} páginas procesadas.")
                except Exception as e:
                    st.error(f"❌ Error al procesar el archivo: {str(e)}")
    else:
        # Limpieza automática si el usuario remueve el archivo
        if "texto_contexto" in st.session_state:
            del st.session_state["texto_contexto"]
            del st.session_state["nombre_archivo"]
            if "messages" in st.session_state:
                del st.session_state["messages"]

# 5. CONTROL DEL FLUJO DEL CHAT COMPATIBLE CON EL CONTEXTO
if "messages" not in st.session_state:
    st.session_state.messages = []

# Renderizar el historial de conversación en la pantalla
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Evaluar si el contexto del PDF ya está disponible para habilitar la interacción
if "texto_contexto" in st.session_state:
    if prompt := st.chat_input("¿Qué cifra o análisis cualitativo deseas consultar?"):
        # Mostrar y guardar el mensaje del usuario
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Generar respuesta del RAG en tiempo real
        with st.chat_message("assistant"):
            with st.spinner("Buscando en bloques financieros..."):
                respuesta_rag = generar_respuesta_rag_inteligente(prompt, st.session_state["texto_contexto"])
                st.markdown(respuesta_rag)
        st.session_state.messages.append({"role": "assistant", "content": respuesta_rag})
else:
    st.info("👋 Para activar el chat del analista, por favor arrastra o selecciona un archivo PDF en la barra lateral.")