# src/pipeline_manager.py
from extract.extraer_productos_excel import extraer_productos_excel
from extract.extraer_ventas_csv_ import extraer_ventas_csv
from extract.extraer_clientes_json import extraer_clientes_json
from extract.extraer_inventario_db import extraer_inventario_db
from extract.extraer_marketing_api import extraer_marketing_api

from transform.transformar_clientes_json import transformar_clientes_json
from transform.transformar_productos_excel import transformar_productos_excel
from transform.transformar_ventas_csv import transformar_ventas_csv
from transform.transformar_inventario_db import transformar_inventario_db
from transform.transformar_marketing_api import transformar_marketing_api

from load.construir_dimensiones import construir_todas_las_dimensiones
from load.construir_hechos import construir_todas_las_tablas_hecho
from load.cargar_dw import cargar_data_warehouse

# 1. Importamos la función de BigQuery aquí arriba para mantener el orden limpio
# Nota: Mantenemos el nombre de tu archivo 'cargar_bigquerry' tal como lo definiste
from load.cargar_bigquerry import migrar_sqlite_a_bigquery 


def run_etl_pipeline():
    print("🚀 Iniciando Pipeline ETL - Proyecto Final\n")

    # --- Día 2: Extracción ---
    print("--- 1. Extracción de datos ---")
    df_prod = extraer_productos_excel()
    df_ventas = extraer_ventas_csv()
    df_cli = extraer_clientes_json()
    df_inv_actual, df_mov = extraer_inventario_db()
    df_mkt = extraer_marketing_api()

    # --- Día 2: Transformación (Limpieza) ---
    print("\n--- 2. Transformación (Limpieza y estandarización) ---")
    df_cli_limpio = transformar_clientes_json(df_cli)
    df_prod_limpio = transformar_productos_excel(df_prod)
    df_inv_limpio, df_mov_limpio = transformar_inventario_db(df_inv_actual, df_mov)
    df_ventas_limpio = transformar_ventas_csv(df_ventas)
    df_mkt_limpio = transformar_marketing_api(df_mkt)

    # --- Día 3: Modelo dimensional ---
    print("\n--- 3. Construcción del modelo dimensional ---")
    dimensiones = construir_todas_las_dimensiones(
        df_cli_limpio,
        df_prod_limpio,
        df_ventas_limpio,
        df_inv_limpio,
        df_mov_limpio,
        df_mkt_limpio,
    )

    hechos = construir_todas_las_tablas_hecho(
        df_ventas_limpio,
        df_inv_limpio,
        df_mov_limpio,
        df_mkt_limpio,
        dimensiones,
    )

    # --- Día 3: Carga al Data Warehouse Local ---
    print("\n--- 4. Carga al Data Warehouse Local (SQLite) ---")
    cargar_data_warehouse(dimensiones, hechos)
    print("✅ Base de datos SQLite local generada y actualizada.")

    # --- Carga al Data Warehouse en la Nube (BigQuery) ---
    print("\n--- 5. Sincronización de datos con Google BigQuery ---")
    
    # 2. Invocamos aquí la función que sube todo a la nube de manera secuencial
    migrar_sqlite_a_bigquery()

    # 3. Bloque de verificación final en consola para confirmar el éxito de todo el flujo
    print("\n==================================================================")
    print("🎉 ¡EL PIPELINE DE DATOS SE CUMPLIÓ COMPLETAMENTE CON ÉXITO! 🎉")
    print("   -> Fase 1, 2 y 3: Extracción, Limpieza y Modelo Dimensional [OK]")
    print("   -> Fase 4: Almacenamiento local SQLite Completado           [OK]")
    print("   -> Fase 5: Carga Limpia en BigQuery (Sin Duplicados)        [OK]")
    print("==================================================================")

if __name__ == "__main__":
    run_etl_pipeline()