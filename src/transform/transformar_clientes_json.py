import pandas as pd


def transformar_clientes_json(df_clientes):
  try:
    df = df_clientes.drop_duplicates(subset=["cliente_id"], keep="last").copy()

    df["municipio"] = df["municipio"].replace("", "No disponible").fillna("No disponible")
    df["fecha_registro"] = pd.to_datetime(
      df["fecha_registro"], errors="coerce"
    ).dt.strftime("%Y-%m-%d")

    for col in df.select_dtypes(include="object").columns:
      df[col] = df[col].fillna("No disponible")

    df["edad"] = pd.to_numeric(df["edad"], errors="coerce").fillna(0).astype(int)

    print("✅ Limpieza de Clientes completada.")
    print("\n--- Primeros 3 registros de Clientes (Limpios) ---")
    print(df.head(3))
    print("--------------------------------------------------\n")

    return df
  except Exception as e:
    print(f"Error al limpiar clientes: {e}")
    return None
