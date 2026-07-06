import os
import matplotlib.pyplot as plt
import seaborn as sns

def crear_dashboards_estaticos(tablas_kpi):
    print("\n🎨 Generando Dashboard Gerencial (Visualización de 14 KPIs)...")
    
    #
    if os.path.exists("/opt/airflow"):
        ruta_reportes = "/opt/airflow/reportes_visuales"
    else:
        ruta_reportes = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../reportes_visuales")
        )

    os.makedirs(ruta_reportes, exist_ok=True)
    sns.set_theme(style="whitegrid")
    paleta = ['#003366', '#008080', '#008B8B', '#4682B4', '#00CED1']

    # --- 1. GRÁFICO: Tendencia de Ingresos y ROAS (Ventas/Mkt) ---
    df_mkt = tablas_kpi.get('ventas_marketing_kpi')
    if df_mkt is not None and not df_mkt.empty:
        fig, ax1 = plt.subplots(figsize=(10, 5))
        ax1.plot(df_mkt.index, df_mkt['ingresos_totales'], color='#003366', marker='o', label='Ingresos')
        ax2 = ax1.twinx()
        ax2.plot(df_mkt.index, df_mkt['roas'], color='#008080', linestyle='--', marker='s', label='ROAS')
        plt.title('Evolución: Ingresos Totales vs ROAS')
        plt.savefig(os.path.join(ruta_reportes, '01_tendencia_ventas_roas.png'), dpi=300)
        plt.close()

    # --- 2. GRÁFICO: Clasificación ABC de Rentabilidad ---
    df_rent = tablas_kpi.get('rentabilidad_kpi')
    if df_rent is not None and not df_rent.empty:
        plt.figure(figsize=(10, 5))
        sns.barplot(data=df_rent.head(5), x='ganancia_neta', y='nombre_producto', palette=paleta)
        plt.title('Top 5 Productos: Contribución a Ganancia Neta')
        plt.savefig(os.path.join(ruta_reportes, '02_rentabilidad_top5.png'), dpi=300)
        plt.close()

    # --- 3. GRÁFICO: Distribución de Ingresos por Canal (Demografía) ---
    df_demo = tablas_kpi.get('demografia_canales')
    if df_demo is not None and not df_demo.empty:
        df_canal = df_demo.groupby('canal_venta')['ingresos_generados'].sum().reset_index()
        plt.figure(figsize=(7, 7))
        plt.pie(df_canal['ingresos_generados'], labels=df_canal['canal_venta'], autopct='%1.1f%%', colors=paleta)
        plt.title('Ingresos por Canal de Venta')
        plt.savefig(os.path.join(ruta_reportes, '03_distribucion_canal.png'), dpi=300)
        plt.close()

    # --- 4. GRÁFICO: Ranking de Clientes (Top 5) ---
    df_top = tablas_kpi.get('top_clientes')
    if df_top is not None and not df_top.empty:
        plt.figure(figsize=(10, 5))
        sns.barplot(data=df_top.head(5), x='total_comprado', y='nombre_cliente', palette=paleta)
        plt.title('Ranking: Top 5 Clientes por Volumen de Compra')
        plt.savefig(os.path.join(ruta_reportes, '04_ranking_clientes.png'), dpi=300)
        plt.close()

    # --- 5. GRÁFICO: Salud de Inventario (Ratio Salida) ---
    df_inv = tablas_kpi.get('inventario_kpi')
    if df_inv is not None and not df_inv.empty:
        plt.figure(figsize=(10, 5))
        sns.barplot(data=df_inv.sort_values('ratio_salida_stock', ascending=False).head(5), 
                    x='ratio_salida_stock', y='nombre_producto', palette=paleta)
        plt.title('Top 5 Productos con Mayor Rotación (Riesgo Agotamiento)')
        plt.savefig(os.path.join(ruta_reportes, '05_inventario_rotacion.png'), dpi=300)
        plt.close()

    print(f"✅ Dashboard Completo generado en: {ruta_reportes}")