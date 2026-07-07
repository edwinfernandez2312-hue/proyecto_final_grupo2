import os
import re
import sqlite3

import pandas as pd
from dotenv import load_dotenv

from config import DW_PATH

load_dotenv()

ID_PROYECTO = os.getenv("ID_PROYECTO")

ARCHIVOS_ANALITICOS = {
  "ventas_comercial": "01_rendimiento_comercial.sql",
  "inventario_movimientos": "02_conciliacion_inventario.sql",
  "roi_marketing": "03_roi_marketing.sql",
  "top_clientes": "04_top_clientes.sql",
  "ventas_marketing": "05_ventas_vs_marketing.sql",
  "rentabilidad_margen": "06_rentabilidad_margen.sql",
  "demografia_canales": "07_comportamiento_demografico.sql",
  "kpis_globales": "08_kpis_globales.sql",
  "ventas_por_canal": "09_ventas_por_canal.sql",
  "ventas_por_sucursal": "10_ventas_por_sucursal.sql",
  "ventas_por_producto": "11_ventas_por_producto.sql",
  "ventas_diarias": "12_ventas_diarias.sql",
  "ventas_demografia": "13_ventas_demografia.sql",
}


def _ruta_sql(nombre_archivo):
  return os.path.join(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../sql")),
    nombre_archivo,
  )


def _adaptar_sql_para_sqlite(query):
  query = re.sub(r"`[^`]+\.[^`]+\.([^`]+)`", r"\1", query)
  query = re.sub(
    r"SAFE_DIVIDE\(([^,]+),\s*([^)]+)\)",
    r"CASE WHEN (\2) != 0 THEN (\1) / (\2) ELSE NULL END",
    query,
  )
  return query


def _obtener_cliente_bigquery():
  from google.cloud import bigquery

  if not ID_PROYECTO:
    raise ValueError("ID_PROYECTO no configurado en .env")
  return bigquery.Client(project=ID_PROYECTO)


def ejecutar_consulta_sqlite(nombre_archivo_sql):
  ruta = _ruta_sql(nombre_archivo_sql)
  if not os.path.exists(ruta):
    print(f"❌ Archivo no encontrado: {ruta}")
    return None

  if not DW_PATH.exists():
    print(f"❌ Data Warehouse local no encontrado: {DW_PATH}")
    return None

  try:
    with open(ruta, "r", encoding="utf-8") as archivo:
      query = _adaptar_sql_para_sqlite(archivo.read())

    with sqlite3.connect(DW_PATH) as conn:
      return pd.read_sql_query(query, conn)
  except Exception as e:
    print(f"❌ Error SQLite en {nombre_archivo_sql}: {e}")
    return None


def ejecutar_consulta_bigquery(nombre_archivo_sql):
  ruta = _ruta_sql(nombre_archivo_sql)
  if not os.path.exists(ruta):
    print(f"❌ Archivo no encontrado: {ruta}")
    return None

  try:
    with open(ruta, "r", encoding="utf-8") as archivo:
      query = archivo.read()

    cliente = _obtener_cliente_bigquery()
    print(f"🔍 Ejecutando en BigQuery: {nombre_archivo_sql}...")
    return cliente.query(query).to_dataframe()
  except Exception as e:
    print(f"❌ Error BigQuery en {nombre_archivo_sql}: {e}")
    return None


def ejecutar_consulta_sql(nombre_archivo_sql, preferir_sqlite=True):
  if preferir_sqlite and DW_PATH.exists():
    df = ejecutar_consulta_sqlite(nombre_archivo_sql)
    if df is not None:
      return df

  if ID_PROYECTO:
    return ejecutar_consulta_bigquery(nombre_archivo_sql)

  return None


def cargar_todas_las_consultas(preferir_sqlite=True):
  dataframes_proyecto = {}
  fuente = "SQLite local (datos frescos del ETL)" if preferir_sqlite and DW_PATH.exists() else "BigQuery"

  print(f"🚀 Extrayendo datos analíticos desde {fuente}...")

  for clave, archivo in ARCHIVOS_ANALITICOS.items():
    df = ejecutar_consulta_sql(archivo, preferir_sqlite=preferir_sqlite)
    if df is not None:
      dataframes_proyecto[clave] = df
      print(f"✅ {archivo} cargado. Formato: {df.shape}")

  return dataframes_proyecto


if __name__ == "__main__":
  dfs = cargar_todas_las_consultas()
  if dfs:
    print("\n🏁 Extracción completada. DataFrames listos para KPIs.")
