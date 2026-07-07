"""
generar_dashboard_html.py
Genera un dashboard HTML paginado y profesional a partir del Data Warehouse SQLite.
Paleta: slate blues / grises / esmeralda — sin colores neón.

Uso:
    cd proyecto_final_grupo2
    python src/analytics/generar_dashboard_html.py
"""

import os
import json
import sqlite3

import numpy as np
import pandas as pd

# ─── Rutas ────────────────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DW_PATH   = os.path.join(BASE_DIR, "data", "datacommerce_dw.db")
OUT_PATH  = os.path.join(BASE_DIR, "dashboards", "dashboard_ejecutivo.html")
os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

# ─── Helpers ──────────────────────────────────────────────────────────────────
def q(sql):
    with sqlite3.connect(DW_PATH) as conn:
        return pd.read_sql_query(sql, conn)

def safe_json(obj):
    if isinstance(obj, (np.integer, np.int64)):   return int(obj)
    if isinstance(obj, (np.floating, np.float64)):
        return float(obj) if not (np.isnan(obj) or np.isinf(obj)) else 0.0
    if isinstance(obj, pd.Timestamp): return obj.strftime("%Y-%m-%d")
    if pd.isna(obj): return None
    return obj

def to_json(df):
    return json.dumps(df.map(safe_json).to_dict(orient="records"))

def fmt_q(v):
    v = float(v)
    if abs(v) >= 1e9: return f"Q{v/1e9:.2f}B"
    if abs(v) >= 1e6: return f"Q{v/1e6:.1f}M"
    if abs(v) >= 1e3: return f"Q{v/1e3:.1f}K"
    return f"Q{v:,.0f}"

# ─── Carga de datos ────────────────────────────────────────────────────────────
print("Cargando datos…")

df_canal = q("""
    SELECT dc.canal_venta AS canal, SUM(fv.total_venta) AS ingresos, COUNT(fv.venta_id) AS pedidos
    FROM fact_ventas fv JOIN dim_canal dc ON fv.canal_key=dc.canal_key
    GROUP BY canal ORDER BY ingresos DESC
""")

df_mens = q("""
    SELECT dt.anio, dt.mes, dt.nombre_mes,
           SUM(fv.total_venta) AS ingresos, SUM(fv.descuento) AS descuentos, COUNT(fv.venta_id) AS transacciones
    FROM fact_ventas fv JOIN dim_tiempo dt ON fv.fecha_key=dt.fecha_key
    GROUP BY dt.anio, dt.mes, dt.nombre_mes ORDER BY dt.anio, dt.mes
""")
df_mens["label"] = df_mens["nombre_mes"].str[:3] + " " + df_mens["anio"].astype(str)

df_rent = q("""
    SELECT dp.nombre_producto, dp.categoria,
           SUM(fv.total_venta) AS ingresos,
           SUM(fv.total_venta)-SUM(fv.cantidad*dp.costo_unitario) AS ganancia,
           SUM(fv.descuento) AS descuentos, SUM(fv.cantidad) AS unidades
    FROM fact_ventas fv JOIN dim_producto dp ON fv.producto_key=dp.producto_key
    GROUP BY dp.nombre_producto, dp.categoria ORDER BY ganancia DESC LIMIT 10
""")
df_rent["margen_pct"] = (df_rent["ganancia"]/df_rent["ingresos"].replace(0,np.nan)*100).fillna(0).round(1)

df_cli = q("""
    SELECT dc.nombre AS cliente, dc.segmento_cliente AS segmento,
           SUM(fv.total_venta) AS total, COUNT(fv.venta_id) AS pedidos
    FROM fact_ventas fv JOIN dim_cliente dc ON fv.cliente_key=dc.cliente_key
    WHERE dc.nombre != 'Cliente no registrado'
    GROUP BY dc.nombre, dc.segmento_cliente ORDER BY total DESC LIMIT 10
""")

df_inv = q("""
    SELECT dp.nombre_producto, db.nombre_bodega, fi.existencia AS stock_actual,
           COALESCE(sal.salidas,0) AS salidas
    FROM fact_inventario fi
    JOIN dim_producto dp ON fi.producto_key=dp.producto_key
    JOIN dim_bodega   db ON fi.bodega_key=db.bodega_key
    LEFT JOIN (SELECT producto_key, SUM(cantidad) AS salidas FROM fact_movimientos_inventario
               WHERE tipo_movimiento='Salida' GROUP BY producto_key) sal ON fi.producto_key=sal.producto_key
    ORDER BY fi.existencia ASC LIMIT 12
""")

df_pago = q("""
    SELECT dmp.metodo_pago AS metodo, COUNT(fv.venta_id) AS pedidos, SUM(fv.total_venta) AS ingresos
    FROM fact_ventas fv JOIN dim_metodo_pago dmp ON fv.metodo_pago_key=dmp.metodo_pago_key
    GROUP BY metodo ORDER BY pedidos DESC LIMIT 8
""")

df_depto = q("""
    SELECT dc.departamento, SUM(fv.total_venta) AS ingresos, COUNT(fv.venta_id) AS pedidos
    FROM fact_ventas fv JOIN dim_cliente dc ON fv.cliente_key=dc.cliente_key
    WHERE dc.departamento IS NOT NULL AND dc.departamento != ''
    GROUP BY dc.departamento ORDER BY ingresos DESC LIMIT 10
""")

