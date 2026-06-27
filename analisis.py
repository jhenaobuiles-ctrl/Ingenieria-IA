import pandas as pd
from pathlib import Path

# Configuración de rutas
RUTA_PROYECTO = Path(r"C:\Proyectos\Ingenieria-IA")
RUTA_CSV = RUTA_PROYECTO / "precios_cripto.csv"

def filtrar_por_ventana_tiempo(df: pd.DataFrame, minutos: int = 15) -> pd.DataFrame:
    """Filtra el DataFrame para obtener los registros de los últimos N minutos del dataset."""
    df = df.copy()
    
    # Encontrar el punto de tiempo más reciente en el CSV
    ultima_captura = df['Fecha_Hora'].max()
    
    # Calcular el límite inferior restando el intervalo de tiempo
    limite_tiempo = ultima_captura - pd.Timedelta(minutes=minutos)
    
    # Aplicar máscara booleana
    mascara = df['Fecha_Hora'] >= limite_tiempo
    df_filtrado = df[mascara]
    
    print(f"\n⏱️ Ventana de tiempo: Desde {limite_tiempo} hasta {ultima_captura} ({minutos} min)")
    print(f"📊 Registros encontrados en esta ventana: {len(df_filtrado)}")
    
    return df_filtrado.sort_values(by='Fecha_Hora', ascending=False)
def calcular_volatilidad(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula la desviación porcentual de cada precio respecto a su promedio histórico."""
    df = df.copy()
    
    # 1. Obtener el promedio de forma vectorizada alineado al DataFrame original
    promedio_por_cripto = df.groupby('Cripto')['Precio_USD'].transform('mean')
    
    # 2. Calcular la variación porcentual
    df['Variacion_Porcentaje'] = ((df['Precio_USD'] - promedio_por_cripto) / promedio_por_cripto) * 100
    
    return df

def cargar_datos(ruta: Path) -> pd.DataFrame:
    """Carga el archivo CSV en un DataFrame."""
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró el archivo de datos en: {ruta}")
    try:
        df = pd.read_csv(ruta)
        print(f"✅ Datos cargados exitosamente. Total registros: {len(df)}")
        return df
    except Exception as e:
        print(f"❌ Error al leer el archivo CSV: {e}")
        raise

def limpiar_y_estructurar(df: pd.DataFrame) -> pd.DataFrame:
    """Asegura tipos de datos correctos utilizando las columnas reales."""
    df = df.copy()
    df['Fecha_Hora'] = pd.to_datetime(df['Fecha_Hora'])
    df['Precio_USD'] = df['Precio_USD'].astype(float)
    
    print("\n--- Tipos de datos del DataFrame ---")
    print(df.dtypes)
    return df

def filtrar_y_ordenar(df: pd.DataFrame, moneda: str, precio_min: float) -> pd.DataFrame:
    """Filtra por criptomoneda y umbral de precio, ordenando descendentemente."""
    mascara = (df['Cripto'] == moneda) & (df['Precio_USD'] > precio_min)
    df_filtrado = df[mascara]
    return df_filtrado.sort_values(by='Precio_USD', ascending=False)

def generar_estadisticas_eda(df: pd.DataFrame) -> pd.DataFrame:
    """Genera métricas estadísticas agrupadas por activo."""
    print("\n==================================================")
    print("      RESUMEN ESTADÍSTICO GENERAL DEL DATASET     ")
    print("==================================================")
    print(df.describe())
    
    print("\n==================================================")
    print("     MÉTRICAS AVANZADAS POR CRIPTOMONEDA (EDA)     ")
    print("==================================================")
    
    resumen_cripto = df.groupby('Cripto')['Precio_USD'].agg(
        conteo='count',
        precio_minimo='min',
        precio_maximo='max',
        precio_promedio='mean',
        desviacion_estandar='std',
        mediana='median'
    )
    print(resumen_cripto)
    return resumen_cripto

if __name__ == "__main__":
    # 1. Cargar y limpiar
    df_raw = cargar_datos(RUTA_CSV)
    df_limpio = limpiar_y_estructurar(df_raw)
    
    # 2. Reto 1: Volatilidad
    df_con_volatilidad = calcular_volatilidad(df_limpio)
    
    # 3. Reto 2: Filtro temporal (últimos 15 minutos del histórico)
    df_recientes = filtrar_por_ventana_tiempo(df_con_volatilidad, minutos=15)
    print("\n--- Muestra de datos más recientes ---")
    print(df_recientes[['Fecha_Hora', 'Cripto', 'Precio_USD']].head(8))
    
    # 4. Filtrar por precio objetivo
    df_btc = filtrar_y_ordenar(df_con_volatilidad, moneda='BTC', precio_min=58500.0)
    
    # 5. Estadísticas descriptivas para EDA
    generar_estadisticas_eda(df_limpio)