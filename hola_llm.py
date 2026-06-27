import os
from dotenv import load_dotenv
from google import genai

# 1. Cargar las variables de entorno desde el archivo .env local
load_dotenv()

# 2. Recuperar la API key cargada en el entorno de forma segura
api_key = os.getenv('GEMINI_API_KEY')

# Validar que la clave de API exista antes de inicializar el cliente
if not api_key:
    raise SystemExit('Error crítico: Falta la variable GEMINI_API_KEY en el archivo .env')

# 3. Inicializar el cliente oficial de Gemini utilizando el SDK google-genai
cliente = genai.Client(api_key=api_key)

# 4. Enviar un prompt de prueba al modelo y gestionar posibles excepciones
try:
    print("Enviando petición a Gemini (modelo: gemini-2.5-flash)...")
    
    respuesta = cliente.models.generate_content(
        model='gemini-2.5-flash',
        contents='Explica en una frase qué es una API.'
    )
    
    # Imprimir la respuesta devuelta por el modelo de lenguaje
    print("\n--- Respuesta del Modelo ---")
    print(respuesta.text)
    print("----------------------------")

except Exception as e:
    # Manejo de excepciones elegante ante fallos de conexión, límites de tarifa o credenciales inválidas
    print(f'\n[ERROR] No se pudo obtener respuesta del modelo de lenguaje: {e}')