# KPIs
total_ing   = float(df_canal["ingresos"].sum())
total_ped   = float(df_canal["pedidos"].sum())
ticket_prom = total_ing / total_ped if total_ped else 0
gan_total   = float(df_rent["ganancia"].sum())
margen_prom = float(df_rent["margen_pct"].mean()) if not df_rent.empty else 0
desc_total  = float(df_mens["descuentos"].sum())
agotados    = int(q("SELECT COUNT(*) n FROM fact_inventario WHERE existencia=0").iloc[0]["n"])
canal_top   = df_canal.iloc[0]["canal"] if not df_canal.empty else "—"
pago_top    = df_pago.iloc[0]["metodo"]  if not df_pago.empty else "—"
ing_act     = float(df_mens.iloc[-1]["ingresos"]) if not df_mens.empty else 0
ing_ant     = float(df_mens.iloc[-2]["ingresos"]) if len(df_mens)>=2 else 0
mom         = ((ing_act-ing_ant)/ing_ant*100) if ing_ant else 0
mom_str     = ("+" if mom>=0 else "") + f"{mom:.1f}%"
mom_up      = mom >= 0

# Serializar a JSON
j_canal  = to_json(df_canal)
j_mens   = to_json(df_mens.tail(24))
j_rent   = to_json(df_rent)
j_cli    = to_json(df_cli)
j_inv    = to_json(df_inv)
j_pago   = to_json(df_pago)
j_depto  = to_json(df_depto)

print("Construyendo HTML…")

# ─── Plantilla HTML ────────────────────────────────────────────────────────────
HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>DataCommerce GT — Dashboard Ejecutivo</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
/* ── Reset & Base ── */
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:        #0F172A;
  --surface:   #1E293B;
  --surface2:  #263148;
  --border:    #334155;
  --border2:   #475569;
  --text:      #F1F5F9;
  --muted:     #94A3B8;
  --muted2:    #64748B;
  --blue:      #3B82F6;
  --blue-d:    #2563EB;
  --emerald:   #10B981;
  --amber:     #F59E0B;
  --red:       #EF4444;
  --violet:    #8B5CF6;
  --sky:       #0EA5E9;
  --teal:      #14B8A6;
  --sidebar-w: 240px;
}
html,body{height:100%;font-family:'Inter',sans-serif;background:var(--bg);color:var(--text);font-size:14px}

/* ── Scrollbar ── */
::-webkit-scrollbar{width:6px;height:6px}
::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:var(--border2);border-radius:3px}

/* ── Layout ── */
.app{display:flex;height:100vh;overflow:hidden}

/* ── Sidebar ── */
.sidebar{
  width:var(--sidebar-w);flex-shrink:0;
  background:var(--surface);border-right:1px solid var(--border);
  display:flex;flex-direction:column;padding:24px 0;
  position:relative;z-index:10;
}
.brand{padding:0 20px 24px;border-bottom:1px solid var(--border)}
.brand-icon{
  width:40px;height:40px;border-radius:10px;
  background:linear-gradient(135deg,var(--blue),var(--violet));
  display:flex;align-items:center;justify-content:center;
  font-size:18px;margin-bottom:12px;font-weight:700;color:#fff
}
.brand h1{font-size:15px;font-weight:700;color:var(--text);line-height:1.2}
.brand p{font-size:11px;color:var(--muted);margin-top:2px;letter-spacing:.5px;text-transform:uppercase}

.nav{padding:16px 12px;flex:1;overflow-y:auto}
.nav-section{font-size:10px;font-weight:600;color:var(--muted2);letter-spacing:1px;
             text-transform:uppercase;padding:0 8px;margin:12px 0 6px}
.nav-item{
  display:flex;align-items:center;gap:10px;padding:9px 12px;
  border-radius:8px;cursor:pointer;transition:all .15s;
  color:var(--muted);font-size:13px;font-weight:500;margin-bottom:2px
}
.nav-item:hover{background:var(--surface2);color:var(--text)}
.nav-item.active{background:rgba(59,130,246,.15);color:var(--blue);border:1px solid rgba(59,130,246,.25)}
.nav-item .icon{width:18px;text-align:center;font-size:15px;flex-shrink:0}

.sidebar-footer{
  padding:16px 20px;border-top:1px solid var(--border);
  font-size:11px;color:var(--muted2)
}
.status-dot{
  display:inline-block;width:7px;height:7px;border-radius:50%;
  background:var(--emerald);margin-right:6px;
  box-shadow:0 0 6px var(--emerald);
}

/* ── Main ── */
.main{flex:1;display:flex;flex-direction:column;overflow:hidden}
.topbar{
  background:var(--surface);border-bottom:1px solid var(--border);
  padding:14px 28px;display:flex;align-items:center;justify-content:space-between;
  flex-shrink:0
}
.topbar-title{font-size:16px;font-weight:600;color:var(--text)}
.topbar-sub{font-size:12px;color:var(--muted);margin-top:2px}
.topbar-badge{
  background:rgba(59,130,246,.12);border:1px solid rgba(59,130,246,.25);
  color:var(--blue);font-size:11px;font-weight:600;padding:5px 12px;border-radius:20px
}

.content{flex:1;overflow-y:auto;padding:28px}

/* ── Pages ── */
.page{display:none;animation:fadein .25s ease}
.page.active{display:block}
@keyframes fadein{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:translateY(0)}}

/* ── Section headers ── */
.section-header{margin-bottom:20px}
.section-header h2{font-size:18px;font-weight:700;color:var(--text)}
.section-header p{font-size:13px;color:var(--muted);margin-top:4px}

/* ── KPI Cards grid ── */
.kpi-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:16px;margin-bottom:28px}
.kpi-card{
  background:var(--surface);border:1px solid var(--border);border-radius:12px;
  padding:20px;position:relative;overflow:hidden;transition:border-color .2s
}
.kpi-card:hover{border-color:var(--border2)}
.kpi-card .kpi-label{font-size:11px;font-weight:600;color:var(--muted);letter-spacing:.5px;
                      text-transform:uppercase;margin-bottom:8px}
