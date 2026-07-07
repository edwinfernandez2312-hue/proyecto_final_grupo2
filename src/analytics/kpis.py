import os
import pandas as pd
import numpy as np
from analytics.consultas import cargar_todas_las_consultas


def generar_kpis_comerciales(df_ventas_mes):
    """
    Calcula variaciones porcentuales mes a mes (MoM), ROAS y esfuerzo de marketing.
    Corrección para dataset masivo:
    - ordena por anio y mes, no por nombre_mes;
    - evita nan en crecimiento;
    - convierte columnas numéricas de forma segura.
    """
    if df_ventas_mes is None or df_ventas_mes.empty:
        return None

    df = df_ventas_mes.copy()

    # Asegurar columnas numéricas
    for col in ["anio", "mes", "ingresos_totales", "inversion_total", "conversiones_marketing"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Orden cronológico real
    if "anio" in df.columns and "mes" in df.columns:
        df = df.sort_values(["anio", "mes"]).reset_index(drop=True)
    else:
        df = df.reset_index(drop=True)

    df["ingresos_totales"] = pd.to_numeric(df["ingresos_totales"], errors="coerce").fillna(0)
    df["inversion_total"] = pd.to_numeric(df["inversion_total"], errors="coerce").fillna(0)

    # Crecimiento de ingresos Mes a Mes
    df["crecimiento_ingresos_pct"] = df["ingresos_totales"].pct_change() * 100
    df["crecimiento_ingresos_pct"] = df["crecimiento_ingresos_pct"].replace([np.inf, -np.inf], np.nan)

    # ROAS = Ingresos / Inversión de Marketing
    df["roas"] = np.where(
        df["inversion_total"] > 0,
        df["ingresos_totales"] / df["inversion_total"],
        0
    )

    # % del ingreso que se va en marketing
    df["esfuerzo_marketing_pct"] = np.where(
        df["ingresos_totales"] > 0,
        (df["inversion_total"] / df["ingresos_totales"]) * 100,
        0
    )

    return df


def generar_kpis_rentabilidad(df_rentabilidad):
    if df_rentabilidad is None or df_rentabilidad.empty:
        return None

    df = df_rentabilidad.copy()

    for col in [
        "ingresos_brutos",
        "volumen_vendido",
        "dinero_cedido_en_descuentos",
        "ganancia_neta",
        "margen_rentabilidad_pct",
    ]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["precio_promedio_venta"] = np.where(
        df["volumen_vendido"] > 0,
        df["ingresos_brutos"] / df["volumen_vendido"],
        0
    )

    df["impacto_descuento_pct"] = np.where(
        (df["ingresos_brutos"] + df["dinero_cedido_en_descuentos"]) > 0,
        (df["dinero_cedido_en_descuentos"] / (df["ingresos_brutos"] + df["dinero_cedido_en_descuentos"])) * 100,
        0
    )

    df = df.sort_values(by="ganancia_neta", ascending=False).reset_index(drop=True)

    total_ganancia = df["ganancia_neta"].sum()
    if total_ganancia != 0:
        df["contribucion_acumulada_pct"] = df["ganancia_neta"].cumsum() / total_ganancia * 100
    else:
        df["contribucion_acumulada_pct"] = 0

    df["categoria_rentabilidad"] = pd.cut(
        df["contribucion_acumulada_pct"],
        bins=[0, 70, 90, 100],
        labels=["Clase A (Alta)", "Clase B (Media)", "Clase C (Baja)"],
        include_lowest=True
    )

    return df


def generar_kpis_inventario(df_inventario):
    if df_inventario is None or df_inventario.empty:
        return None

    df = df_inventario.copy()

    df["stock_actual"] = pd.to_numeric(df["stock_actual"], errors="coerce").fillna(0)
    df["unidades_retiradas"] = pd.to_numeric(df["unidades_retiradas"], errors="coerce").fillna(0)

    df["ratio_salida_stock"] = np.where(
        df["stock_actual"] > 0,
        df["unidades_retiradas"] / df["stock_actual"],
        df["unidades_retiradas"]
    )

    df["requiere_reabastecimiento_urgente"] = (
        (df["stock_actual"] == 0) & (df["unidades_retiradas"] > 0)
    )

    return df


def _valor_float_seguro(valor, default=0.0):
    try:
        if pd.isna(valor) or np.isinf(valor):
            return default
        return float(valor)
    except Exception:
        return default


def calcular_resumen_ejecutivo(dict_dfs):
    resumen = {}

    # KPIs de Ventas y Marketing
    if "ventas_marketing" in dict_dfs:
        df_vm = generar_kpis_comerciales(dict_dfs["ventas_marketing"])
        if df_vm is not None and not df_vm.empty:

            # Elegimos el último mes con ingresos reales.
            # Así evitamos que un mes con marketing pero ventas 0 deje el KPI principal en 0.
            df_con_ingresos = df_vm[df_vm["ingresos_totales"] > 0].copy()

            if not df_con_ingresos.empty:
                ultimo_mes = df_con_ingresos.iloc[-1]
            else:
                ultimo_mes = df_vm.iloc[-1]

            resumen["ingresos_totales_mes"] = _valor_float_seguro(ultimo_mes.get("ingresos_totales", 0))
            resumen["roas_actual"] = _valor_float_seguro(ultimo_mes.get("roas", 0))
            resumen["crecimiento_mom_pct"] = _valor_float_seguro(
                ultimo_mes.get("crecimiento_ingresos_pct", 0),
                default=0.0
            )

    # KPIs de Rentabilidad Global
    if "rentabilidad_margen" in dict_dfs:
        df_rm = dict_dfs["rentabilidad_margen"].copy()
        df_rm["ganancia_neta"] = pd.to_numeric(df_rm["ganancia_neta"], errors="coerce").fillna(0)
        df_rm["margen_rentabilidad_pct"] = pd.to_numeric(df_rm["margen_rentabilidad_pct"], errors="coerce")
        resumen["ganancia_neta_total"] = float(df_rm["ganancia_neta"].sum())
        resumen["margen_promedio_global_pct"] = _valor_float_seguro(df_rm["margen_rentabilidad_pct"].mean())

    # KPIs de Operaciones
    if "inventario_movimientos" in dict_dfs:
        df_im = dict_dfs["inventario_movimientos"].copy()
        df_im["stock_actual"] = pd.to_numeric(df_im["stock_actual"], errors="coerce").fillna(0)
        resumen["productos_agotados"] = int((df_im["stock_actual"] == 0).sum())

    # KPIs de Clientes
    if "top_clientes" in dict_dfs:
        df_tc = dict_dfs["top_clientes"].copy()
        if "nombre_cliente" in df_tc.columns:
            df_tc = df_tc[df_tc["nombre_cliente"] != "Cliente no registrado"]
        if not df_tc.empty:
            resumen["cliente_top_1"] = str(df_tc.iloc[0]["nombre_cliente"])

    # KPIs de Demografía
    if "demografia_canales" in dict_dfs:
        df_dc = dict_dfs["demografia_canales"].copy()
        if not df_dc.empty:
            df_dc["ingresos_generados"] = pd.to_numeric(df_dc["ingresos_generados"], errors="coerce").fillna(0)
            df_dc["cantidad_pedidos"] = pd.to_numeric(df_dc["cantidad_pedidos"], errors="coerce").fillna(0)

            mejor_canal = df_dc.groupby("canal_venta")["ingresos_generados"].sum().idxmax()
            resumen["canal_estrella"] = str(mejor_canal)

            mejor_pago = df_dc.groupby("metodo_pago")["cantidad_pedidos"].sum().idxmax()
            resumen["metodo_pago_favorito"] = str(mejor_pago)

    return resumen


def procesar_toda_la_analitica():
    dfs_crudos = cargar_todas_las_consultas()

    if not dfs_crudos:
        print("❌ No se pudieron extraer los DataFrames base.")
        return None, None

    dfs_transformados = {}

    print("\n🧠 Calculando capas de KPIs y métricas de negocio con Pandas...")

    dfs_transformados["ventas_marketing_kpi"] = generar_kpis_comerciales(dfs_crudos.get("ventas_marketing"))
    dfs_transformados["rentabilidad_kpi"] = generar_kpis_rentabilidad(dfs_crudos.get("rentabilidad_margen"))
    dfs_transformados["inventario_kpi"] = generar_kpis_inventario(dfs_crudos.get("inventario_movimientos"))

    dfs_transformados["ventas_comercial"] = dfs_crudos.get("ventas_comercial")
    dfs_transformados["top_clientes"] = dfs_crudos.get("top_clientes")
    dfs_transformados["roi_marketing"] = dfs_crudos.get("roi_marketing")
    dfs_transformados["demografia_canales"] = dfs_crudos.get("demografia_canales")

    resumen = calcular_resumen_ejecutivo(dfs_crudos)

    print("✅ Transformación analítica finalizada.")
    return dfs_transformados, resumen


if __name__ == "__main__":
    tablas_kpi, KPI_cards = procesar_toda_la_analitica()

    if KPI_cards:
        print("\n📊 ========================================================")
        print("   TARJETAS DE KPI PRINCIPALES (RESUMEN EJECUTIVO)")
        print("============================================================")
        for kpi, valor in KPI_cards.items():
            if isinstance(valor, float):
                print(f"🔹 {kpi:<30}: {valor:,.2f}")
            else:
                print(f"🔹 {kpi:<30}: {valor}")
