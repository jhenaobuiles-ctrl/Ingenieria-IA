import requests
import csv
import json
from datetime import datetime
import os

# ==========================================
# 1. CONFIGURACIÓN
# ==========================================
CRIPTOS_CRUDAS = ['btc ', '  eth', 'Sol', 'ADA', 'usdt']
ARCHIVO_CSV = "precios_cripto.csv"
ARCHIVO_JSON = "precios_cripto.json"

# ==========================================
# 2. FUNCIONES SECUNDARIAS
# ==========================================

def limpiar_lista(lista_sucia):
    """Limpia espacios, pasa a mayúsculas y filtra USDT."""
    return [moneda.strip().upper() for moneda in lista_sucia if moneda.strip().lower() != 'usdt']


def consultar_precio(moneda):
    """Consulta la API de Coinbase para una moneda específica."""
    url = f"https://api.coinbase.com/v2/prices/{moneda}-USD/spot"
    respuesta = requests.get(url, timeout=5)
    respuesta.raise_for_status()
    datos = respuesta.json()
    return datos['data']['amount']


def guardar_en_csv(archivo, moneda, precio):
    """Maneja la persistencia en formato CSV (Tabular)."""
    archivo_nuevo = not os.path.exists(archivo)
    try:
        with open(archivo, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if archivo_nuevo:
                writer.writerow(['Fecha_Hora', 'Cripto', 'Precio_USD'])
            
            fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            writer.writerow([fecha_actual, moneda, precio])
            return True
    except PermissionError:
        print(f"⚠️ Error de Permiso en CSV: ¿Archivo abierto?")
        return False


def guardar_en_json(archivo, moneda, precio):
    """Maneja la persistencia en formato JSON de forma robusta con manejo de corrupción."""
    fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    nuevo_registro = {
        "fecha_hora": fecha_actual,
        "cripto": moneda,
        "precio_usd": float(precio)
    }
    
    historial = []
    
    if os.path.exists(archivo):
        try:
            with open(archivo, 'r', encoding='utf-8') as file:
                historial = json.load(file)
        except json.JSONDecodeError:
            print(f"⚠️ ¡Alerta! El archivo '{archivo}' está corrupto.")
            archivo_respaldo = archivo + ".bak"
            try:
                if os.path.exists(archivo_respaldo):
                    os.remove(archivo_respaldo)
                os.rename(archivo, archivo_respaldo)
                print(f"📦 Archivo corrupto respaldado como '{archivo_respaldo}'. Iniciando historial nuevo.")
            except OSError as e:
                print(f"❌ No se pudo respaldar el archivo corrupto: {e}")
            historial = []
            
    historial.append(nuevo_registro)
    
    try:
        with open(archivo, 'w', encoding='utf-8') as file:
            json.dump(historial, file, indent=4, ensure_ascii=False)
        return True
    except (PermissionError, OSError) as e:
        print(f"❌ Error al escribir JSON: {e}")
        return False


# 🌟 FUNCIÓN EVOLUCIONADA CON DICTIONARY COMPREHENSION
def analizar_historico_json(archivo, lista_monedas):
    """Lee el archivo JSON y calcula promedios masivos usando Dictionary Comprehensions."""
    if not os.path.exists(archivo):
        print("📋 No hay historial JSON para analizar todavía.")
        return

    try:
        with open(archivo, 'r', encoding='utf-8') as file:
            historial = json.load(file)
        
        print(f"\n--- 📊 AUDITORÍA DE DATOS MULTI-ACTIVO (Semana 3) ---")
        print(f"Total de registros históricos analizados: {len(historial)}")
        
        # 💡 DICTIONARY COMPREHENSION:
        # Genera un diccionario donde la 'clave' es la moneda y el 'valor' es su precio promedio.
        # Dentro, usa una list comprehension anidada para aislar los precios de esa moneda específica.
        promedios = {
            moneda: round(sum([r['precio_usd'] for r in historial if r['cripto'] == moneda]) / 
                          len([r['precio_usd'] for r in historial if r['cripto'] == moneda]), 4)
            for moneda in lista_monedas
            if any(r['cripto'] == moneda for r in historial) # Condición: Solo si la moneda existe en el historial
        }
        
        # Mostramos los resultados del diccionario generado
        print("\n📈 Precios Promedio Calculados:")
        for moneda, promedio in promedios.items():
            print(f"  - {moneda}: ${promedio}")
                
    except Exception as e:
        print(f"❌ Error al auditar el archivo JSON: {e}")


# ==========================================
# 3. FLUJO PRINCIPAL
# ==========================================
def main():
    print("--- Iniciando Pipeline de Datos Multi-Formato ---")
    criptos = limpiar_lista(CRIPTOS_CRUDAS)
    
    for moneda in criptos:
        try:
            precio = consultar_precio(moneda)
            csv_ok = guardar_en_csv(ARCHIVO_CSV, moneda, precio)
            json_ok = guardar_en_json(ARCHIVO_JSON, moneda, precio)
            
            if csv_ok and json_ok:
                print(f"✅ {moneda}: ${precio} - Guardado en CSV y JSON.")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de red con {moneda}: {e}")
        except Exception as e:
            print(f"❌ Error inesperado con {moneda}: {e}")

    # Pasamos también la lista de criptos limpias para la auditoría dinámica
    analizar_historico_json(ARCHIVO_JSON, criptos)


if __name__ == "__main__":
    main()