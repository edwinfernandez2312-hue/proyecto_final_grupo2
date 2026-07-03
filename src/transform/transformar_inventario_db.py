import pandas as pd


def transformar_inventario_db(df_inventario_actual, df_movimientos):
  try:
    inv = df_inventario_actual.drop_duplicates(
      subset=["producto_id", "bodega"], keep="last"
    ).copy()
    mov = df_movimientos.drop_duplicates(subset=["id"], keep="last").copy()

    inv["bodega"] = inv["bodega"].astype(str).str.strip().str.title()
    inv["existencia"] = pd.to_numeric(inv["existencia"], errors="coerce").fillna(0).astype(int)

    mov["fecha"] = pd.to_datetime(mov["fecha"], errors="coerce").dt.strftime("%Y-%m-%d")
    mov["tipo"] = mov["tipo"].astype(str).str.strip().str.title()
    mov["cantidad"] = pd.to_numeric(mov["cantidad"], errors="coerce").fillna(0).astype(int)
    mov = mov.dropna(subset=["fecha", "producto_id"])

    print("✅ Limpieza de Inventario completada.")
    print("\n--- Inventario actual (Limpio) ---")
    print(inv.head())
    print("\n--- Movimientos (Limpios) ---")
    print(mov.head())
    print("----------------------------------------------------\n")

    return inv, mov
  except Exception as e:
    print(f"Error al limpiar inventario: {e}")
    return None, None