.kpi-card .kpi-value{font-size:24px;font-weight:700;color:var(--text);line-height:1}
.kpi-card .kpi-sub{font-size:11px;color:var(--muted);margin-top:8px}
.kpi-card .kpi-accent{position:absolute;top:0;left:0;width:3px;height:100%;border-radius:12px 0 0 12px}
.kpi-card .kpi-badge{
  display:inline-block;font-size:10px;font-weight:600;padding:2px 8px;
  border-radius:20px;margin-top:6px
}
.badge-up{background:rgba(16,185,129,.12);color:var(--emerald);border:1px solid rgba(16,185,129,.2)}
.badge-down{background:rgba(239,68,68,.12);color:var(--red);border:1px solid rgba(239,68,68,.2)}
.badge-warn{background:rgba(245,158,11,.12);color:var(--amber);border:1px solid rgba(245,158,11,.2)}
.badge-info{background:rgba(59,130,246,.12);color:var(--blue);border:1px solid rgba(59,130,246,.2)}

/* ── Chart cards ── */
.grid-2{display:grid;grid-template-columns:2fr 1fr;gap:20px;margin-bottom:20px}
.grid-2-equal{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:20px}
.grid-3{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-bottom:20px}
.grid-full{margin-bottom:20px}

.chart-card{
  background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:22px
}
.chart-card h3{font-size:14px;font-weight:600;color:var(--text);margin-bottom:4px}
.chart-card .chart-sub{font-size:12px;color:var(--muted);margin-bottom:18px}
.chart-wrap{position:relative;width:100%}

/* ── Tables ── */
.data-table{width:100%;border-collapse:collapse;font-size:13px}
.data-table th{
  text-align:left;padding:10px 14px;font-size:11px;font-weight:600;
  color:var(--muted);letter-spacing:.5px;text-transform:uppercase;
  border-bottom:1px solid var(--border);background:var(--surface2)
}
.data-table td{padding:11px 14px;border-bottom:1px solid var(--border);color:var(--text)}
.data-table tr:last-child td{border-bottom:none}
.data-table tr:hover td{background:var(--surface2)}
.pill{
  display:inline-block;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:600
}
.pill-blue{background:rgba(59,130,246,.12);color:var(--blue)}
.pill-green{background:rgba(16,185,129,.12);color:var(--emerald)}
.pill-amber{background:rgba(245,158,11,.12);color:var(--amber)}
.pill-red{background:rgba(239,68,68,.12);color:var(--red)}
.pill-violet{background:rgba(139,92,246,.12);color:var(--violet)}

/* ── Stat row ── */
.stat-row{display:flex;gap:20px;margin-bottom:20px;flex-wrap:wrap}
.stat-item{
  flex:1;min-width:140px;background:var(--surface);border:1px solid var(--border);
  border-radius:10px;padding:16px 20px
}
.stat-item .s-label{font-size:11px;color:var(--muted);font-weight:600;letter-spacing:.4px;text-transform:uppercase}
.stat-item .s-value{font-size:20px;font-weight:700;margin-top:4px}

/* ── Progress bar ── */
.progress-bar{background:var(--border);border-radius:4px;height:6px;margin-top:6px;overflow:hidden}
.progress-fill{height:100%;border-radius:4px;transition:width .5s}

/* ── Search ── */
.search-wrap{margin-bottom:16px}
.search-input{
  width:100%;max-width:320px;background:var(--surface2);border:1px solid var(--border);
  border-radius:8px;padding:9px 14px;color:var(--text);font-size:13px;font-family:'Inter',sans-serif
}
.search-input:focus{outline:none;border-color:var(--blue)}
.search-input::placeholder{color:var(--muted)}
</style>
</head>
<body>
<div class="app">

<!-- ══════════ SIDEBAR ══════════ -->
<aside class="sidebar">
  <div class="brand">
    <div class="brand-icon">DC</div>
    <h1>DataCommerce GT</h1>
    <p>Business Intelligence</p>
  </div>
  <nav class="nav">
    <div class="nav-section">Análisis</div>
    <div class="nav-item active" onclick="goTo('resumen',this)">
      <span class="icon">&#9632;</span> Resumen Ejecutivo
    </div>
    <div class="nav-item" onclick="goTo('ventas',this)">
      <span class="icon">&#9650;</span> Ventas &amp; Tendencias
    </div>
    <div class="nav-item" onclick="goTo('rentabilidad',this)">
      <span class="icon">&#9670;</span> Rentabilidad &amp; Margen
    </div>
    <div class="nav-section">Operaciones</div>
    <div class="nav-item" onclick="goTo('inventario',this)">
      <span class="icon">&#9744;</span> Inventario &amp; Stock
    </div>
    <div class="nav-item" onclick="goTo('clientes',this)">
      <span class="icon">&#9737;</span> Clientes &amp; Canales
    </div>
  </nav>
  <div class="sidebar-footer">
    <span class="status-dot"></span>DW Local Sincronizado<br>
    <span style="margin-top:4px;display:block">datacommerce_dw.db</span>
  </div>
</aside>

