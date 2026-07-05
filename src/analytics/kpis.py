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
    
    # KPIs de Ventas y Marketing (Tomando el mes más reciente disponible)
    if 'ventas_marketing' in dict_dfs:
        df_vm = generar_kpis_comerciales(dict_dfs['ventas_marketing'])
        if df_vm is not None and not df_vm.empty:
            ultimo_mes = df_vm.iloc[-1]
            resumen['ingresos_totales_mes'] = float(ultimo_mes['ingresos_totales'])
            resumen['roas_actual'] = float(ultimo_mes['roas'])
            resumen['crecimiento_mom_pct'] = float(ultimo_mes['crecimiento_ingresos_pct'])

    # KPIs de Rentabilidad Global
    if 'rentabilidad_margen' in dict_dfs:
        df_rm = dict_dfs['rentabilidad_margen']
        resumen['ganancia_neta_total'] = float(df_rm['ganancia_neta'].sum())
        resumen['margen_promedio_global_pct'] = float(df_rm['margen_rentabilidad_pct'].mean())
        
    # KPIs de Operaciones
    if 'inventario_movimientos' in dict_dfs:
        df_im = dict_dfs['inventario_movimientos']
        resumen['productos_agotados'] = int((df_im['stock_actual'] == 0).sum())
        
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
    
    # 3. Calcular métricas clave consolidadas
    resumen = calcular_resumen_ejecutivo(dfs_crudos)
    
    print("✅ Transformación analítica finalizada.")
    return dfs_transformados, resumen

if __name__ == "__main__":
    # Ejecución de la capa analítica completa
    tablas_kpi, KPI_cards = procesar_toda_la_analitica()
    
    # --- BLOQUE DE VERIFICACIÓN VISUAL DE DATAFRAMES ---
    if tablas_kpi:
        print("\n👀 ========================================================")
        print("🔍 MUESTRA ANALÍTICA (1ª FILA DE CADA DATAFRAME CALCULADO)")
        print("============================================================")
        for nombre, df in tablas_kpi.items():
            print(f"\n📈 [DataFrame: {nombre}] - Dimensiones totales: {df.shape if df is not None else 'Vacío'}")
            if df is not None and not df.empty:
                # Mostramos la primera fila formateada sin índices numéricos de Pandas
                print(df.head(1).to_string(index=False))
            else:
                print("⚠️ No hay datos disponibles para esta tabla.")
        print("\n============================================================\n")
        
    # --- BLOQUE DE TARJETAS DE MÉTRICAS MACRO ---
    if KPI_cards:
        print("📊 --- TARJETAS DE KPI PRINCIPALES (RESUMEN EJECUTIVO) ---")
        for kpi, valor in KPI_cards.items():
            if isinstance(valor, float):
                print(f"🔹 {kpi:<30}: {valor:,.2f}")
            else:
                print(f"🔹 {kpi:<30}: {valor}")