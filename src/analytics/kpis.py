import os
import pandas as pd
import numpy as np
from analytics.consultas import cargar_todas_las_consultas

def generar_kpis_comerciales(df_ventas_mes):
    """
    Calcula variaciones porcentuales mes a mes (MoM) de ingresos 
    e inversión utilizando funciones de ventana de Pandas.
    """
    if df_ventas_mes is None or df_ventas_mes.empty:
        return None
        
    df = df_ventas_mes.copy()
    
    # Invertir el orden para calcular el cambio hacia adelante (cronológico)
    df = df.iloc[::-1].reset_index(drop=True)
    
    # 1. Crecimiento de Ingresos Mes a Mes (MoM)
    df['crecimiento_ingresos_pct'] = df['ingresos_totales'].pct_change() * 100
    
    # 2. ROAS (Return on Ad Spend) = Ingresos / Inversión de Marketing
    df['roas'] = np.where(
        df['inversion_total'] > 0, 
        df['ingresos_totales'] / df['inversion_total'], 
        0
    )
    
    # 3. Ratio de Eficiencia de Costo de Marketing (Qué % del ingreso se va en marketing)
    df['esfuerzo_marketing_pct'] = np.where(
        df['ingresos_totales'] > 0,
        (df['inversion_total'] / df['ingresos_totales']) * 100,
        0
    )
    
    return df

def generar_kpis_rentabilidad(df_rentabilidad):
    """
    Calcula la contribución marginal de cada producto al negocio
    y añade banderas de rendimiento financiero.
    """
    if df_rentabilidad is None or df_rentabilidad.empty:
        return None
        
    df = df_rentabilidad.copy()
    
    # 1. Ticket promedio por producto (Ingresos brutos / volumen)
    df['precio_promedio_venta'] = df['ingresos_brutos'] / df['volumen_vendido']
    
    # 2. Impacto de descuentos (Qué porcentaje del ingreso bruto representó el descuento)
    df['impacto_descuento_pct'] = (df['dinero_cedido_en_descuentos'] / (df['ingresos_brutos'] + df['dinero_cedido_en_descuentos'])) * 100
    
    # 3. Clasificación ABC de productos basada en la ganancia neta
    df = df.sort_values(by='ganancia_neta', ascending=False).reset_index(drop=True)
    df['contribucion_acumulada_pct'] = df['ganancia_neta'].cumsum() / df['ganancia_neta'].sum() * 100
    
    df['categoria_rentabilidad'] = pd.cut(
        df['contribucion_acumulada_pct'],
        bins=[0, 70, 90, 100],
        labels=['Clase A (Alta)', 'Clase B (Media)', 'Clase C (Baja)'],
        include_lowest=True
    )
    
    return df

def generar_kpis_inventario(df_inventario):
    """
    Determina la salud del inventario cruzando las existencias 
    con el flujo histórico de movimientos.
    """
    if df_inventario is None or df_inventario.empty:
        return None
        
    df = df_inventario.copy()
    
    # 1. Ratio de Rotación del Stock disponible frente a las salidas
    df['ratio_salida_stock'] = np.where(
        df['stock_actual'] > 0,
        df['unidades_retiradas'] / df['stock_actual'],
        df['unidades_retiradas'] # Si el stock es 0, el riesgo es directo
    )
    
    # 2. Variable booleana de riesgo logístico severo
    df['requiere_reabastecimiento_urgente'] = (df['stock_actual'] == 0) & (df['unidades_retiradas'] > 0)
    
    return df