<!-- ══════════ MAIN ══════════ -->
<div class="main">
  <div class="topbar">
    <div>
      <div class="topbar-title" id="page-title">Resumen Ejecutivo</div>
      <div class="topbar-sub">Dashboard General de Inteligencia de Negocio &mdash; DataCommerce GT</div>
    </div>
    <div class="topbar-badge">&#9679; En vivo &mdash; SQLite Local</div>
  </div>

  <div class="content">

    <!-- ════ PAGE: RESUMEN ════ -->
    <div class="page active" id="page-resumen">
      <div class="section-header">
        <h2>Resumen Ejecutivo</h2>
        <p>Vista consolidada de los indicadores clave de desempe&ntilde;o del negocio.</p>
      </div>

      <div class="kpi-grid" id="kpi-cards">
        <!-- Filled by JS -->
      </div>

      <div class="grid-2">
        <div class="chart-card">
          <h3>Evoluci&oacute;n de Ingresos Mensuales</h3>
          <p class="chart-sub">Ingresos por mes &mdash; &uacute;ltimos 24 meses</p>
          <div class="chart-wrap" style="height:280px"><canvas id="ch-resumen-mens"></canvas></div>
        </div>
        <div class="chart-card">
          <h3>Ingresos por Canal de Venta</h3>
          <p class="chart-sub">Distribuci&oacute;n porcentual por canal</p>
          <div class="chart-wrap" style="height:280px"><canvas id="ch-resumen-canal"></canvas></div>
        </div>
      </div>

      <div class="grid-2-equal">
        <div class="chart-card">
          <h3>Top 5 Productos m&aacute;s Rentables</h3>
          <p class="chart-sub">Por ganancia neta acumulada</p>
          <div class="chart-wrap" style="height:220px"><canvas id="ch-resumen-top5"></canvas></div>
        </div>
        <div class="chart-card">
          <h3>M&eacute;todos de Pago</h3>
          <p class="chart-sub">Preferencia por volumen de transacciones</p>
          <div class="chart-wrap" style="height:220px"><canvas id="ch-resumen-pago"></canvas></div>
        </div>
      </div>
    </div>

    <!-- ════ PAGE: VENTAS ════ -->
    <div class="page" id="page-ventas">
      <div class="section-header">
        <h2>Ventas &amp; Tendencias</h2>
        <p>An&aacute;lisis detallado del comportamiento de ventas por per&iacute;odo, canal y regi&oacute;n.</p>
      </div>

      <div class="stat-row" id="stat-ventas"><!-- JS --></div>

      <div class="grid-full chart-card">
        <h3>Ingresos vs Transacciones Mensuales</h3>
        <p class="chart-sub">Comparativa de ingresos (barras) y volumen de pedidos (l&iacute;nea) &mdash; &uacute;ltimos 24 meses</p>
        <div class="chart-wrap" style="height:320px"><canvas id="ch-ventas-combo"></canvas></div>
      </div>

      <div class="grid-2">
        <div class="chart-card">
          <h3>Participaci&oacute;n por Canal</h3>
          <p class="chart-sub">Porcentaje de ingresos por canal de venta</p>
          <div class="chart-wrap" style="height:280px"><canvas id="ch-ventas-canal"></canvas></div>
        </div>
        <div class="chart-card">
          <h3>Ingresos por Departamento</h3>
          <p class="chart-sub">Top 10 departamentos geogr&aacute;ficos por ingresos</p>
          <div class="chart-wrap" style="height:280px"><canvas id="ch-ventas-depto"></canvas></div>
        </div>
      </div>
    </div>

    <!-- ════ PAGE: RENTABILIDAD ════ -->
    <div class="page" id="page-rentabilidad">
      <div class="section-header">
        <h2>Rentabilidad &amp; M&aacute;rgenes</h2>
        <p>An&aacute;lisis de ganancia neta, m&aacute;rgenes por producto y el impacto de los descuentos.</p>
      </div>

      <div class="stat-row" id="stat-rent"><!-- JS --></div>

      <div class="chart-card grid-full">
        <h3>Top 10 Productos &mdash; Ganancia Neta y Margen (%)</h3>
        <p class="chart-sub">Ordenados por mayor contribuci&oacute;n a la utilidad total</p>
        <div class="chart-wrap" style="height:340px"><canvas id="ch-rent-top10"></canvas></div>
      </div>

      <div class="grid-2-equal">
        <div class="chart-card">
          <h3>Distribuci&oacute;n de Ganancia por Categor&iacute;a</h3>
          <p class="chart-sub">Participaci&oacute;n de cada categor&iacute;a en la utilidad total</p>
          <div class="chart-wrap" style="height:260px"><canvas id="ch-rent-cat"></canvas></div>
        </div>
        <div class="chart-card">
          <h3>Descuentos Cedidos por Mes</h3>
          <p class="chart-sub">Impacto mensual de los descuentos en los ingresos</p>
          <div class="chart-wrap" style="height:260px"><canvas id="ch-rent-desc"></canvas></div>
        </div>
      </div>
    </div>

    <!-- ════ PAGE: INVENTARIO ════ -->
    <div class="page" id="page-inventario">
      <div class="section-header">
        <h2>Inventario &amp; Stock</h2>
        <p>Estado actual del inventario, alertas de reabastecimiento y rotaci&oacute;n de productos.</p>
      </div>

      <div class="stat-row" id="stat-inv"><!-- JS --></div>

      <div class="grid-2">
        <div class="chart-card">
          <h3>Stock Actual vs Unidades Despachadas</h3>
          <p class="chart-sub">Productos con menor nivel de existencias</p>
          <div class="chart-wrap" style="height:300px"><canvas id="ch-inv-stock"></canvas></div>
        </div>
        <div class="chart-card">
          <h3>Alertas Cr&iacute;ticas de Inventario</h3>
          <p class="chart-sub">Estado de existencias por producto y bodega</p>
          <div class="search-wrap">
            <input class="search-input" type="text" placeholder="Buscar producto..." oninput="filterInv(this.value)">
          </div>
          <div style="overflow:auto;max-height:260px">
            <table class="data-table" id="tbl-inv">
              <thead><tr><th>Producto</th><th>Bodega</th><th>Stock</th><th>Salidas</th><th>Estado</th></tr></thead>
              <tbody id="tbl-inv-body"></tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- ════ PAGE: CLIENTES ════ -->
    <div class="page" id="page-clientes">
      <div class="section-header">
        <h2>Clientes &amp; Canales</h2>
        <p>Clientes VIP, m&eacute;todos de pago preferidos y distribuci&oacute;n geogr&aacute;fica de ventas.</p>
      </div>

      <div class="stat-row" id="stat-cli"><!-- JS --></div>

      <div class="grid-2">
        <div class="chart-card">
          <h3>Top 10 Clientes VIP</h3>
          <p class="chart-sub">Clientes con mayor volumen de compra total</p>
          <div class="search-wrap">
            <input class="search-input" type="text" placeholder="Buscar cliente..." oninput="filterCli(this.value)">
          </div>
          <div style="overflow:auto;max-height:300px">
            <table class="data-table" id="tbl-cli">
              <thead><tr><th>#</th><th>Cliente</th><th>Segmento</th><th>Pedidos</th><th>Total Comprado</th><th>% del Total</th></tr></thead>
              <tbody id="tbl-cli-body"></tbody>
            </table>
          </div>
        </div>
        <div class="chart-card">
          <h3>M&eacute;todos de Pago Favoritos</h3>
          <p class="chart-sub">Distribuci&oacute;n de transacciones por m&eacute;todo</p>
          <div class="chart-wrap" style="height:280px"><canvas id="ch-cli-pago"></canvas></div>
        </div>
      </div>

      <div class="chart-card grid-full">
        <h3>Ingresos por Departamento Geogr&aacute;fico</h3>
        <p class="chart-sub">Top 10 departamentos con mayor aporte a las ventas</p>
        <div class="chart-wrap" style="height:280px"><canvas id="ch-cli-depto"></canvas></div>
      </div>
    </div>

  </div><!-- /content -->
