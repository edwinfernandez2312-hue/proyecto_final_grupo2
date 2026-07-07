import os
import re
import sqlite3
import pandas as pd
from google.cloud import bigquery
from dotenv import load_dotenv
from config import DW_PATH

# Cargar el entorno para asegurar el uso de las credenciales
load_dotenv()

ID_PROYECTO = os.getenv("ID_PROYECTO")
DATASET_ID = "proyectofinalG2"

def obtener_cliente_bigquery():
    """Inicializa y devuelve el cliente nativo de BigQuery."""
    if not ID_PROYECTO:
        raise ValueError("❌ Error: La variable ID_PROYECTO no está configurada en el archivo .env")
    return bigquery.Client(project=ID_PROYECTO)

def resolver_safe_divide(sql):
    """
    Parsea y reemplaza SAFE_DIVIDE(A, B) por su equivalente en SQLite: ((A) * 1.0 / NULLIF(B, 0))
    Maneja correctamente paréntesis anidados.
    """
    while "SAFE_DIVIDE(" in sql:
        idx = sql.find("SAFE_DIVIDE(")
        start = idx + len("SAFE_DIVIDE(")
        
        nivel = 1
        coma_idx = -1
        end_idx = -1
        
        for i in range(start, len(sql)):
            if sql[i] == '(':
                nivel += 1
            elif sql[i] == ')':
                nivel -= 1
                if nivel == 0:
                    end_idx = i
                    break
            elif sql[i] == ',' and nivel == 1:
                coma_idx = i
                
        if coma_idx != -1 and end_idx != -1:
            arg1 = sql[start:coma_idx].strip()
            arg2 = sql[coma_idx+1:end_idx].strip()
            reemplazo = f"(({arg1}) * 1.0 / NULLIF({arg2}, 0))"
            sql = sql[:idx] + reemplazo + sql[end_idx+1:]
        else:
            break
    return sql

def ejecutar_consulta_sql(nombre_archivo_sql):
    """
    Lee un archivo SQL desde la carpeta de analytics.
    Intenta ejecutarlo en BigQuery adaptando el ID del proyecto,
    y si falla o no está configurado, realiza fallback a SQLite local.
    """
    ruta_base = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../sql"))
    ruta_completa = os.path.join(ruta_base, nombre_archivo_sql)
    
    if not os.path.exists(ruta_completa):
        print(f"❌ Archivo no encontrado: {ruta_completa}")
        return None
        
    try:
        with open(ruta_completa, "r", encoding="utf-8") as archivo:
            query_raw = archivo.read()
            
        # Si ID_PROYECTO está disponible, intentamos BigQuery
        if ID_PROYECTO:
            try:
                cliente = obtener_cliente_bigquery()
                # Reemplazar proyecto y dataset en la query por los reales
                query_bq = re.sub(
                    r'`proyectofinalg2\.proyectofinalG2\.(\w+)`',
                    f'`{ID_PROYECTO}.{DATASET_ID}.\\1`',
                    query_raw
                )
                print(f"🔍 Ejecutando en BigQuery: {nombre_archivo_sql}...")
                df = cliente.query(query_bq).to_dataframe()
                print(f"✅ Query {nombre_archivo_sql} ejecutada en BigQuery. Filas: {len(df)}")
                return df
            except Exception as bq_err:
                print(f"⚠️ BigQuery falló ({bq_err}). Intentando fallback local a SQLite...")
        else:
            print(f"ℹ️ ID_PROYECTO no configurado. Usando SQLite local para: {nombre_archivo_sql}")
            
        # Fallback a SQLite
        query_sqlite = re.sub(
            r'`proyectofinalg2\.proyectofinalG2\.(\w+)`',
            r'`\1`',
            query_raw
        )
        
        # Reemplazar SAFE_DIVIDE por su equivalente compatible con SQLite
        query_sqlite = resolver_safe_divide(query_sqlite)
        
        if not os.path.exists(DW_PATH):
            print(f"❌ Base de datos SQLite local no encontrada en: {DW_PATH}")
            return None
            
        with sqlite3.connect(DW_PATH) as conn:
            df = pd.read_sql_query(query_sqlite, conn)
            print(f"✅ Query {nombre_archivo_sql} ejecutada en SQLite local. Filas: {len(df)}")
            return df
            
    except Exception as e:
        print(f"❌ Error crítico al ejecutar {nombre_archivo_sql}: {str(e)}")
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