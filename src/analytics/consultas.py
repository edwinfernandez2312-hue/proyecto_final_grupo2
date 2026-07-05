import os
import pandas as pd
from google.cloud import bigquery
from dotenv import load_dotenv

# Cargar el entorno para asegurar el uso de las credenciales
load_dotenv()

ID_PROYECTO = os.getenv("ID_PROYECTO")

def obtener_cliente_bigquery():
    """Inicializa y devuelve el cliente nativo de BigQuery."""
    if not ID_PROYECTO:
        raise ValueError("❌ Error: La variable ID_PROYECTO no está configurada en el archivo .env")
    return bigquery.Client(project=ID_PROYECTO)

def ejecutar_consulta_sql(nombre_archivo_sql):
    """
    Lee un archivo SQL desde la carpeta de analytics, lo ejecuta en BigQuery
    y devuelve el resultado en un DataFrame de Pandas.
    """
    # Construcción de la ruta relativa hacia la carpeta sql/analytics desde src/analytics
    # Subimos dos niveles (de analytics -> src -> raíz) y entramos a sql
    ruta_base = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../sql"))
    ruta_completa = os.path.join(ruta_base, nombre_archivo_sql)
    
    if not os.path.exists(ruta_completa):
        print(f"❌ Archivo no encontrado: {ruta_completa}")
        return None
        
    try:
        with open(ruta_completa, "r", encoding="utf-8") as archivo:
            query = archivo.read()
            
        cliente = obtener_cliente_bigquery()
        print(f"🔍 Ejecutando en BigQuery: {nombre_archivo_sql}...")
        
        # El método to_dataframe() convierte la respuesta directamente a Pandas de forma nativa
        df = cliente.query(query).to_dataframe()
        return df
        
    except Exception as e:
        print(f"❌ Error al ejecutar {nombre_archivo_sql}: {str(e)}")
        return None

def cargar_todas_las_consultas():
    """
    Ejecuta todo el portafolio analítico y devuelve un diccionario 
    con los DataFrames listos para la capa de KPIs.
    """
    archivos_analiticos = {
        "ventas_comercial": "01_rendimiento_comercial.sql",
        "inventario_movimientos": "02_conciliacion_inventario.sql",
        "roi_marketing": "03_roi_marketing.sql",
        "top_clientes": "04_top_clientes.sql",
        "ventas_marketing": "05_ventas_vs_marketing.sql",
        "rentabilidad_margen": "06_rentabilidad_margen.sql",
        "demografia_canales": "07_comportamiento_demografico.sql"
    }
    
    dataframes_proyecto = {}
    
    print("🚀 Iniciando extracción de datos analíticos desde el Data Warehouse...")
    for clave, archivo in archivos_analiticos.items():
        df = ejecutar_consulta_sql(archivo)
        if df is not None:
            dataframes_proyecto[clave] = df
            print(f"✅ {archivo} cargado exitosamente. Formato: {df.shape}")
            
    return dataframes_proyecto

if __name__ == "__main__":
    # Prueba de integración local de la capa de extracción
    dfs = cargar_todas_las_consultas()
    if dfs:
        print("\n🏁 Extracción completada. DataFrames disponibles para la capa de KPIs.")