</div><!-- /main -->
</div><!-- /app -->

<script>
// ══════════════════════════════════════════════════════════════
//  DATA (injected by Python)
// ══════════════════════════════════════════════════════════════
const D_CANAL  = __D_CANAL__;
const D_MENS   = __D_MENS__;
const D_RENT   = __D_RENT__;
const D_CLI    = __D_CLI__;
const D_INV    = __D_INV__;
const D_PAGO   = __D_PAGO__;
const D_DEPTO  = __D_DEPTO__;

const KPI = {
  total_ing:   __TOTAL_ING__,
  total_ped:   __TOTAL_PED__,
  ticket_prom: __TICKET_PROM__,
  gan_total:   __GAN_TOTAL__,
  margen_prom: __MARGEN_PROM__,
  desc_total:  __DESC_TOTAL__,
  agotados:    __AGOTADOS__,
  canal_top:   "__CANAL_TOP__",
  pago_top:    "__PAGO_TOP__",
  ing_act:     __ING_ACT__,
  mom_str:     "__MOM_STR__",
  mom_up:      __MOM_UP__,
};

// ══════════════════════════════════════════════════════════════
//  HELPERS
// ══════════════════════════════════════════════════════════════
function fmtQ(v){
  if(Math.abs(v)>=1e9) return 'Q'+(v/1e9).toFixed(2)+'B';
  if(Math.abs(v)>=1e6) return 'Q'+(v/1e6).toFixed(1)+'M';
  if(Math.abs(v)>=1e3) return 'Q'+(v/1e3).toFixed(1)+'K';
  return 'Q'+v.toFixed(0).replace(/\B(?=(\\d{3})+(?!\\d))/g,',');
}
function fmtN(v){return Math.round(v).toLocaleString('es-GT')}

const C = {
  blue:'#3B82F6', emerald:'#10B981', amber:'#F59E0B',
  red:'#EF4444',  violet:'#8B5CF6', sky:'#0EA5E9',
  teal:'#14B8A6', rose:'#F43F5E',  orange:'#F97316',
  indigo:'#6366F1',slate:'#64748B', lime:'#84CC16'
};
const PALETTE = Object.values(C);

const CFG = {
  plugins:{legend:{labels:{color:'#94A3B8',font:{family:'Inter',size:11}}}},
  scales:{
    x:{ticks:{color:'#64748B',font:{size:10}},grid:{color:'#1E293B'}},
    y:{ticks:{color:'#64748B',font:{size:10}},grid:{color:'#263148'}}
  }
};

function baseOpts(extra){return Object.assign({responsive:true,maintainAspectRatio:false,plugins:CFG.plugins},extra);}

// ══════════════════════════════════════════════════════════════
//  NAVIGATION
// ══════════════════════════════════════════════════════════════
const TITLES = {resumen:'Resumen Ejecutivo',ventas:'Ventas & Tendencias',
                rentabilidad:'Rentabilidad & Márgenes',inventario:'Inventario & Stock',
                clientes:'Clientes & Canales'};

function goTo(id, el){
  document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n=>n.classList.remove('active'));
  document.getElementById('page-'+id).classList.add('active');
  el.classList.add('active');
  document.getElementById('page-title').textContent = TITLES[id];
  renderPage(id);
}

// ══════════════════════════════════════════════════════════════
//  KPI CARDS
// ══════════════════════════════════════════════════════════════
function buildKPICards(){
  const cards = [
    {label:'Ingresos Totales',   value:fmtQ(KPI.total_ing),   sub:'Acumulado global',         color:C.blue,    badge:'info'},
    {label:'Crecimiento MoM',    value:KPI.mom_str,            sub:'Mes anterior vs actual',   color:KPI.mom_up?C.emerald:C.red, badge:KPI.mom_up?'up':'down'},
    {label:'Ticket Promedio',    value:fmtQ(KPI.ticket_prom),  sub:fmtN(KPI.total_ped)+' transacciones', color:C.violet, badge:'info'},
    {label:'Margen Rentabilidad',value:KPI.margen_prom.toFixed(1)+'%', sub:'Top 10 productos', color:C.amber,   badge:'warn'},
    {label:'Productos Agotados', value:String(KPI.agotados),   sub:'Requieren reabastecimiento',color:C.red,   badge:'down'},
    {label:'Descuentos Cedidos', value:fmtQ(KPI.desc_total),  sub:'Canal estrella: '+KPI.canal_top, color:C.teal, badge:'info'},
  ];
  const container = document.getElementById('kpi-cards');
  container.innerHTML = cards.map(c=>`
    <div class="kpi-card">
      <div class="kpi-accent" style="background:${c.color}"></div>
      <div class="kpi-label">${c.label}</div>
      <div class="kpi-value" style="color:${c.color}">${c.value}</div>
      <div class="kpi-sub">${c.sub}</div>
    </div>`).join('');
}

