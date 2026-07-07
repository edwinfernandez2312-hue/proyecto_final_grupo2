import pandas as pd


def _crear_mapa(df, natural_col, key_col):
    """
    Crea un diccionario para buscar claves rápidamente.
    Reemplaza los _lookup fila por fila, que son muy lentos con datos masivos.
    """
    if df is None or natural_col not in df.columns or key_col not in df.columns:
        return {}

    tmp = df[[natural_col, key_col]].dropna().drop_duplicates(subset=[natural_col])
    return tmp.set_index(natural_col)[key_col].to_dict()


def _crear_fecha_key(serie):
    fechas = pd.to_datetime(serie, errors="coerce", format="mixed")
    return pd.to_numeric(fechas.dt.strftime("%Y%m%d"), errors="coerce")


def construir_fact_ventas(df_ventas, dimensiones):
    fact = df_ventas.copy()

    dim_cliente = dimensiones["dim_cliente"]
    dim_producto = dimensiones["dim_producto"]
    dim_sucursal = dimensiones["dim_sucursal"]
    dim_canal = dimensiones["dim_canal"]
    dim_metodo = dimensiones["dim_metodo_pago"]

    mapa_cliente = _crear_mapa(dim_cliente, "cliente_id_natural", "cliente_key")
    mapa_producto = _crear_mapa(dim_producto, "producto_id_natural", "producto_key")
    mapa_sucursal = _crear_mapa(dim_sucursal, "sucursal_id_natural", "sucursal_key")
    mapa_canal = _crear_mapa(dim_canal, "canal_venta", "canal_key")
    mapa_metodo = _crear_mapa(dim_metodo, "metodo_pago", "metodo_pago_key")

    fact["fecha_key"] = _crear_fecha_key(fact["fecha_venta"])

    fact["cliente_id"] = pd.to_numeric(fact["cliente_id"], errors="coerce")
    fact["producto_id"] = pd.to_numeric(fact["producto_id"], errors="coerce")
    fact["sucursal_id"] = pd.to_numeric(fact["sucursal_id"], errors="coerce")

    fact["cliente_key"] = fact["cliente_id"].map(mapa_cliente)
    fact["producto_key"] = fact["producto_id"].map(mapa_producto)
    fact["sucursal_key"] = fact["sucursal_id"].map(mapa_sucursal)
    fact["canal_key"] = fact["canal_venta"].map(mapa_canal)
    fact["metodo_pago_key"] = fact["metodo_pago"].map(mapa_metodo)

    for col in ["venta_id", "cantidad"]:
        if col in fact.columns:
            fact[col] = pd.to_numeric(fact[col], errors="coerce")

    for col in ["precio_unitario", "descuento", "total_venta"]:
        if col in fact.columns:
            fact[col] = pd.to_numeric(fact[col], errors="coerce").fillna(0)

    columnas_obligatorias = [
        "venta_id",
        "fecha_key",
        "cliente_key",
        "producto_key",
        "sucursal_key",
        "canal_key",
        "metodo_pago_key",
        "cantidad",
    ]

    fact = fact.dropna(subset=[c for c in columnas_obligatorias if c in fact.columns])

    columnas_enteras = [
        "venta_id",
        "fecha_key",
        "cliente_key",
        "producto_key",
        "sucursal_key",
        "canal_key",
        "metodo_pago_key",
        "cantidad",
    ]

    for col in columnas_enteras:
        if col in fact.columns:
            fact[col] = fact[col].astype("int64")

    columnas_finales = [
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

    resultado = fact[[c for c in columnas_finales if c in fact.columns]].copy()
    print(f"   - fact_ventas generada: {len(resultado)} registros")
    return resultado


def construir_fact_inventario(df_inventario, dimensiones):
    fact = df_inventario.copy()

    dim_producto = dimensiones["dim_producto"]
    dim_bodega = dimensiones["dim_bodega"]

    mapa_producto = _crear_mapa(dim_producto, "producto_id_natural", "producto_key")
    mapa_bodega = _crear_mapa(dim_bodega, "nombre_bodega", "bodega_key")

    fact["producto_id"] = pd.to_numeric(fact["producto_id"], errors="coerce")
    fact["producto_key"] = fact["producto_id"].map(mapa_producto)
    fact["bodega_key"] = fact["bodega"].map(mapa_bodega)

    fact["existencia"] = pd.to_numeric(fact["existencia"], errors="coerce").fillna(0)

    fact = fact.dropna(subset=["producto_key", "bodega_key"])

    for col in ["producto_key", "bodega_key", "existencia"]:
        fact[col] = fact[col].astype("int64")

    resultado = fact[["producto_key", "bodega_key", "existencia"]].copy()
    print(f"   - fact_inventario generada: {len(resultado)} registros")
    return resultado


def construir_fact_movimientos_inventario(df_movimientos, dimensiones):
    fact = df_movimientos.copy()

    dim_producto = dimensiones["dim_producto"]

    mapa_producto = _crear_mapa(dim_producto, "producto_id_natural", "producto_key")

    fact["fecha_key"] = _crear_fecha_key(fact["fecha"])
    fact["producto_id"] = pd.to_numeric(fact["producto_id"], errors="coerce")
    fact["producto_key"] = fact["producto_id"].map(mapa_producto)

    if "id" in fact.columns:
        fact["movimiento_id"] = pd.to_numeric(fact["id"], errors="coerce")
    elif "movimiento_id" in fact.columns:
        fact["movimiento_id"] = pd.to_numeric(fact["movimiento_id"], errors="coerce")

    fact["cantidad"] = pd.to_numeric(fact["cantidad"], errors="coerce")

    fact = fact.dropna(subset=["movimiento_id", "fecha_key", "producto_key", "cantidad"])

    for col in ["movimiento_id", "fecha_key", "producto_key", "cantidad"]:
        fact[col] = fact[col].astype("int64")

    columnas_finales = [
        "movimiento_id",
        "fecha_key",
        "producto_key",
        "tipo",
        "cantidad",
    ]

    resultado = fact[[c for c in columnas_finales if c in fact.columns]].copy()

    if "tipo" in resultado.columns:
        resultado = resultado.rename(columns={"tipo": "tipo_movimiento"})

    print(f"   - fact_movimientos_inventario generada: {len(resultado)} registros")
    return resultado


def construir_fact_marketing(df_marketing, dimensiones):
    if df_marketing is None or df_marketing.empty:
        return pd.DataFrame(columns=[
            "campana_key",
            "fecha_key",
            "impresiones",
            "clics",
            "costo",
            "leads",
            "conversiones",
        ])
    fact = df_marketing.copy()

    dim_campana = dimensiones["dim_campana"]

    mapa_campana = _crear_mapa(dim_campana, "campana_id_natural", "campana_key")

    fact["fecha_key"] = _crear_fecha_key(fact["fecha"])
    fact["campana_id"] = pd.to_numeric(fact["campana_id"], errors="coerce")
    fact["campana_key"] = fact["campana_id"].map(mapa_campana)

    for col in ["impresiones", "clics", "leads", "conversiones"]:
        if col in fact.columns:
            fact[col] = pd.to_numeric(fact[col], errors="coerce").fillna(0)

    fact["costo"] = pd.to_numeric(fact["costo"], errors="coerce").fillna(0)

    fact = fact.dropna(subset=["campana_key", "fecha_key"])

    for col in ["campana_key", "fecha_key", "impresiones", "clics", "leads", "conversiones"]:
        if col in fact.columns:
            fact[col] = fact[col].astype("int64")

    columnas_finales = [
        "campana_key",
        "fecha_key",
        "impresiones",
        "clics",
        "costo",
        "leads",
        "conversiones",
    ]

    resultado = fact[[c for c in columnas_finales if c in fact.columns]].copy()
    print(f"   - fact_marketing generada: {len(resultado)} registros")
    return resultado


def construir_todas_las_tablas_hecho(
    df_ventas,
    df_inventario,
    df_movimientos,
    df_marketing,
    dimensiones
):
    print("⚙️ Construyendo tablas de hechos en modo rápido...")

    hechos = {
        "fact_ventas": construir_fact_ventas(df_ventas, dimensiones),
        "fact_inventario": construir_fact_inventario(df_inventario, dimensiones),
        "fact_movimientos_inventario": construir_fact_movimientos_inventario(
            df_movimientos,
            dimensiones
        ),
        "fact_marketing": construir_fact_marketing(df_marketing, dimensiones),
    }

    print("✅ Tablas de hechos construidas:")
    for nombre, df in hechos.items():
        print(f"   - {nombre}: {len(df)} registros")

    return hechos
