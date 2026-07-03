import sqlite3

import pandas as pd

from config import INVENTARIO_DB


def extraer_inventario_db():
  try:
    with sqlite3.connect(INVENTARIO_DB) as conn:
      inventario_actual_df = pd.read_sql_query(
        "SELECT * FROM inventario_actual;", conn
      )
      movimientos_df = pd.read_sql_query(
        "SELECT * FROM movimientos_inventario;", conn
      )

    print(
      "Inventario extraído correctamente.",
      f"Existencias: {len(inventario_actual_df)},",
      f"Movimientos: {len(movimientos_df)}",
    )
    print("\n--- Inventario actual ---")
    print(inventario_actual_df.head())
    print("\n--- Movimientos ---")
    print(movimientos_df.head())
    print("------------------------------------------\n")

    return inventario_actual_df, movimientos_df
  except Exception as e:
    print(f"Error al extraer la base de datos SQLite de inventario: {e}")
    return None, None
