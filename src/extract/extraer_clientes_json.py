import pandas as pd

from config import CLIENTES_JSON


def extraer_clientes_json():
  try:
    clientes_df = pd.read_json(CLIENTES_JSON)

    print("Clientes extraídos correctamente. Total de registros:", len(clientes_df))
    print("\n--- Primeros 3 registros de Clientes ---")
    print(clientes_df.head(3))
    print("----------------------------------------\n")

    return clientes_df
  except Exception as e:
    print(f"Error al extraer el archivo JSON de clientes: {e}")
    return None
