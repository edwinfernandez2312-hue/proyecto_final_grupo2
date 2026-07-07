import pandas as pd

from transform.normalizacion import normalizar_fecha_iso

SUCURSALES = {
  1: "Sucursal Centro",
  2: "Sucursal Norte",
  3: "Sucursal Sur",
}


def _fechas_unicas(*dataframes):
  fechas = set()
  for df, col in dataframes:
    if df is not None and col in df.columns:
      parsed = pd.to_datetime(df[col], errors="coerce")
      fechas.update(parsed.dropna().dt.strftime("%Y-%m-%d").tolist())
  return sorted(fechas)


def construir_dim_tiempo(df_ventas, df_movimientos, df_marketing):
  fechas = _fechas_unicas(
    (df_ventas, "fecha_venta"),
    (df_movimientos, "fecha"),
    (df_marketing, "fecha"),
  )

  registros = []
  for fecha in fechas:
    dt = pd.to_datetime(fecha, errors="coerce")
    registros.append(
      {
        "fecha_key": int(dt.strftime("%Y%m%d")),
        "fecha": dt.strftime("%Y-%m-%d"),
        "anio": dt.year,
        "mes": dt.month,
        "dia": dt.day,
        "trimestre": (dt.month - 1) // 3 + 1,
        "nombre_mes": dt.strftime("%B"),
        "dia_semana": dt.strftime("%A"),
      }
    )

  return pd.DataFrame(registros).assign(
    fecha=lambda df: normalizar_fecha_iso(df["fecha"])
  )


def construir_dim_cliente(df_clientes, df_ventas=None):
  dim = df_clientes.copy()
  dim = dim.rename(columns={"cliente_id": "cliente_id_natural"})

  if df_ventas is not None:
    clientes_ventas = set(df_ventas["cliente_id"].astype(int).unique())
    clientes_dim = set(dim["cliente_id_natural"].astype(int).unique())
    faltantes = clientes_ventas - clientes_dim

    if faltantes:
      orphan_df = pd.DataFrame(
        {
          "cliente_id_natural": sorted(faltantes),
          "nombre": "Cliente no registrado",
          "genero": "No disponible",
          "edad": 0,
          "departamento": "No disponible",
          "municipio": "No disponible",
          "fecha_registro": None,
          "segmento_cliente": "No disponible",
        }
      )
      dim = pd.concat([dim, orphan_df], ignore_index=True)

  dim.insert(0, "cliente_key", range(1, len(dim) + 1))
  return dim


def construir_dim_producto(df_productos):
  dim = df_productos.copy()
  dim = dim.rename(columns={"producto_id": "producto_id_natural"})
  dim.insert(0, "producto_key", range(1, len(dim) + 1))
  return dim


def construir_dim_sucursal(df_ventas):
  sucursales = sorted(df_ventas["sucursal_id"].dropna().unique())
  registros = [
    {
      "sucursal_key": idx,
      "sucursal_id_natural": int(suc_id),
      "nombre_sucursal": SUCURSALES.get(int(suc_id), f"Sucursal {int(suc_id)}"),
    }
    for idx, suc_id in enumerate(sucursales, start=1)
  ]
  return pd.DataFrame(registros)


def construir_dim_canal(df_ventas):
  canales = sorted(df_ventas["canal_venta"].dropna().unique())
  registros = [
    {"canal_key": idx, "canal_venta": canal}
    for idx, canal in enumerate(canales, start=1)
  ]
  return pd.DataFrame(registros)


def construir_dim_bodega(df_inventario):
  bodegas = sorted(df_inventario["bodega"].dropna().unique())
  registros = [
    {"bodega_key": idx, "nombre_bodega": bodega}
    for idx, bodega in enumerate(bodegas, start=1)
  ]
  return pd.DataFrame(registros)


def construir_dim_metodo_pago(df_ventas):
  metodos = sorted(df_ventas["metodo_pago"].dropna().unique())
  registros = [
    {"metodo_pago_key": idx, "metodo_pago": metodo}
    for idx, metodo in enumerate(metodos, start=1)
  ]
  return pd.DataFrame(registros)


def construir_dim_campana(df_marketing):
  dim = df_marketing[["campana_id", "plataforma"]].copy()
  dim = dim.rename(columns={"campana_id": "campana_id_natural"})
  dim.insert(0, "campana_key", range(1, len(dim) + 1))
  return dim


def construir_todas_las_dimensiones(
  df_clientes,
  df_productos,
  df_ventas,
  df_inventario,
  df_movimientos,
  df_marketing,
):
  dimensiones = {
    "dim_tiempo": construir_dim_tiempo(df_ventas, df_movimientos, df_marketing),
    "dim_cliente": construir_dim_cliente(df_clientes, df_ventas),
    "dim_producto": construir_dim_producto(df_productos),
    "dim_sucursal": construir_dim_sucursal(df_ventas),
    "dim_canal": construir_dim_canal(df_ventas),
    "dim_bodega": construir_dim_bodega(df_inventario),
    "dim_metodo_pago": construir_dim_metodo_pago(df_ventas),
    "dim_campana": construir_dim_campana(df_marketing),
  }

  print("✅ Dimensiones construidas:")
  for nombre, df in dimensiones.items():
    print(f"   - {nombre}: {len(df)} registros")

  return dimensiones