def calcular_resumen_ejecutivo(dict_dfs):
    """
    Consolida las métricas macro del negocio en un solo diccionario 
    ideal para tarjetas de KPI principales (KPI Cards).
    """
    resumen = {}
    
    # KPIs globales (ventas totales, ticket, descuentos, etc.)
    if 'kpis_globales' in dict_dfs:
        df_kg = dict_dfs['kpis_globales']
        if df_kg is not None and not df_kg.empty:
            row = df_kg.iloc[0]
            resumen['ventas_totales'] = float(row.get('ventas_totales', 0))
            resumen['ticket_promedio'] = float(row.get('ticket_promedio', 0))
            resumen['productos_vendidos'] = int(row.get('productos_vendidos', 0))
            resumen['numero_ventas'] = int(row.get('numero_ventas', 0))
            resumen['descuentos_otorgados'] = float(row.get('descuentos_otorgados', 0))
            resumen['descuento_promedio'] = float(row.get('descuento_promedio', 0))
            resumen['venta_maxima'] = float(row.get('venta_maxima', 0))
            resumen['venta_minima'] = float(row.get('venta_minima', 0))

    # KPIs de Ventas y Marketing
    if 'ventas_marketing' in dict_dfs:
        df_vm = generar_kpis_comerciales(dict_dfs['ventas_marketing'])
        if df_vm is not None and not df_vm.empty:
            ultimo_mes = df_vm.iloc[-1]
            resumen['ingresos_totales_mes'] = float(ultimo_mes['ingresos_totales'])
            resumen['roas_actual'] = float(ultimo_mes['roas'])
            resumen['crecimiento_mom_pct'] = float(ultimo_mes.get('crecimiento_ingresos_pct', 0.0) or 0.0)
            resumen['esfuerzo_marketing_pct'] = float(ultimo_mes.get('esfuerzo_marketing_pct', 0.0) or 0.0)

    # KPIs de Rentabilidad Global
    if 'rentabilidad_margen' in dict_dfs:
        df_rm = dict_dfs['rentabilidad_margen']
        resumen['ganancia_neta_total'] = float(df_rm['ganancia_neta'].sum())
        resumen['margen_promedio_global_pct'] = float(df_rm['margen_rentabilidad_pct'].mean())
        
    # KPIs de Operaciones
    if 'inventario_movimientos' in dict_dfs:
        df_im = dict_dfs['inventario_movimientos']
        resumen['productos_agotados'] = int((df_im['stock_actual'] == 0).sum())

    if 'ventas_por_canal' in dict_dfs:
        df_vc = dict_dfs['ventas_por_canal']
        if df_vc is not None and not df_vc.empty:
            top = df_vc.iloc[0]
            resumen['canal_lider'] = str(top['canal_venta'])
            resumen['canal_lider_participacion_pct'] = float(top.get('participacion_pct', 0))

    if 'ventas_por_sucursal' in dict_dfs:
        df_vs = dict_dfs['ventas_por_sucursal']
        if df_vs is not None and not df_vs.empty:
            resumen['sucursal_lider'] = str(df_vs.iloc[0]['nombre_sucursal'])

    if 'ventas_por_producto' in dict_dfs:
        df_vp = dict_dfs['ventas_por_producto']
        if df_vp is not None and not df_vp.empty:
            resumen['producto_top'] = str(df_vp.iloc[0]['nombre_producto'])
            resumen['categoria_top'] = str(df_vp.iloc[0]['categoria'])

    if 'ventas_demografia' in dict_dfs:
        df_vd = dict_dfs['ventas_demografia']
        if df_vd is not None and not df_vd.empty:
            resumen['segmento_top'] = str(df_vd.iloc[0]['segmento_cliente'])
            resumen['departamento_top'] = str(df_vd.iloc[0]['departamento'])

    # --- KPIs de Clientes y Demografía ---
    if 'top_clientes' in dict_dfs:
        df_tc = dict_dfs['top_clientes']
        if not df_tc.empty:
            # Extraemos el nombre del cliente #1
            resumen['cliente_top_1'] = str(df_tc.iloc[0]['nombre_cliente'])
            
    if 'demografia_canales' in dict_dfs:
        df_dc = dict_dfs['demografia_canales']
        if not df_dc.empty:
            # Agrupamos para descubrir cuál es el canal que más dinero genera
            mejor_canal = df_dc.groupby('canal_venta')['ingresos_generados'].sum().idxmax()
            resumen['canal_estrella'] = str(mejor_canal)
            
            # Método de pago favorito
            mejor_pago = df_dc.groupby('metodo_pago')['cantidad_pedidos'].sum().idxmax()
            resumen['metodo_pago_favorito'] = str(mejor_pago)
            
    return resumen

