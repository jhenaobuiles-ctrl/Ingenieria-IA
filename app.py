import streamlit as st
import pypdf
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

# 1. Carga automática de la configuración (.env)
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

# 2. Configuración de la Interfaz
st.set_page_config(page_title="RAG Financial Dashboard", page_icon="📊", layout="wide")
st.title("📊 Dashboard Financiero - Motor RAG Oficial")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "texto_pdf" not in st.session_state:
    st.session_state.texto_pdf = ""

# 3. Extracción de texto
def extraer_texto_pdf(uploaded_file):
    pdf_reader = pypdf.PdfReader(uploaded_file)
    return "".join([page.extract_text() or "" for page in pdf_reader.pages])

# 4. Barra Lateral
with st.sidebar:
    st.header("Documentos de Entrada")
    uploaded_file = st.file_uploader("Carga un PDF financiero", type=["pdf"])
    
    if uploaded_file and not st.session_state.texto_pdf:
        with st.spinner("Procesando documento..."):
            st.session_state.texto_pdf = extraer_texto_pdf(uploaded_file)
            st.success("¡PDF indexado correctamente!")

# 5. Renderizado del Historial
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. Flujo de Consulta
if prompt := st.chat_input("Haz una pregunta sobre el reporte..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        if st.session_state.texto_pdf:
            with st.spinner("Gemini está analizando..."):
                try:
                    prompt_sistema = (
                        "Eres un consultor financiero experto. Responde a la última pregunta usando "
                        "únicamente el contexto provisto abajo. Si la respuesta no está allí, di: "
                        "'No encontré esa información en el documento.'\n\n"
                        f"--- CONTEXTO DEL PDF ---\n{st.session_state.texto_pdf}\n------------------------"
                    )
                    
                    # Estructura de historial compatible con el nuevo SDK
                    contenido_historial = []
                    for msg in st.session_state.messages:
                        role = "user" if msg["role"] == "user" else "model"
                        contenido_historial.append({
                            "role": role, 
                            "parts": [{"text": msg["content"]}]
                        })
                    
                    # Consumir el nuevo cliente oficial
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=contenido_historial,
                        config=types.GenerateContentConfig(
                            system_instruction=prompt_sistema,
                            temperature=0.0
                        )
                    )
                    
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    
                except Exception as e:
                    st.error(f"Error en la API: {e}")
        else:
            st.warning("Por favor, carga un PDF en la barra lateral para activar el contexto.")