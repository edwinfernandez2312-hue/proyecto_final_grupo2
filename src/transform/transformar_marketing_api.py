import pandas as pd


def transformar_marketing_api(df_marketing):
  try:
    df = df_marketing.copy()
    df = df.rename(
      columns={
        "campaña_id": "campana_id",
        "campa\u00f1a_id": "campana_id",
      }
    )

    if "campana_id" not in df.columns:
      campana_col = [c for c in df.columns if "campana" in c.lower() or "campa" in c.lower()]
      if campana_col:
        df = df.rename(columns={campana_col[0]: "campana_id"})

    df = df.drop_duplicates(subset=["campana_id"], keep="last").copy()
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce").dt.strftime("%Y-%m-%d")
    df["plataforma"] = df["plataforma"].astype(str).str.strip().str.title()

    for col in ["impresiones", "clics", "leads", "conversiones"]:
      df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    df["costo"] = pd.to_numeric(df["costo"], errors="coerce").fillna(0.0)

    print("✅ Limpieza de Marketing completada.")
    print("\n--- Registros de Marketing (Limpios) ---")
    print(df)
    print("---------------------------------------\n")

    return df
  except Exception as e:
    print(f"Error al limpiar marketing: {e}")
    return None
