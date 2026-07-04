import os
import sqlite3
import pandas as pd
from google.cloud import bigquery
from dotenv import load_dotenv

# Carga las variables del archivo .env de forma segura
load_dotenv() 

ID_PROYECTO = os.getenv("ID_PROYECTO")
DATASET_ID = "proyectofinalG2"
RUTA_DB = "../data/datacommerce_dw.db"

# 3. Lista ordenada de tus dimensiones y tablas de hechos
TABLAS_DW = [
    # Dimensiones
    "dim_tiempo",
    "dim_cliente",
    "dim_producto",
    "dim_sucursal",
    "dim_canal",
    "dim_bodega",
    "dim_metodo_pago",
    "dim_campana",
    
    # Tablas de Hechos
    "fact_ventas",
    "fact_inventario",
    "fact_movimientos_inventario",
    "fact_marketing"
]

def migrar_sqlite_a_bigquery():
    # Validar que la base de datos local exista antes de iniciar
    if not os.path.exists(RUTA_DB):
        print(f"❌ Error: No se encontró el archivo de base de datos en: {RUTA_DB}")
        return

    # Inicializar el cliente oficial de BigQuery (usa las credenciales del entorno)
    print("☁️ Inicializando cliente nativo de Google BigQuery...")
    client = bigquery.Client(project=ID_PROYECTO)

    print("🔌 Conectando a la base de datos SQLite local...")
    conexion = sqlite3.connect(RUTA_DB)
    
    for tabla in TABLAS_DW:
        print(f"\n──────────────────────────────────────────")
        print(f"📦 Procesando tabla: {tabla}")
        print(f"──────────────────────────────────────────")
        
        try:
            # 1. Extraer los datos locales con Pandas
            query = f"SELECT * FROM {tabla}"
            df = pd.read_sql_query(query, conexion)
            
            if df.empty:
                print(f"⚠️ La tabla {tabla} está vacía en SQLite. Saltando carga...")
                continue
                
            print(f"🔹 Registros locales encontrados: {len(df)}")
            
            # Formato requerido por la API nativa: proyecto.dataset.tabla
            tabla_destino = f"{ID_PROYECTO}.{DATASET_ID}.{tabla}"
            
            # Configurar las reglas de la carga nativa
            job_config = bigquery.LoadJobConfig(
                # WRITE_TRUNCATE reemplaza los datos existentes (equivalente a if_exists='replace')
                # Si prefieres acumular datos, cámbialo por "WRITE_APPEND"
                write_disposition="WRITE_TRUNCATE", 
            )
            
            # 2. Cargar a BigQuery usando el cliente de Google de forma directa
            print(f"🚀 Enviando DataFrame al motor de BigQuery...")
            job = client.load_table_from_dataframe(df, tabla_destino, job_config=job_config)
            
            # Esperar a que el proceso en la nube termine
            job.result() 
            
            print(f"✅ ¡Tabla {tabla} migrada exitosamente de manera nativa!")
            
        except Exception as e:
            print(f"❌ Error durante la migración de la tabla {tabla}:")
            print(f"   {str(e)}")

    conexion.close()
    print("\n🏁 ¡El proceso de carga nativa al Data Warehouse ha finalizado con éxito!")

if __name__ == "__main__":
    migrar_sqlite_a_bigquery()