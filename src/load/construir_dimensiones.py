import pandas as pd

SUCURSALES = {
  1: "Sucursal Centro",
  2: "Sucursal Norte",
  3: "Sucursal Sur",
}


def _fechas_unicas(*dataframes):
  fechas = set()
  for df, col in dataframes:
    if df is not None and col in df.columns:
      fechas.update(df[col].dropna().astype(str).tolist())
  return sorted(fechas)


def construir_dim_tiempo(df_ventas, df_movimientos, df_marketing):
  fechas = _fechas_unicas(
    (df_ventas, "fecha_venta"),
    (df_movimientos, "fecha"),
    (df_marketing, "fecha"),
  )

  registros = []
  for fecha in fechas:
    dt = pd.to_datetime(fecha)
    registros.append(
      {
        "fecha_key": int(dt.strftime("%Y%m%d")),
        "fecha": fecha,
        "anio": dt.year,
        "mes": dt.month,
        "dia": dt.day,
        "trimestre": (dt.month - 1) // 3 + 1,
        "nombre_mes": dt.strftime("%B"),
        "dia_semana": dt.strftime("%A"),
      }
    )

  return pd.DataFrame(registros)


def construir_dim_cliente(df_clientes, df_ventas=None):
  if df_clientes is None or df_clientes.empty:
    dim = pd.DataFrame(columns=[
      "cliente_id_natural", "nombre", "genero", "edad",
      "departamento", "municipio", "fecha_registro", "segmento_cliente"
    ])
  else:
    dim = df_clientes.copy()
    dim = dim.rename(columns={"cliente_id": "cliente_id_natural"})

  if df_ventas is not None and not dim.empty:
    clientes_ventas = set(df_ventas["cliente_id"].dropna().astype(int).unique())
    clientes_dim = set(dim["cliente_id_natural"].dropna().astype(int).unique())
    faltantes = clientes_ventas - clientes_dim

    if faltantes:
      nuevos_clientes = [
        {
          "cliente_id_natural": cliente_id,
          "nombre": "Cliente no registrado",
          "genero": "No disponible",
          "edad": 0,
          "departamento": "No disponible",
          "municipio": "No disponible",
          "fecha_registro": None,
          "segmento_cliente": "No disponible",
        }
        for cliente_id in sorted(faltantes)
      ]
      dim = pd.concat([dim, pd.DataFrame(nuevos_clientes)], ignore_index=True)
  elif df_ventas is not None and dim.empty:
    # Si la dimension esta vacia, todos los de ventas son nuevos
    clientes_ventas = sorted(set(df_ventas["cliente_id"].dropna().astype(int).unique()))
    nuevos_clientes = [
      {
        "cliente_id_natural": cliente_id,
        "nombre": "Cliente no registrado",
        "genero": "No disponible",
        "edad": 0,
        "departamento": "No disponible",
        "municipio": "No disponible",
        "fecha_registro": None,
        "segmento_cliente": "No disponible",
      }
      for cliente_id in clientes_ventas
    ]
    dim = pd.DataFrame(nuevos_clientes)

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
  if df_marketing is None or df_marketing.empty:
    return pd.DataFrame(columns=["campana_key", "campana_id_natural", "plataforma"])
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
