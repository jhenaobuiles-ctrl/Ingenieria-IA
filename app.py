import requests

def obtener_precio_cripto(sigla):
    # Convertimos a mayúsculas por si el usuario escribe en minúsculas
    sigla = sigla.upper()
    
    # Usamos una f-string para hacer la URL dinámica
    url = f"https://api.coinbase.com/v2/prices/{sigla}-USD/spot"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    try:
        respuesta = requests.get(url, headers=headers, timeout=10)
        
        # Si el usuario escribe una sigla que no existe (ej: "XYZ"), 
        # raise_for_status() capturará el error HTTP 404
        respuesta.raise_for_status()
        
        datos = respuesta.json()
        precio = float(datos['data']['amount'])
        
        print(f" El precio actual de {sigla} es: ${precio:,.2f} USD")
        
    except requests.exceptions.HTTPError:
        print(f"❌ Error: La moneda '{sigla}' no fue encontrada o no es válida para Coinbase.")
    except Exception as e:
        print(f"Ocurrió un error al consultar la API: {e}")

if __name__ == "__main__":
    print("--- CONSULTA DE MERCADO DINÁMICA ---")
    # Capturamos la entrada del usuario
    moneda_usuario = input("Introduce la sigla de la criptomoneda (ej: BTC, ETH, SOL, ADA): ")
    obtener_precio_cripto(moneda_usuario)