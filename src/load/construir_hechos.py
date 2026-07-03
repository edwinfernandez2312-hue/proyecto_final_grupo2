import pandas as pd


def _lookup(df, natural_col, key_col, value):
  match = df.loc[df[natural_col] == value, key_col]
  return int(match.iloc[0]) if not match.empty else None


def construir_fact_ventas(df_ventas, dimensiones):
  dim_cliente = dimensiones["dim_cliente"]
  dim_producto = dimensiones["dim_producto"]
  dim_tiempo = dimensiones["dim_tiempo"]
  dim_sucursal = dimensiones["dim_sucursal"]
  dim_canal = dimensiones["dim_canal"]
  dim_metodo = dimensiones["dim_metodo_pago"]

  registros = []
  for _, row in df_ventas.iterrows():
    cliente_key = _lookup(
      dim_cliente, "cliente_id_natural", "cliente_key", int(row["cliente_id"])
    )
    if cliente_key is None:
      continue

    registros.append(
      {
        "venta_id": int(row["venta_id"]),
        "fecha_key": _lookup(
          dim_tiempo, "fecha", "fecha_key", row["fecha_venta"]
        ),
        "cliente_key": cliente_key,
        "producto_key": _lookup(
          dim_producto, "producto_id_natural", "producto_key", int(row["producto_id"])
        ),
        "sucursal_key": _lookup(
          dim_sucursal, "sucursal_id_natural", "sucursal_key", int(row["sucursal_id"])
        ),
        "canal_key": _lookup(dim_canal, "canal_venta", "canal_key", row["canal_venta"]),
        "metodo_pago_key": _lookup(
          dim_metodo, "metodo_pago", "metodo_pago_key", row["metodo_pago"]
        ),
        "cantidad": int(row["cantidad"]),
        "precio_unitario": float(row["precio_unitario"]),
        "descuento": float(row["descuento"]),
        "total_venta": float(row["total_venta"]),
      }
    )

  return pd.DataFrame(registros)


def construir_fact_inventario(df_inventario, dimensiones):
  dim_producto = dimensiones["dim_producto"]
  dim_bodega = dimensiones["dim_bodega"]

  registros = []
  for _, row in df_inventario.iterrows():
    registros.append(
      {
        "producto_key": _lookup(
          dim_producto, "producto_id_natural", "producto_key", int(row["producto_id"])
        ),
        "bodega_key": _lookup(
          dim_bodega, "nombre_bodega", "bodega_key", row["bodega"]
        ),
        "existencia": int(row["existencia"]),
      }
    )

  return pd.DataFrame(registros)


def construir_fact_movimientos_inventario(df_movimientos, dimensiones):
  dim_producto = dimensiones["dim_producto"]
  dim_tiempo = dimensiones["dim_tiempo"]

  registros = []
  for _, row in df_movimientos.iterrows():
    registros.append(
      {
        "movimiento_id": int(row["id"]),
        "fecha_key": _lookup(dim_tiempo, "fecha", "fecha_key", row["fecha"]),
        "producto_key": _lookup(
          dim_producto, "producto_id_natural", "producto_key", int(row["producto_id"])
        ),
        "tipo_movimiento": row["tipo"],
        "cantidad": int(row["cantidad"]),
      }
    )

  return pd.DataFrame(registros)


def construir_fact_marketing(df_marketing, dimensiones):
  dim_tiempo = dimensiones["dim_tiempo"]
  dim_campana = dimensiones["dim_campana"]

  registros = []
  for _, row in df_marketing.iterrows():
    registros.append(
      {
        "campana_key": _lookup(
          dim_campana, "campana_id_natural", "campana_key", int(row["campana_id"])
        ),
        "fecha_key": _lookup(dim_tiempo, "fecha", "fecha_key", row["fecha"]),
        "impresiones": int(row["impresiones"]),
        "clics": int(row["clics"]),
        "costo": float(row["costo"]),
        "leads": int(row["leads"]),
        "conversiones": int(row["conversiones"]),
      }
    )

  return pd.DataFrame(registros)


def construir_todas_las_tablas_hecho(df_ventas, df_inventario, df_movimientos, df_marketing, dimensiones):
  hechos = {
    "fact_ventas": construir_fact_ventas(df_ventas, dimensiones),
    "fact_inventario": construir_fact_inventario(df_inventario, dimensiones),
    "fact_movimientos_inventario": construir_fact_movimientos_inventario(
      df_movimientos, dimensiones
    ),
    "fact_marketing": construir_fact_marketing(df_marketing, dimensiones),
  }

  print("✅ Tablas de hechos construidas:")
  for nombre, df in hechos.items():
    print(f"   - {nombre}: {len(df)} registros")

  return hechos
