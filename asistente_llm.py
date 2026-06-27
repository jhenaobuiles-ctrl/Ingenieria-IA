import os
import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 1. Configurar variables de entorno y validar clave de API
load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    raise SystemExit('Error: No se encontró la variable GEMINI_API_KEY en el archivo .env')

# 2. Inicializar el cliente oficial de Gemini
cliente = genai.Client(api_key=api_key)

# 3. Definir las directivas globales del sistema (Rol)
ROL_SISTEMA = (
    "Eres un analista financiero sénior, experto en criptomonedas. "
    "Tu tono debe ser profesional, claro, analítico y muy conciso. "
    "Respondes siempre en español de forma directa y sin rodeos innecesarios."
)

def preguntar_llm(prompt_usuario: str, temperatura: float = 0.7) -> str:
    """
    Envía un prompt al modelo gemini-2.5-flash aplicando el rol de sistema y la temperatura especificada.
    """
    try:
        respuesta = cliente.models.generate_content(
            model='gemini-2.5-flash',
            config=types.GenerateContentConfig(
                system_instruction=ROL_SISTEMA,
                temperature=temperatura,
            ),
            contents=prompt_usuario,
        )
        return respuesta.text
    except Exception as e:
        return f"[ERROR] Error de comunicación con el LLM: {e}"

def ejecutar_analisis_datos() -> str:
    """
    Carga el CSV de precios cripto, calcula métricas clave con Pandas,
    y solicita un resumen analítico al LLM.
    """
    ruta_csv = 'precios_cripto.csv'
    
    # Validación física del archivo CSV generado en las semanas previas
    if not os.path.exists(ruta_csv):
        return (
            f"[ADVERTENCIA] No se encontró el archivo '{ruta_csv}' en el directorio actual.\n"
            "Asegúrate de copiar tu CSV de precios cripto de la Semana 4 a esta carpeta."
        )
    
    try:
        # Carga del dataset con Pandas
        df = pd.read_csv(ruta_csv)
        
        # Validar columnas necesarias
        if 'Cripto' not in df.columns or 'Precio_USD' not in df.columns:
            return "[Error] El CSV no contiene las columnas requeridas ('Cripto' y 'Precio_USD')."
            
        # Calcular estadísticas agrupadas básicas
        resumen = df.groupby('Cripto')['Precio_USD'].agg(['mean', 'min', 'max']).round(2)
        resumen.columns = ['Precio_Promedio', 'Precio_Minimo', 'Precio_Maximo']
        
        # Construcción del prompt con inyección de datos estructurados
        prompt_datos = (
            "Como analista, examina los siguientes datos de precios de criptomonedas procesados hoy.\n"
            "Resume en un máximo de 3 frases orientadas a un inversor no técnico qué está sucediendo, "
            "destacando alguna anomalía o punto de atención relevante:\n\n"
            f"{resumen.to_string()}\n"
        )
        
        # Llamar al LLM con temperatura baja para garantizar fidelidad analítica de los números
        analisis_narrativo = preguntar_llm(prompt_datos, temperatura=0.1)
        return analisis_narrativo
        
    except Exception as e:
        return f"[ERROR] Falló el procesamiento de datos o la generación de análisis: {e}"

if __name__ == '__main__':
    print("==================================================")
    print("   ASISTENTE INTELIGENTE DE ANÁLISIS FINANCIERO   ")
    print("==================================================")
    print("Cargando y analizando datos históricos con Pandas...")
    
    # Ejecutar de inmediato el Reto 1 (Integración de Datos + LLM)
    analisis_inicial = ejecutar_analisis_datos()
    print("\n--- INFORME EJECUTIVO DE CARTERA (LLM + PANDAS) ---")
    print(analisis_inicial)
    print("---------------------------------------------------\n")
    
    print("Iniciando chat interactivo. Escribe 'salir' para terminar.")
    while True:
        try:
            pregunta = input('\nTu pregunta: ')
            if pregunta.strip().lower() == 'salir':
                print("Finalizando sesión del asistente. ¡Hasta pronto!")
                break
                
            if not pregunta.strip():
                continue
                
            # Procesar la consulta interactiva
            respuesta = preguntar_llm(pregunta, temperatura=0.7)
            print("\n--- Respuesta del Analista ---")
            print(respuesta)
            print("------------------------------")
            
        except KeyboardInterrupt:
            print("\nSesión interrumpida por el usuario. Saliendo...")
            break