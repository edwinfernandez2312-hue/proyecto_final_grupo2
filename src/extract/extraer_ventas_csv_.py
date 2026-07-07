import pandas as pd

from config import VENTAS_CSV

def extraer_ventas_csv():
  try:
    ventas_df = pd.read_csv(
      VENTAS_CSV,
      dtype={
        "venta_id": "Int64",
        "cliente_id": "Int64",
        "producto_id": "Int64",
        "sucursal_id": "Int64",
      },
      low_memory=False,
    )

    print(f"Ventas extraídas correctamente. Total de registros: {len(ventas_df):,}")
    print("\n--- Primeros 3 registros de Ventas ---")
    print(ventas_df.head(3))
    print("--------------------------------------\n")

    return ventas_df
  except Exception as e:
    print(f"Error al extraer el archivo CSV de ventas: {e}")
    return None