// ══════════════════════════════════════════════════════════════
//  CHART REGISTRY (prevent duplicates)
// ══════════════════════════════════════════════════════════════
const charts = {};
function mkChart(id, config){
  if(charts[id]) charts[id].destroy();
  const ctx = document.getElementById(id);
  if(!ctx) return;
  charts[id] = new Chart(ctx, config);
}

// ══════════════════════════════════════════════════════════════
//  RENDER PER PAGE
// ══════════════════════════════════════════════════════════════
const rendered = new Set();

function renderPage(id){
  if(rendered.has(id)) return;
  rendered.add(id);
  if(id==='resumen')       renderResumen();
  if(id==='ventas')        renderVentas();
  if(id==='rentabilidad')  renderRentabilidad();
  if(id==='inventario')    renderInventario();
  if(id==='clientes')      renderClientes();
}

// ─── RESUMEN ──────────────────────────────────────────────────
function renderResumen(){
  const mens24 = D_MENS.slice(-24);
  mkChart('ch-resumen-mens',{
    type:'bar',
    data:{
      labels:mens24.map(r=>r.label),
      datasets:[{
        label:'Ingresos',data:mens24.map(r=>r.ingresos),
        backgroundColor:'rgba(59,130,246,.65)',borderColor:C.blue,borderWidth:1,borderRadius:4
      }]
    },
    options:{...baseOpts(),scales:{
      x:{...CFG.scales.x,ticks:{...CFG.scales.x.ticks,maxRotation:45}},
      y:{...CFG.scales.y,ticks:{...CFG.scales.y.ticks,callback:v=>fmtQ(v)}}
    }}
  });

  mkChart('ch-resumen-canal',{
    type:'doughnut',
    data:{
      labels:D_CANAL.map(r=>r.canal),
      datasets:[{data:D_CANAL.map(r=>r.ingresos),backgroundColor:PALETTE,borderColor:'#1E293B',borderWidth:2}]
    },
    options:{...baseOpts({cutout:'58%'}),plugins:{
      legend:{...CFG.plugins.legend,position:'bottom',labels:{...CFG.plugins.legend.labels,padding:12,boxWidth:12}}
    }}
  });

  const top5 = D_RENT.slice(0,5);
  mkChart('ch-resumen-top5',{
    type:'bar',
    data:{
      labels:top5.map(r=>r.nombre_producto.substring(0,22)),
      datasets:[{label:'Ganancia Neta',data:top5.map(r=>r.ganancia),
        backgroundColor:'rgba(16,185,129,.7)',borderColor:C.emerald,borderWidth:1,borderRadius:4}]
    },
    options:{...baseOpts(),indexAxis:'y',scales:{
      x:{...CFG.scales.x,ticks:{callback:v=>fmtQ(v)}},
      y:{...CFG.scales.y,ticks:{color:'#94A3B8',font:{size:9}}}
    }}
  });

  mkChart('ch-resumen-pago',{
    type:'pie',
    data:{
      labels:D_PAGO.map(r=>r.metodo),
      datasets:[{data:D_PAGO.map(r=>r.pedidos),backgroundColor:PALETTE,borderColor:'#1E293B',borderWidth:2}]
    },
    options:{...baseOpts(),plugins:{
      legend:{...CFG.plugins.legend,position:'right',labels:{...CFG.plugins.legend.labels,padding:10,boxWidth:12}}
    }}
  });
}

// ─── VENTAS ───────────────────────────────────────────────────
function renderVentas(){
  const mens24 = D_MENS.slice(-24);

  // Stat row
  document.getElementById('stat-ventas').innerHTML = [
    {l:'Ingresos Totales',      v:fmtQ(KPI.total_ing),     c:C.blue},
    {l:'Ingresos Último Mes',   v:fmtQ(KPI.ing_act),       c:C.emerald},
    {l:'Crecimiento MoM',       v:KPI.mom_str,             c:KPI.mom_up?C.emerald:C.red},
    {l:'Transacciones Totales', v:fmtN(KPI.total_ped),     c:C.violet},
    {l:'Canal Estrella',        v:KPI.canal_top,           c:C.sky},
  ].map(s=>`<div class="stat-item"><div class="s-label">${s.l}</div>
    <div class="s-value" style="color:${s.c}">${s.v}</div></div>`).join('');

  mkChart('ch-ventas-combo',{
    type:'bar',
    data:{
      labels:mens24.map(r=>r.label),
      datasets:[
        {type:'bar',  label:'Ingresos', data:mens24.map(r=>r.ingresos),
         backgroundColor:'rgba(59,130,246,.55)',borderColor:C.blue,borderWidth:1,borderRadius:3,yAxisID:'y'},
        {type:'line', label:'Transacciones', data:mens24.map(r=>r.transacciones),
         borderColor:C.emerald,backgroundColor:'rgba(16,185,129,.08)',
         borderWidth:2,pointRadius:3,tension:.35,yAxisID:'y1'}
      ]
    },
    options:{...baseOpts(),scales:{
      x:{...CFG.scales.x,ticks:{...CFG.scales.x.ticks,maxRotation:45}},
      y:{...CFG.scales.y,ticks:{callback:v=>fmtQ(v)},title:{display:true,text:'Ingresos',color:'#64748B',font:{size:10}}},
      y1:{position:'right',ticks:{color:'#64748B',font:{size:10},callback:v=>fmtN(v)},
          grid:{drawOnChartArea:false},title:{display:true,text:'Transacciones',color:'#64748B',font:{size:10}}}
    }}
  });

  mkChart('ch-ventas-canal',{
    type:'doughnut',
    data:{
      labels:D_CANAL.map(r=>r.canal),
      datasets:[{data:D_CANAL.map(r=>r.ingresos),backgroundColor:PALETTE,borderColor:'#1E293B',borderWidth:2}]
    },
    options:{...baseOpts({cutout:'55%'}),plugins:{
      legend:{...CFG.plugins.legend,position:'bottom',labels:{...CFG.plugins.legend.labels,padding:8,boxWidth:10,font:{size:10}}}
    }}
  });

  mkChart('ch-ventas-depto',{
    type:'bar',
    data:{
      labels:D_DEPTO.map(r=>r.departamento),
      datasets:[{label:'Ingresos',data:D_DEPTO.map(r=>r.ingresos),
        backgroundColor:PALETTE,borderRadius:4}]
    },
    options:{...baseOpts(),plugins:{legend:{display:false}},scales:{
      x:{...CFG.scales.x,ticks:{...CFG.scales.x.ticks,maxRotation:40}},
      y:{...CFG.scales.y,ticks:{callback:v=>fmtQ(v)}}
    }}
  });
}

