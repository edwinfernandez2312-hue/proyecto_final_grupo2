import pandas as pd

from config import PRODUCTOS_XLSX


def extraer_productos_excel():
  try:
    productos_df = pd.read_excel(PRODUCTOS_XLSX)

    print("Productos extraídos correctamente. Total de registros:", len(productos_df))
    print("\n--- Primeros 3 registros de Productos ---")
    print(productos_df.head(3))
    print("-----------------------------------------\n")

    return productos_df
  except Exception as e:
    print(f"Error al extraer el archivo Excel de productos: {e}")
    return None
