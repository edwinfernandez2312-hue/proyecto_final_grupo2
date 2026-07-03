import pandas as pd


def transformar_productos_excel(df_productos):
  try:
    df = df_productos.drop_duplicates(subset=["producto_id"], keep="last").copy()

    df["costo_unitario"] = pd.to_numeric(df["costo_unitario"], errors="coerce")
    df["precio_lista"] = pd.to_numeric(df["precio_lista"], errors="coerce")

    for col in df.select_dtypes(include="object").columns:
      df[col] = df[col].astype(str).str.strip().replace("", "No disponible")
      df[col] = df[col].fillna("No disponible")

    for col in df.select_dtypes(include="number").columns:
      df[col] = df[col].fillna(0)

    print("✅ Limpieza de Productos completada.")
    print("\n--- Primeros 3 registros de Productos (Limpios) ---")
    print(df.head(3))
    print("---------------------------------------------------\n")

    return df
  except Exception as e:
    print(f"Error al limpiar productos: {e}")
    return None