def procesar_toda_la_analitica():
    """
    Orquesta el flujo analítico completo: extrae de BigQuery
    y transforma con las reglas de negocio de Pandas.
    """
    # 1. Extraer datos limpios desde consultas.py
    dfs_crudos = cargar_todas_las_consultas()
    
    if not dfs_crudos:
        print("❌ No se pudieron extraer los DataFrames base.")
        return None, None
        
    # 2. Diccionario contenedor de DataFrames con KPIs integrados
    dfs_transformados = {}
    
    print("\n🧠 Calculando capas de KPIs y métricas de negocio con Pandas...")
    
    dfs_transformados['ventas_marketing_kpi'] = generar_kpis_comerciales(dfs_crudos.get('ventas_marketing'))
    dfs_transformados['rentabilidad_kpi'] = generar_kpis_rentabilidad(dfs_crudos.get('rentabilidad_margen'))
    dfs_transformados['inventario_kpi'] = generar_kpis_inventario(dfs_crudos.get('inventario_movimientos'))
    
    # Mantener los que no requieren cálculos complejos pero sirven para reportes directos
    dfs_transformados['ventas_comercial'] = dfs_crudos.get('ventas_comercial')
    dfs_transformados['top_clientes'] = dfs_crudos.get('top_clientes')
    dfs_transformados['roi_marketing'] = dfs_crudos.get('roi_marketing')
    dfs_transformados['demografia_canales'] = dfs_crudos.get('demografia_canales')
    dfs_transformados['kpis_globales'] = dfs_crudos.get('kpis_globales')
    dfs_transformados['ventas_por_canal'] = dfs_crudos.get('ventas_por_canal')
    dfs_transformados['ventas_por_sucursal'] = dfs_crudos.get('ventas_por_sucursal')
    dfs_transformados['ventas_por_producto'] = dfs_crudos.get('ventas_por_producto')
    dfs_transformados['ventas_diarias'] = dfs_crudos.get('ventas_diarias')
    dfs_transformados['ventas_demografia'] = dfs_crudos.get('ventas_demografia')
    
    # 3. Calcular métricas clave consolidadas
    resumen = calcular_resumen_ejecutivo(dfs_crudos)
    
    print("✅ Transformación analítica finalizada.")
    return dfs_transformados, resumen

if __name__ == "__main__":
    # Ejecución de la capa analítica completa
    tablas_kpi, KPI_cards = procesar_toda_la_analitica()
    
    # 1. BLOQUE GERENCIAL: Tarjetas de Métricas Macro
    if KPI_cards:
        print("\n📊 ========================================================")
        print("   TARJETAS DE KPI PRINCIPALES (RESUMEN EJECUTIVO)")
        print("============================================================")
        for kpi, valor in KPI_cards.items():
            if isinstance(valor, float):
                print(f"🔹 {kpi:<30}: {valor:,.2f}")
            else:
                print(f"🔹 {kpi:<30}: {valor}")

    # 2. BLOQUE COMERCIAL: Clientes y Demografía
    print("\n👥 ========================================================")
    print("   ANÁLISIS DE CLIENTES Y COMPORTAMIENTO")
    print("============================================================")
    if 'top_clientes' in tablas_kpi and not tablas_kpi['top_clientes'].empty:
        print("\n🏆 [Top 5 Clientes Estrella]")
        print(tablas_kpi['top_clientes'].head(5).to_string(index=False))
        
    if 'demografia_canales' in tablas_kpi and not tablas_kpi['demografia_canales'].empty:
        print("\n🗺️ [Top 5 Segmentos Demográficos por Ingreso]")
        columnas_demo = ['departamento', 'genero', 'segmento_cliente', 'canal_venta', 'ingresos_generados']
        # Filtramos columnas para que no se desborde la terminal
        df_demo_mostrar = tablas_kpi['demografia_canales'][[col for col in columnas_demo if col in tablas_kpi['demografia_canales'].columns]]
        print(df_demo_mostrar.head(5).to_string(index=False))

    # 3. BLOQUE OPERATIVO: Rentabilidad e Inventario
    print("\n⚙️ ========================================================")
    print("   ANÁLISIS DE OPERACIONES Y RENTABILIDAD")
    print("============================================================")
    if 'rentabilidad_kpi' in tablas_kpi and not tablas_kpi['rentabilidad_kpi'].empty:
        print("\n💰 [Top 3 Productos más Rentables]")
        columnas_rent = ['nombre_producto', 'volumen_vendido', 'ganancia_neta', 'categoria_rentabilidad']
        print(tablas_kpi['rentabilidad_kpi'][columnas_rent].head(3).to_string(index=False))

    if 'inventario_kpi' in tablas_kpi and not tablas_kpi['inventario_kpi'].empty:
        df_inv = tablas_kpi['inventario_kpi']
        alertas = df_inv[df_inv['requiere_reabastecimiento_urgente'] == True]
        print(f"\n📦 [Alertas de Inventario]: {len(alertas)} productos requieren reabastecimiento urgente.")
        if not alertas.empty:
            print(alertas[['nombre_producto', 'stock_actual', 'unidades_retiradas']].head(3).to_string(index=False))
            
    print("\n============================================================\n")