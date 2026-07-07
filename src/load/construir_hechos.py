import pandas as pd

from transform.normalizacion import normalizar_fecha_iso


def _merge_key(df, dim, left_col, dim_natural_col, key_col):
  merged = df.merge(
    dim[[dim_natural_col, key_col]],
    left_on=left_col,
    right_on=dim_natural_col,
    how="left",
  )
  return merged[key_col]


def construir_fact_ventas(df_ventas, dimensiones):
  dim_cliente = dimensiones["dim_cliente"]
  dim_producto = dimensiones["dim_producto"]
  dim_tiempo = dimensiones["dim_tiempo"]
  dim_sucursal = dimensiones["dim_sucursal"]
  dim_canal = dimensiones["dim_canal"]
  dim_metodo = dimensiones["dim_metodo_pago"]

  df = df_ventas.copy()
  df["fecha_venta"] = normalizar_fecha_iso(df["fecha_venta"])
  dim_fechas = dim_tiempo[["fecha", "fecha_key"]].copy()
  dim_fechas["fecha"] = normalizar_fecha_iso(dim_fechas["fecha"])
  df["cliente_id"] = df["cliente_id"].astype(int)
  df["producto_id"] = df["producto_id"].astype(int)
  df["sucursal_id"] = df["sucursal_id"].astype(int)
  df["venta_id"] = df["venta_id"].astype(int)

  df = df.merge(
    dim_cliente[["cliente_id_natural", "cliente_key"]],
    left_on="cliente_id",
    right_on="cliente_id_natural",
    how="inner",
  )
  df = df.merge(
    dim_fechas,
    left_on="fecha_venta",
    right_on="fecha",
    how="left",
  )
  df = df.merge(
    dim_producto[["producto_id_natural", "producto_key"]],
    left_on="producto_id",
    right_on="producto_id_natural",
    how="left",
  )
  df = df.merge(
    dim_sucursal[["sucursal_id_natural", "sucursal_key"]],
    left_on="sucursal_id",
    right_on="sucursal_id_natural",
    how="left",
  )
  df = df.merge(
    dim_canal[["canal_venta", "canal_key"]],
    on="canal_venta",
    how="left",
  )
  df = df.merge(
    dim_metodo[["metodo_pago", "metodo_pago_key"]],
    on="metodo_pago",
    how="left",
  )

  df = df.dropna(
    subset=[
      "fecha_key",
      "producto_key",
      "sucursal_key",
      "canal_key",
      "metodo_pago_key",
    ]
  )

  return df[
    [
      "venta_id",
      "fecha_key",
      "cliente_key",
      "producto_key",
      "sucursal_key",
      "canal_key",
      "metodo_pago_key",
      "cantidad",
      "precio_unitario",
      "descuento",
      "total_venta",
    ]
  ].astype(
    {
      "venta_id": int,
      "fecha_key": "Int64",
      "cliente_key": int,
      "producto_key": "Int64",
      "sucursal_key": "Int64",
      "canal_key": "Int64",
      "metodo_pago_key": "Int64",
      "cantidad": int,
      "precio_unitario": float,
      "descuento": float,
      "total_venta": float,
    }
  )


def construir_fact_inventario(df_inventario, dimensiones):
  dim_producto = dimensiones["dim_producto"]
  dim_bodega = dimensiones["dim_bodega"]

  df = df_inventario.copy()
  df["producto_id"] = df["producto_id"].astype(int)

  df = df.merge(
    dim_producto[["producto_id_natural", "producto_key"]],
    left_on="producto_id",
    right_on="producto_id_natural",
    how="left",
  )
  df = df.merge(
    dim_bodega[["nombre_bodega", "bodega_key"]],
    left_on="bodega",
    right_on="nombre_bodega",
    how="left",
  )

  df = df.dropna(subset=["producto_key", "bodega_key"])

  return df[["producto_key", "bodega_key", "existencia"]].astype(
    {"producto_key": int, "bodega_key": int, "existencia": int}
  )


def construir_fact_movimientos_inventario(df_movimientos, dimensiones):
  dim_producto = dimensiones["dim_producto"]
  dim_tiempo = dimensiones["dim_tiempo"]

  df = df_movimientos.copy()
  df["fecha"] = normalizar_fecha_iso(df["fecha"])
  dim_fechas = dim_tiempo[["fecha", "fecha_key"]].copy()
  dim_fechas["fecha"] = normalizar_fecha_iso(dim_fechas["fecha"])
  df["producto_id"] = df["producto_id"].astype(int)
  df["id"] = df["id"].astype(int)

  df = df.merge(
    dim_fechas,
    left_on="fecha",
    right_on="fecha",
    how="left",
  )
  df = df.merge(
    dim_producto[["producto_id_natural", "producto_key"]],
    left_on="producto_id",
    right_on="producto_id_natural",
    how="left",
  )

  df = df.dropna(subset=["fecha_key", "producto_key"])

  return df.rename(columns={"id": "movimiento_id", "tipo": "tipo_movimiento"})[
    ["movimiento_id", "fecha_key", "producto_key", "tipo_movimiento", "cantidad"]
  ].astype(
    {
      "movimiento_id": int,
      "fecha_key": int,
      "producto_key": int,
      "cantidad": int,
    }
  )


def construir_fact_marketing(df_marketing, dimensiones):
  dim_tiempo = dimensiones["dim_tiempo"]
  dim_campana = dimensiones["dim_campana"]

  df = df_marketing.copy()
  df["fecha"] = normalizar_fecha_iso(df["fecha"])
  dim_fechas = dim_tiempo[["fecha", "fecha_key"]].copy()
  dim_fechas["fecha"] = normalizar_fecha_iso(dim_fechas["fecha"])
  df["campana_id"] = df["campana_id"].astype(int)

  df = df.merge(
    dim_campana[["campana_id_natural", "campana_key"]],
    left_on="campana_id",
    right_on="campana_id_natural",
    how="left",
  )
  df = df.merge(
    dim_fechas,
    left_on="fecha",
    right_on="fecha",
    how="left",
  )

  df = df.dropna(subset=["campana_key", "fecha_key"])

  return df[
    ["campana_key", "fecha_key", "impresiones", "clics", "costo", "leads", "conversiones"]
  ].astype(
    {
      "campana_key": int,
      "fecha_key": int,
      "impresiones": int,
      "clics": int,
      "costo": float,
      "leads": int,
      "conversiones": int,
    }
  )


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
    print(f"   - {nombre}: {len(df):,} registros")

  return hechos
