import requests

def obtener_precio_bitcoin():
    # API pública de Coinbase para el par BTC-USD
    url = "https://api.coinbase.com/v2/prices/BTC-USD/spot"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    try:
        # Hacemos la petición a la API
        respuesta = requests.get(url, headers=headers, timeout=10)
        respuesta.raise_for_status()
        
        # Parseamos el JSON
        datos = respuesta.json()
        precio = float(datos['data']['amount'])
        
        print(f" El precio actual de Bitcoin es: ${precio:,.2f} USD")
        
    except Exception as e:
        print(f"Ocurrió un error al consultar la API: {e}")

if __name__ == "__main__":
    print("Iniciando consulta de mercado...")
    obtener_precio_bitcoin()