// ─── RENTABILIDAD ─────────────────────────────────────────────
function renderRentabilidad(){
  document.getElementById('stat-rent').innerHTML = [
    {l:'Utilidad Neta (Top10)',  v:fmtQ(KPI.gan_total),    c:C.emerald},
    {l:'Margen Promedio',        v:KPI.margen_prom.toFixed(1)+'%', c:C.amber},
    {l:'Descuentos Cedidos',     v:fmtQ(KPI.desc_total),   c:C.red},
    {l:'Ingresos Brutos',        v:fmtQ(KPI.total_ing),    c:C.blue},
  ].map(s=>`<div class="stat-item"><div class="s-label">${s.l}</div>
    <div class="s-value" style="color:${s.c}">${s.v}</div></div>`).join('');

  mkChart('ch-rent-top10',{
    type:'bar',
    data:{
      labels:D_RENT.map(r=>r.nombre_producto.substring(0,32)),
      datasets:[
        {label:'Ganancia Neta',data:D_RENT.map(r=>r.ganancia),
         backgroundColor:'rgba(16,185,129,.7)',borderColor:C.emerald,borderWidth:1,borderRadius:4},
        {type:'line',label:'Margen %',data:D_RENT.map(r=>r.margen_pct),
         borderColor:C.amber,backgroundColor:'transparent',borderWidth:2,pointRadius:4,yAxisID:'y1'}
      ]
    },
    options:{...baseOpts(),indexAxis:'y',scales:{
      x:{...CFG.scales.x,ticks:{callback:v=>fmtQ(v)}},
      y:{...CFG.scales.y,ticks:{color:'#94A3B8',font:{size:9}}},
      y1:{display:false}
    }}
  });

  // Dona por categoría
  const catMap = {};
  D_RENT.forEach(r=>{catMap[r.categoria]=(catMap[r.categoria]||0)+r.ganancia;});
  const catK = Object.keys(catMap), catV = Object.values(catMap);
  mkChart('ch-rent-cat',{
    type:'doughnut',
    data:{labels:catK,datasets:[{data:catV,backgroundColor:PALETTE,borderColor:'#1E293B',borderWidth:2}]},
    options:{...baseOpts({cutout:'52%'}),plugins:{
      legend:{...CFG.plugins.legend,position:'right',labels:{...CFG.plugins.legend.labels,padding:10,boxWidth:12}}
    }}
  });

  // Barras de descuentos mensuales
  const mens24 = D_MENS.slice(-24);
  mkChart('ch-rent-desc',{
    type:'bar',
    data:{
      labels:mens24.map(r=>r.label),
      datasets:[{label:'Descuentos',data:mens24.map(r=>r.descuentos),
        backgroundColor:'rgba(239,68,68,.6)',borderColor:C.red,borderWidth:1,borderRadius:3}]
    },
    options:{...baseOpts(),scales:{
      x:{...CFG.scales.x,ticks:{...CFG.scales.x.ticks,maxRotation:45}},
      y:{...CFG.scales.y,ticks:{callback:v=>fmtQ(v)}}
    }}
  });
}

// ─── INVENTARIO ───────────────────────────────────────────────
function renderInventario(){
  const totalStock = D_INV.reduce((a,r)=>a+(r.stock_actual||0),0);
  const totalSal   = D_INV.reduce((a,r)=>a+(r.salidas||0),0);
  document.getElementById('stat-inv').innerHTML = [
    {l:'Stock Total (muestra)',  v:fmtN(totalStock),       c:C.blue},
    {l:'Unidades Despachadas',   v:fmtN(totalSal),         c:C.violet},
    {l:'Productos Agotados',     v:String(KPI.agotados),   c:C.red},
  ].map(s=>`<div class="stat-item"><div class="s-label">${s.l}</div>
    <div class="s-value" style="color:${s.c}">${s.v}</div></div>`).join('');

  mkChart('ch-inv-stock',{
    type:'bar',
    data:{
      labels:D_INV.map(r=>r.nombre_producto.substring(0,24)),
      datasets:[
        {label:'Stock Actual',       data:D_INV.map(r=>r.stock_actual),
         backgroundColor:'rgba(59,130,246,.65)',borderRadius:3},
        {label:'Unidades Despachadas',data:D_INV.map(r=>r.salidas),
         backgroundColor:'rgba(245,158,11,.65)',borderRadius:3}
      ]
    },
    options:{...baseOpts(),indexAxis:'y',scales:{
      x:{...CFG.scales.x,ticks:{callback:v=>fmtN(v)}},
      y:{...CFG.scales.y,ticks:{color:'#94A3B8',font:{size:9}}}
    }}
  });

  // Tabla inventario
  buildInvTable(D_INV);
}

