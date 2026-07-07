import pandas as pd

from transform.normalizacion import normalizar_canal_venta, normalizar_metodo_pago, normalizar_fecha_iso


def _parsear_fechas_vectorizado(serie):
  texto = serie.astype(str).str.strip()
  texto = texto.replace({"nan": pd.NA, "None": pd.NA, "": pd.NA})

  iso = pd.to_datetime(texto, format="%Y-%m-%d", errors="coerce")
  dmy = pd.to_datetime(texto, format="%d/%m/%Y", errors="coerce")
  ymd = pd.to_datetime(texto, format="%Y/%m/%d", errors="coerce")
  dmy2 = pd.to_datetime(texto, format="%m/%d/%Y", errors="coerce")
  dmy3 = pd.to_datetime(texto, format="%d-%m-%Y", errors="coerce")

  return iso.fillna(dmy).fillna(ymd).fillna(dmy2).fillna(dmy3)


def transformar_ventas_csv(df_ventas):
  try:
    df = df_ventas.drop_duplicates(subset=["venta_id"], keep="last").copy()

    df["fecha_venta"] = normalizar_fecha_iso(_parsear_fechas_vectorizado(df["fecha_venta"]))

    df["canal_venta"] = df["canal_venta"].apply(normalizar_canal_venta)
    df["metodo_pago"] = df["metodo_pago"].apply(normalizar_metodo_pago)

    for col in ["cantidad", "precio_unitario", "descuento", "total_venta"]:
      df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["venta_id", "cliente_id", "producto_id", "fecha_venta"])

    print(f"✅ Limpieza de Ventas completada. Registros válidos: {len(df):,}")
    if len(df) <= 10:
      print("\n--- Primeros registros de Ventas (Limpias) ---")
      print(df.head(3))
      print("------------------------------------------------\n")

    return df
  except Exception as e:
    print(f"Error al limpiar ventas: {e}")
    return None
