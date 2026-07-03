import pandas as pd


def _parsear_fecha(valor):
  texto = str(valor).strip()
  if not texto or texto.lower() == "nan":
    return pd.NaT

  if "-" in texto and len(texto.split("-")[0]) == 4:
    return pd.to_datetime(texto, format="%Y-%m-%d", errors="coerce")

  if "/" in texto:
    partes = texto.split("/")
    if len(partes[0]) == 4:
      return pd.to_datetime(texto, format="%Y/%m/%d", errors="coerce")
    return pd.to_datetime(texto, format="%d/%m/%Y", errors="coerce")

  return pd.to_datetime(texto, errors="coerce")


def transformar_ventas_csv(df_ventas):
  try:
    df = df_ventas.drop_duplicates(subset=["venta_id"], keep="last").copy()

    df["fecha_venta"] = df["fecha_venta"].apply(_parsear_fecha).dt.strftime("%Y-%m-%d")

    # Estandarizar nombres de canal
    df["canal_venta"] = (
      df["canal_venta"]
      .astype(str)
      .str.strip()
      .str.title()
      .replace({"Web": "E-commerce"})
    )

    df["metodo_pago"] = df["metodo_pago"].fillna("No disponible")

    for col in ["cantidad", "precio_unitario", "descuento", "total_venta"]:
      df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["venta_id", "cliente_id", "producto_id", "fecha_venta"])

    print("✅ Limpieza de Ventas completada.")
    print("\n--- Primeros 3 registros de Ventas (Limpias) ---")
    print(df.head(3))
    print("------------------------------------------------\n")

    return df
  except Exception as e:
    print(f"Error al limpiar ventas: {e}")
    return None