function buildInvTable(data){
  document.getElementById('tbl-inv-body').innerHTML = data.map(r=>{
    const s = r.stock_actual||0;
    let pill, cls;
    if(s===0){pill='Agotado';cls='pill-red';}
    else if(s<50){pill='Crítico';cls='pill-amber';}
    else{pill='Estable';cls='pill-green';}
    return `<tr>
      <td>${r.nombre_producto}</td>
      <td>${r.nombre_bodega}</td>
      <td>${fmtN(s)}</td>
      <td>${fmtN(r.salidas||0)}</td>
      <td><span class="pill ${cls}">${pill}</span></td>
    </tr>`;
  }).join('');
}

function filterInv(q){
  const rows = document.querySelectorAll('#tbl-inv-body tr');
  rows.forEach(r=>{r.style.display=r.cells[0].textContent.toLowerCase().includes(q.toLowerCase())?'':'none';});
}

// ─── CLIENTES ─────────────────────────────────────────────────
function renderClientes(){
  const gran = D_CLI.reduce((a,r)=>a+(r.total||0),0);
  document.getElementById('stat-cli').innerHTML = [
    {l:'Cliente VIP #1',    v:D_CLI[0]?.cliente||'—',  c:C.blue},
    {l:'Segmento Top',      v:D_CLI[0]?.segmento||'—', c:C.violet},
    {l:'Compra Máxima',     v:fmtQ(D_CLI[0]?.total||0),c:C.emerald},
    {l:'Pago Favorito',     v:KPI.pago_top,             c:C.amber},
  ].map(s=>`<div class="stat-item"><div class="s-label">${s.l}</div>
    <div class="s-value" style="color:${s.c}">${s.v}</div></div>`).join('');

  // Tabla clientes
  document.getElementById('tbl-cli-body').innerHTML = D_CLI.map((r,i)=>{
    const pct = gran>0?(r.total/gran*100).toFixed(1):'0.0';
    const sc = {'Premium':'pill-violet','Frecuente':'pill-blue','Nuevo':'pill-green'}[r.segmento]||'pill-slate';
    return `<tr>
      <td style="color:#64748B">${i+1}</td>
      <td>${r.cliente}</td>
      <td><span class="pill ${sc}">${r.segmento}</span></td>
      <td>${fmtN(r.pedidos)}</td>
      <td style="font-weight:600;color:#10B981">${fmtQ(r.total)}</td>
      <td style="color:#F59E0B">${pct}%</td>
    </tr>`;
  }).join('');

  mkChart('ch-cli-pago',{
    type:'bar',
    data:{
      labels:D_PAGO.map(r=>r.metodo),
      datasets:[{label:'Transacciones',data:D_PAGO.map(r=>r.pedidos),
        backgroundColor:PALETTE,borderRadius:4}]
    },
    options:{...baseOpts(),plugins:{legend:{display:false}},scales:{
      x:{...CFG.scales.x,ticks:{...CFG.scales.x.ticks,maxRotation:35}},
      y:{...CFG.scales.y,ticks:{callback:v=>fmtN(v)}}
    }}
  });

  mkChart('ch-cli-depto',{
    type:'bar',
    data:{
      labels:D_DEPTO.map(r=>r.departamento),
      datasets:[{label:'Ingresos',data:D_DEPTO.map(r=>r.ingresos),
        backgroundColor:'rgba(59,130,246,.65)',borderColor:C.blue,borderWidth:1,borderRadius:4}]
    },
    options:{...baseOpts(),plugins:{legend:{display:false}},scales:{
      x:{...CFG.scales.x},
      y:{...CFG.scales.y,ticks:{callback:v=>fmtQ(v)}}
    }}
  });
}

function filterCli(q){
  const rows = document.querySelectorAll('#tbl-cli-body tr');
  rows.forEach(r=>{r.style.display=r.cells[1].textContent.toLowerCase().includes(q.toLowerCase())?'':'none';});
}

// ══════════════════════════════════════════════════════════════
//  INIT
// ══════════════════════════════════════════════════════════════
window.addEventListener('DOMContentLoaded',()=>{
  buildKPICards();
  renderPage('resumen');
});
</script>
</body>
</html>"""

# ─── Inyectar datos ───────────────────────────────────────────────────────────
HTML = (HTML
    .replace("__D_CANAL__",  j_canal)
    .replace("__D_MENS__",   j_mens)
    .replace("__D_RENT__",   j_rent)
    .replace("__D_CLI__",    j_cli)
    .replace("__D_INV__",    j_inv)
    .replace("__D_PAGO__",   j_pago)
    .replace("__D_DEPTO__",  j_depto)
    .replace("__TOTAL_ING__",  str(round(total_ing, 2)))
    .replace("__TOTAL_PED__",  str(int(total_ped)))
    .replace("__TICKET_PROM__",str(round(ticket_prom, 2)))
    .replace("__GAN_TOTAL__",  str(round(gan_total, 2)))
    .replace("__MARGEN_PROM__",str(round(margen_prom, 2)))
    .replace("__DESC_TOTAL__", str(round(desc_total, 2)))
    .replace("__AGOTADOS__",   str(agotados))
    .replace("__CANAL_TOP__",  canal_top)
    .replace("__PAGO_TOP__",   pago_top)
    .replace("__ING_ACT__",    str(round(ing_act, 2)))
    .replace("__MOM_STR__",    mom_str)
    .replace("__MOM_UP__",     "true" if mom_up else "false")
)

with open(OUT_PATH, "w", encoding="utf-8") as f:
    f.write(HTML)

print(f"Dashboard HTML generado en: {OUT_PATH}")
