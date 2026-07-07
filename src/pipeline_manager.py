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
from load.cargar_bigquerry import migrar_sqlite_a_bigquery 
from analytics.kpis import procesar_toda_la_analitica
from analytics.generar_graficos import crear_dashboards_estaticos
import sys
sys.path.append('/opt/airflow/src')
import pandas as pd

def aplicar_parche_dataset_masivo(
    df_cli,
    df_prod,
    df_ventas,
    df_inv,
    df_mov,
    df_mkt
):
    """
    Parche rápido para dataset masivo:
    - elimina IDs vacíos
    - convierte IDs a enteros
    - limpia fechas inválidas
    - evita error: cannot convert float NaN to integer
    """

    def convertir_enteros(df, columnas, drop=True):
        if df is None:
            return df

        for col in columnas:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        if drop:
            columnas_existentes = [c for c in columnas if c in df.columns]
            if columnas_existentes:
                df = df.dropna(subset=columnas_existentes)

        for col in columnas:
            if col in df.columns:
                df[col] = df[col].astype("int64")

        return df

    def convertir_numericos(df, columnas, fill_value=None):
        if df is None:
            return df

        for col in columnas:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
                if fill_value is not None:
                    df[col] = df[col].fillna(fill_value)

        return df

    # =========================
    # CLIENTES
    # =========================
    if df_cli is not None:
        df_cli = df_cli.copy()

        if "cliente_id" in df_cli.columns:
            df_cli["cliente_id"] = pd.to_numeric(df_cli["cliente_id"], errors="coerce")
            df_cli = df_cli.dropna(subset=["cliente_id"])
            df_cli["cliente_id"] = df_cli["cliente_id"].astype("int64")
            df_cli = df_cli.drop_duplicates(subset=["cliente_id"])

        if "edad" in df_cli.columns:
            df_cli["edad"] = pd.to_numeric(df_cli["edad"], errors="coerce")
            df_cli["edad"] = df_cli["edad"].fillna(0).astype("int64")

    # =========================
    # PRODUCTOS
    # =========================
    if df_prod is not None:
        df_prod = df_prod.copy()

        if "producto_id" in df_prod.columns:
            df_prod["producto_id"] = pd.to_numeric(df_prod["producto_id"], errors="coerce")
            df_prod = df_prod.dropna(subset=["producto_id"])
            df_prod["producto_id"] = df_prod["producto_id"].astype("int64")
            df_prod = df_prod.drop_duplicates(subset=["producto_id"])

        for col in ["precio", "costo", "precio_unitario"]:
            if col in df_prod.columns:
                df_prod[col] = pd.to_numeric(df_prod[col], errors="coerce").fillna(0)

    # =========================
    # VENTAS
    # =========================
    if df_ventas is not None:
        df_ventas = df_ventas.copy()

        if "fecha_venta" in df_ventas.columns:
            df_ventas["fecha_venta"] = pd.to_datetime(
                df_ventas["fecha_venta"],
                errors="coerce",
                format="mixed"
            )

        ids_ventas = [
            "venta_id",
            "cliente_id",
            "producto_id",
            "sucursal_id",
            "canal_id",
            "bodega_id",
            "cantidad"
        ]

        for col in ids_ventas:
            if col in df_ventas.columns:
                df_ventas[col] = pd.to_numeric(df_ventas[col], errors="coerce")

        columnas_criticas = [
            c for c in ["venta_id", "fecha_venta", "cliente_id", "producto_id", "cantidad"]
            if c in df_ventas.columns
        ]

        df_ventas = df_ventas.dropna(subset=columnas_criticas)

        if "venta_id" in df_ventas.columns:
            df_ventas = df_ventas.drop_duplicates(subset=["venta_id"])

        for col in ids_ventas:
            if col in df_ventas.columns:
                df_ventas[col] = df_ventas[col].astype("int64")

        for col in ["precio_unitario", "descuento", "total_venta"]:
            if col in df_ventas.columns:
                df_ventas[col] = pd.to_numeric(df_ventas[col], errors="coerce").fillna(0)

    # =========================
    # INVENTARIO ACTUAL
    # =========================
    if df_inv is not None:
        df_inv = df_inv.copy()

        if "producto_id" in df_inv.columns:
            df_inv["producto_id"] = pd.to_numeric(df_inv["producto_id"], errors="coerce")
            df_inv = df_inv.dropna(subset=["producto_id"])
            df_inv["producto_id"] = df_inv["producto_id"].astype("int64")

        for col in ["existencia", "stock", "stock_actual"]:
            if col in df_inv.columns:
                df_inv[col] = pd.to_numeric(df_inv[col], errors="coerce").fillna(0).astype("int64")

    # =========================
    # MOVIMIENTOS INVENTARIO
    # =========================
    if df_mov is not None:
        df_mov = df_mov.copy()

        for fecha_col in ["fecha_movimiento", "fecha"]:
            if fecha_col in df_mov.columns:
                df_mov[fecha_col] = pd.to_datetime(
                    df_mov[fecha_col],
                    errors="coerce",
                    format="mixed"
                )

        ids_mov = [
            "movimiento_id",
            "producto_id",
            "bodega_id",
            "cantidad"
        ]

        for col in ids_mov:
            if col in df_mov.columns:
                df_mov[col] = pd.to_numeric(df_mov[col], errors="coerce")

        columnas_criticas_mov = [
            c for c in ["producto_id", "cantidad"]
            if c in df_mov.columns
        ]

        if columnas_criticas_mov:
            df_mov = df_mov.dropna(subset=columnas_criticas_mov)

        for col in ids_mov:
            if col in df_mov.columns:
                df_mov[col] = df_mov[col].astype("int64")

    # =========================
    # MARKETING
    # =========================
    if df_mkt is not None:
        df_mkt = df_mkt.copy()

        if "campaña_id" in df_mkt.columns and "campana_id" not in df_mkt.columns:
            df_mkt = df_mkt.rename(columns={"campaña_id": "campana_id"})

        if "fecha" in df_mkt.columns:
            df_mkt["fecha"] = pd.to_datetime(
                df_mkt["fecha"],
                errors="coerce",
                format="mixed"
            )

        if "campana_id" in df_mkt.columns:
            df_mkt["campana_id"] = pd.to_numeric(df_mkt["campana_id"], errors="coerce")
            df_mkt = df_mkt.dropna(subset=["campana_id"])
            df_mkt["campana_id"] = df_mkt["campana_id"].astype("int64")

        for col in ["impresiones", "clics", "leads", "conversiones"]:
            if col in df_mkt.columns:
                df_mkt[col] = pd.to_numeric(df_mkt[col], errors="coerce").fillna(0).astype("int64")

        if "costo" in df_mkt.columns:
            df_mkt["costo"] = pd.to_numeric(df_mkt["costo"], errors="coerce").fillna(0)
            df_mkt.loc[df_mkt["costo"] < 0, "costo"] = 0

        if "campana_id" in df_mkt.columns:
            df_mkt = df_mkt.drop_duplicates(subset=["campana_id"])

    print("\n✅ Parche de limpieza para dataset masivo aplicado.")
    print(f"   - ventas limpias: {len(df_ventas) if df_ventas is not None else 0}")
    print(f"   - clientes limpios: {len(df_cli) if df_cli is not None else 0}")
    print(f"   - productos limpios: {len(df_prod) if df_prod is not None else 0}")
    print(f"   - inventario limpio: {len(df_inv) if df_inv is not None else 0}")
    print(f"   - movimientos limpios: {len(df_mov) if df_mov is not None else 0}")
    print(f"   - marketing limpio: {len(df_mkt) if df_mkt is not None else 0}")

    return df_cli, df_prod, df_ventas, df_inv, df_mov, df_mkt


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

    # --- PARCHE DATASET MASIVO ---
    df_cli_limpio, df_prod_limpio, df_ventas_limpio, df_inv_limpio, df_mov_limpio, df_mkt_limpio = aplicar_parche_dataset_masivo(
        df_cli_limpio,
        df_prod_limpio,
        df_ventas_limpio,
        df_inv_limpio,
        df_mov_limpio,
        df_mkt_limpio
    )

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
    migrar_sqlite_a_bigquery()

    # --- Fase 6: Consultas Analíticas y KPIs ---
    print("\n--- 6. Cálculo de Consultas Analíticas y KPIs ---")
    # 2. INVOCAMOS TU FUNCIÓN AQUÍ
    tablas_kpi, KPI_cards = procesar_toda_la_analitica()
    
    # Imprimimos las tarjetas macro si se generaron correctamente
    if KPI_cards:
        print("\n📊 --- TARJETAS DE KPI PRINCIPALES (RESUMEN EJECUTIVO) ---")
        for kpi, valor in KPI_cards.items():
            if isinstance(valor, float):
                print(f"🔹 {kpi:<30}: {valor:,.2f}")
            else:
                print(f"🔹 {kpi:<30}: {valor}")

    # --- NUEVA FASE 7: Generación de Visualizaciones ---
    print("\n--- 7. Generación de Visualizaciones ---")
    if tablas_kpi:
        # Aquí le pasas el diccionario de DataFrames que obtuviste en la Fase 6
        crear_dashboards_estaticos(tablas_kpi)

    # 3. Bloque de verificación final
    print("\n==================================================================")
    print("🎉 ¡EL PIPELINE DE DATOS SE CUMPLIÓ COMPLETAMENTE CON ÉXITO! 🎉")
    print("   -> Fase 1-5: Proceso ETL y Carga BigQuery        [OK]")
    print("   -> Fase 6: Cálculo de KPIs                       [OK]")
    print("   -> Fase 7: Gráficos exportados en PNG            [OK]")
    print("==================================================================")

if __name__ == "__main__":
    run_etl_pipeline()