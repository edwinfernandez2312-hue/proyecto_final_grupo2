# src/pipeline_manager.py
# Imports de Extracción
from extract.extraer_productos_excel import extraer_productos_excel
from extract.extraer_ventas_csv_ import extraer_ventas_csv
from extract.extraer_clientes_json import extraer_clientes_json
from extract.extraer_inventario_db import extraer_inventario_db 

# Imports de Transformación (Limpieza Pura)
from transform.transformar_clientes_json import transformar_clientes_json
from transform.transformar_productos_excel import transformar_productos_excel
from transform.transformar_ventas_csv import transformar_ventas_csv
from transform.transformar_inventario_db import transformar_inventario_db

def run_etl_pipeline():
    print("🚀 Iniciando Pipeline ETL...\n")

    # --- 1. Extracción ---
    print("--- 1. Extracción de datos ---")
    df_prod = extraer_productos_excel()
    df_ventas = extraer_ventas_csv()
    df_cli = extraer_clientes_json()
    df_inv = extraer_inventario_db()
    
    # --- 2. Transformación (Limpieza) ---
    print("\n--- 2. Transformación (Limpieza) ---")
    df_cli_limpio = transformar_clientes_json(df_cli)
    df_prod_limpio = transformar_productos_excel(df_prod)
    df_inv_limpio = transformar_inventario_db(df_inv)
    df_ventas_limpio = transformar_ventas_csv(df_ventas)
    
    # --- 3. Dimensiones (Aquí integrarás tus futuras funciones) ---
    print("\n--- 3. Construcción de Dimensiones y Hechos (PENDIENTE) ---")
    # Ejemplo: df_dim_clientes = construir_dim_clientes(df_cli_limpio)
    
    print("\n✅ Pipeline ejecutado exitosamente.")