import json

import pandas as pd

from config import MARKETING_JSON


def extraer_marketing_api():
  """Simula extracción desde API REST leyendo la respuesta guardada en JSON."""
  try:
    with open(MARKETING_JSON, encoding="utf-8") as f:
      payload = json.load(f)

    marketing_df = pd.json_normalize(payload, record_path="campaigns")

    print("Marketing extraído correctamente. Total de registros:", len(marketing_df))
    print("\n--- Primeros registros de Marketing ---")
    print(marketing_df.head())
    print("---------------------------------------\n")

    return marketing_df
  except Exception as e:
    print(f"Error al extraer datos de marketing: {e}")
    return None
