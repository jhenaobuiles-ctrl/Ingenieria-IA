import os
from dotenv import load_dotenv
import chromadb
from google import genai
from google.genai import types

# 1. Cargar entorno y claves
load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise SystemExit('Falta GEMINI_API_KEY en el archivo .env')

# 2. Inicializar clientes (Gemini API y ChromaDB local)
cliente = genai.Client(api_key=api_key)
chroma_client = chromadb.PersistentClient(path="./chroma_db")
coleccion = chroma_client.get_collection(name="reporte_financiero")

ROL = (
    "Eres un analista financiero claro y conciso. Respondes en español. "
    "Usa estrictamente el contexto proporcionado del reporte financiero para responder. "
    "Si la respuesta no se encuentra en el contexto, di amablemente que no cuentas "
    "con esa información en el documento."
)

def preguntar_asistente_rag(pregunta: str) -> str:
    # ChromaDB vectoriza la pregunta automáticamente de forma local y busca los 3 fragmentos top
    resultados = coleccion.query(
        query_texts=[pregunta],
        n_results=3
    )
    
    # Combinar el texto de los fragmentos encontrados
    if resultados and resultados['documents'] and resultados['documents'][0]:
        contexto = "\n\n".join(resultados['documents'][0])
    else:
        contexto = "No se encontró contexto relevante."
    
    # Construir el prompt para Gemini
    prompt_completo = f"Contexto extraído del reporte:\n{contexto}\n\nPregunta: {pregunta}"
    
    respuesta = cliente.models.generate_content(
        model='gemini-2.5-flash',
        config=types.GenerateContentConfig(
            system_instruction=ROL,
            temperature=0.2,
        ),
        contents=prompt_completo,
    )
    return respuesta.text

if __name__ == '__main__':
    print("==========================================================")
    print("    ASISTENTE RAG: CHATEA CON TU REPORTE FINANCIERO       ")
    print("==========================================================")
    print("Base de datos vectorial cargada con éxito localmente.")
    print("Escribe 'salir' para terminar el chat.")
    
    while True:
        duda = input('\nPregunta sobre el reporte: ')
        if duda.lower() == 'salir':
            break
        if not duda.strip():
            continue
            
        try:
            print("Buscando en la base de datos vectorial y generando respuesta...")
            respuesta_final = preguntar_asistente_rag(duda)
            print(f"\nRespuesta:\n{respuesta_final}")
        except Exception as e:
            print(f'\nError: {e}')