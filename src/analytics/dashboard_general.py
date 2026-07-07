"""
dashboard_general.py
Dashboard Ejecutivo General — pandas + matplotlib + matplotlib.ticker
Lee directamente del Data Warehouse SQLite local y exporta un PNG de alta calidad.

Uso:
    cd proyecto_final_grupo2
    python src/analytics/dashboard_general.py
"""

import os
import sqlite3

import matplotlib
matplotlib.use("Agg")  # Sin ventana — solo guarda el PNG

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch

# ─── Rutas ───────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DW_PATH  = os.path.join(BASE_DIR, "data", "datacommerce_dw.db")
OUT_PATH = os.path.join(BASE_DIR, "dashboards", "dashboard_general.png")
os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

# ─── Paleta ──────────────────────────────────────────────────────────────────
BG       = "#0B0F1A"
BG_CARD  = "#141B2D"
BG_CARD2 = "#1A2236"
CYAN     = "#00D4FF"
PURPLE   = "#A855F7"
GREEN    = "#10B981"
AMBER    = "#F59E0B"
ROSE     = "#F43F5E"
INDIGO   = "#6366F1"
TEXT     = "#F3F4F6"
MUTED    = "#6B7280"
GRID     = "#1E2A3A"
ACCENT   = [CYAN, PURPLE, GREEN, AMBER, ROSE, INDIGO, "#EC4899", "#14B8A6",
            "#F97316", "#84CC16", "#06B6D4", "#8B5CF6"]

# ─── Helpers ─────────────────────────────────────────────────────────────────
def query(sql: str) -> pd.DataFrame:
    with sqlite3.connect(DW_PATH) as conn:
        return pd.read_sql_query(sql, conn)

def fmt_money(v: float) -> str:
    if abs(v) >= 1_000_000_000:
        return f"Q{v/1_000_000_000:.2f}B"
    if abs(v) >= 1_000_000:
        return f"Q{v/1_000_000:.1f}M"
    if abs(v) >= 1_000:
        return f"Q{v/1_000:.1f}K"
    return f"Q{v:,.0f}"

def fmt_pct(v: float) -> str:
    return f"{v:+.1f}%" if v != 0 else "0.0%"

def card_bg(ax):
    ax.set_facecolor(BG_CARD)
    for sp in ax.spines.values():
        sp.set_edgecolor(GRID)

def clean_ax(ax, title="", grid_axis="y"):
    card_bg(ax)
    ax.tick_params(colors=MUTED, labelsize=9)
    if title:
        ax.set_title(title, color=TEXT, fontsize=11, fontweight="bold", pad=10)
    if grid_axis == "y":
        ax.yaxis.grid(True, color=GRID, linewidth=0.5, zorder=0)
        ax.set_axisbelow(True)
    elif grid_axis == "x":
        ax.xaxis.grid(True, color=GRID, linewidth=0.5, zorder=0)
        ax.set_axisbelow(True)

# ─── Carga de datos ───────────────────────────────────────────────────────────
print("Cargando datos del Data Warehouse…")

df_canal = query("""
    SELECT dc.canal_venta AS canal,
           SUM(fv.total_venta)  AS ingresos,
           COUNT(fv.venta_id)   AS pedidos
    FROM fact_ventas fv
    JOIN dim_canal dc ON fv.canal_key = dc.canal_key
    GROUP BY canal ORDER BY ingresos DESC
""")

df_mens = query("""
    SELECT dt.anio, dt.mes, dt.nombre_mes,
           SUM(fv.total_venta)  AS ingresos,
           SUM(fv.descuento)    AS descuentos,
           COUNT(fv.venta_id)   AS transacciones
    FROM fact_ventas fv
    JOIN dim_tiempo dt ON fv.fecha_key = dt.fecha_key
    GROUP BY dt.anio, dt.mes, dt.nombre_mes
    ORDER BY dt.anio, dt.mes
""")
df_mens["label"] = df_mens["nombre_mes"].str[:3] + "'" + df_mens["anio"].astype(str).str[-2:]

df_rent = query("""
    SELECT dp.nombre_producto, dp.categoria,
           SUM(fv.total_venta)                              AS ingresos,
           SUM(fv.cantidad * dp.costo_unitario)             AS costos,
           SUM(fv.total_venta)-SUM(fv.cantidad*dp.costo_unitario) AS ganancia,
           SUM(fv.descuento)   AS descuentos,
           SUM(fv.cantidad)    AS unidades
    FROM fact_ventas fv
    JOIN dim_producto dp ON fv.producto_key = dp.producto_key
    GROUP BY dp.nombre_producto, dp.categoria
    ORDER BY ganancia DESC LIMIT 10
""")
df_rent["margen_pct"] = (
    df_rent["ganancia"] / df_rent["ingresos"].replace(0, np.nan) * 100
).fillna(0).round(1)

df_cli = query("""
    SELECT dc.nombre AS cliente, dc.segmento_cliente AS segmento,
           SUM(fv.total_venta) AS total, COUNT(fv.venta_id) AS pedidos
    FROM fact_ventas fv
    JOIN dim_cliente dc ON fv.cliente_key = dc.cliente_key
    WHERE dc.nombre != 'Cliente no registrado'
    GROUP BY dc.nombre, dc.segmento_cliente
    ORDER BY total DESC LIMIT 5
""")

df_inv = query("""
    SELECT dp.nombre_producto, db.nombre_bodega,
           fi.existencia AS stock_actual,
           COALESCE(sal.salidas,0) AS salidas
    FROM fact_inventario fi
    JOIN dim_producto dp ON fi.producto_key = dp.producto_key
    JOIN dim_bodega   db ON fi.bodega_key   = db.bodega_key
    LEFT JOIN (
        SELECT producto_key, SUM(cantidad) AS salidas
        FROM fact_movimientos_inventario
        WHERE tipo_movimiento='Salida' GROUP BY producto_key
    ) sal ON fi.producto_key = sal.producto_key
    ORDER BY fi.existencia ASC LIMIT 8
""")

df_pago = query("""
    SELECT dmp.metodo_pago AS metodo,
           COUNT(fv.venta_id)   AS pedidos,
           SUM(fv.total_venta)  AS ingresos
    FROM fact_ventas fv
    JOIN dim_metodo_pago dmp ON fv.metodo_pago_key = dmp.metodo_pago_key
    GROUP BY metodo ORDER BY pedidos DESC LIMIT 8
""")

# ─── KPIs ────────────────────────────────────────────────────────────────────
total_ingresos  = float(df_canal["ingresos"].sum())
total_pedidos   = float(df_canal["pedidos"].sum())
ticket_prom     = total_ingresos / total_pedidos if total_pedidos else 0.0
ganancia_total  = float(df_rent["ganancia"].sum())
margen_prom     = float(df_rent["margen_pct"].mean()) if not df_rent.empty else 0.0
desc_total      = float(df_mens["descuentos"].sum())
prod_agotados   = int(query("SELECT COUNT(*) n FROM fact_inventario WHERE existencia=0").iloc[0]["n"])
canal_top       = df_canal.iloc[0]["canal"] if not df_canal.empty else "—"
pago_top        = df_pago.iloc[0]["metodo"]  if not df_pago.empty else "—"
ingresos_act    = float(df_mens.iloc[-1]["ingresos"]) if not df_mens.empty else 0.0
ingresos_ant    = float(df_mens.iloc[-2]["ingresos"]) if len(df_mens) >= 2 else 0.0
crecimiento_mom = ((ingresos_act - ingresos_ant) / ingresos_ant * 100) if ingresos_ant else 0.0

print("Datos OK. Construyendo figura…")

# ─── Configuración global de matplotlib ──────────────────────────────────────
plt.rcParams.update({
    "font.family":     "DejaVu Sans",
    "text.color":      TEXT,
    "axes.labelcolor": MUTED,
    "xtick.color":     MUTED,
    "ytick.color":     MUTED,
    "figure.facecolor": BG,
})

# ─── Figura principal: altura mayor, layout más espaciado ────────────────────
fig = plt.figure(figsize=(30, 24), facecolor=BG)

# Grid principal: 5 filas, proporciones de altura definidas
gs = gridspec.GridSpec(
    5, 1,
    figure=fig,
    height_ratios=[0.9, 3.5, 3.5, 3.5, 1.2],
    hspace=0.55,
    left=0.03, right=0.97,
    top=0.94, bottom=0.04
)

# Fila 0: cabecera KPI (6 columnas)
gs0 = gridspec.GridSpecFromSubplotSpec(1, 6, subplot_spec=gs[0], wspace=0.30)
# Fila 1: ventas mensuales (7 cols) + dona canal (5 cols)
gs1 = gridspec.GridSpecFromSubplotSpec(1, 12, subplot_spec=gs[1], wspace=0.35)
# Fila 2: rentabilidad (8 cols) + pagos (4 cols)
gs2 = gridspec.GridSpecFromSubplotSpec(1, 12, subplot_spec=gs[2], wspace=0.35)
# Fila 3: inventario (6 cols) + tabla clientes (6 cols)
gs3 = gridspec.GridSpecFromSubplotSpec(1, 12, subplot_spec=gs[3], wspace=0.40)
# Fila 4: resumen ejecutivo full width
gs4 = gridspec.GridSpecFromSubplotSpec(1, 1, subplot_spec=gs[4])

# ─── Título ───────────────────────────────────────────────────────────────────
fig.text(0.5, 0.969, "DataCommerce GT  —  Dashboard General de Inteligencia de Negocio",
         ha="center", fontsize=23, fontweight="bold", color=TEXT)
fig.text(0.5, 0.953,
         "KPIs  ·  Ventas Mensuales  ·  Rentabilidad  ·  Canales  ·  Inventario  ·  Clientes  "
         "|  Fuente: datacommerce_dw.db (SQLite Local)",
         ha="center", fontsize=10.5, color=MUTED)

# ════════════════════════════════════════════════════════════════════════════
# FILA 0 — TARJETAS KPI
# ════════════════════════════════════════════════════════════════════════════
KPI_CARDS = [
    ("INGRESOS TOTALES",     fmt_money(total_ingresos),  f"Ult. mes: {fmt_money(ingresos_act)}",         CYAN),
    ("CRECIMIENTO MoM",      fmt_pct(crecimiento_mom),   "Variación mes anterior vs actual",              GREEN if crecimiento_mom >= 0 else ROSE),
    ("TICKET PROMEDIO",      fmt_money(ticket_prom),     f"{int(total_pedidos):,} transacciones",         PURPLE),
    ("MARGEN RENTABILIDAD",  f"{margen_prom:.1f}%",      f"Utilidad top10: {fmt_money(ganancia_total)}",  AMBER),
    ("PROD. AGOTADOS",       str(prod_agotados),         "Requieren reabastecimiento urgente",            ROSE),
    ("DESCUENTOS CEDIDOS",   fmt_money(desc_total),      f"Canal estrella: {canal_top}",                  INDIGO),
]

for i, (titulo, valor, sub, color) in enumerate(KPI_CARDS):
    ax = fig.add_subplot(gs0[0, i])
    ax.set_facecolor(BG_CARD); ax.axis("off")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)

    ax.add_patch(FancyBboxPatch(
        (0.04, 0.06), 0.92, 0.88,
        boxstyle="round,pad=0.03",
        linewidth=2, edgecolor=color,
        facecolor=BG_CARD, transform=ax.transAxes, zorder=0
    ))
    ax.text(0.5, 0.86, titulo, ha="center", va="center",
            fontsize=8, color=MUTED, fontweight="bold", transform=ax.transAxes)
    ax.text(0.5, 0.58, valor,  ha="center", va="center",
            fontsize=19, color=color, fontweight="bold", transform=ax.transAxes)
    ax.text(0.5, 0.22, sub,    ha="center", va="center",
            fontsize=8, color=MUTED, transform=ax.transAxes, wrap=True)
    ax.axhline(0.11, xmin=0.08, xmax=0.92, color=color, linewidth=1.5, alpha=0.4)

# ════════════════════════════════════════════════════════════════════════════
# FILA 1 — Ventas mensuales [0:8] + Dona canal [8:12]
# ════════════════════════════════════════════════════════════════════════════

# ── Ventas mensuales ──────────────────────────────────────────────────────────
ax_m = fig.add_subplot(gs1[0, :8])
clean_ax(ax_m, "Ingresos Mensuales vs Volumen de Transacciones (últimos 24 meses)")

df_p = df_mens.tail(24).reset_index(drop=True)
x    = np.arange(len(df_p))

ax_m.bar(x, df_p["ingresos"], color=CYAN, alpha=0.80, width=0.65, zorder=3)
ax_m.set_ylabel("Ingresos", color=CYAN, fontsize=10)
ax_m.tick_params(axis="y", colors=CYAN, labelsize=9)
ax_m.spines["left"].set_color(CYAN)
ax_m.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: fmt_money(v)))
ax_m.set_xticks(x)
ax_m.set_xticklabels(df_p["label"], rotation=45, ha="right", fontsize=8.5, color=MUTED)

ax_m2 = ax_m.twinx()
ax_m2.plot(x, df_p["transacciones"], color=PURPLE, linewidth=2.5,
           marker="o", markersize=5, zorder=5)
ax_m2.set_ylabel("Transacciones", color=PURPLE, fontsize=10)
ax_m2.tick_params(axis="y", colors=PURPLE, labelsize=9)
ax_m2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
ax_m2.spines["right"].set_color(PURPLE)
ax_m2.spines["left"].set_color(CYAN)

handles = [
    plt.Rectangle((0, 0), 1, 1, color=CYAN,   label="Ingresos por Ventas"),
    plt.Line2D([0], [0], color=PURPLE, lw=2.5, marker="o", ms=5, label="Transacciones"),
]
ax_m.legend(handles=handles, facecolor=BG_CARD2, edgecolor=GRID,
            labelcolor=TEXT, fontsize=9, loc="upper left")

# ── Dona por canal ────────────────────────────────────────────────────────────
ax_d = fig.add_subplot(gs1[0, 8:])
ax_d.set_facecolor(BG_CARD)
ax_d.set_title("Participación por Canal de Venta",
               color=TEXT, fontsize=11, fontweight="bold", pad=14)

# Colores y etiquetas
colores_dona = ACCENT[:len(df_canal)]
pct_vals     = df_canal["ingresos"] / df_canal["ingresos"].sum() * 100

wedges, _, autotexts = ax_d.pie(
    df_canal["ingresos"],
    autopct="%1.1f%%",
    colors=colores_dona,
    startangle=140,
    pctdistance=0.72,
    wedgeprops=dict(width=0.52, edgecolor=BG, linewidth=2.5),
    textprops=dict(fontsize=8.5)
)
for at in autotexts:
    at.set_color(TEXT)
    at.set_fontweight("bold")

# Leyenda fuera de la dona, con monto y %
leyenda_labels = [
    f"{r['canal']}  —  {fmt_money(r['ingresos'])}  ({pct:.1f}%)"
    for (_, r), pct in zip(df_canal.iterrows(), pct_vals)
]
ax_d.legend(
    wedges, leyenda_labels,
    loc="lower center",
    bbox_to_anchor=(0.5, -0.30),
    facecolor=BG_CARD2, edgecolor=GRID,
    labelcolor=MUTED, fontsize=8,
    ncol=2, framealpha=0.9
)

# ════════════════════════════════════════════════════════════════════════════
# FILA 2 — Top10 Rentabilidad [0:8] + Métodos de Pago [8:12]
# ════════════════════════════════════════════════════════════════════════════

# ── Rentabilidad ──────────────────────────────────────────────────────────────
ax_r = fig.add_subplot(gs2[0, :8])
clean_ax(ax_r, "Top 10 Productos · Ganancia Neta y Margen de Rentabilidad (%)", grid_axis="x")

df_rs = df_rent.sort_values("ganancia", ascending=True)
y_pos = np.arange(len(df_rs))

bars_r = ax_r.barh(y_pos, df_rs["ganancia"], color=PURPLE, alpha=0.85,
                    height=0.62, zorder=3)

for bar, (_, row) in zip(bars_r, df_rs.iterrows()):
    w = bar.get_width()
    ax_r.text(
        w + df_rs["ganancia"].max() * 0.008,
        bar.get_y() + bar.get_height() / 2,
        f"  {fmt_money(w)}  |  {row['margen_pct']:.1f}%",
        va="center", ha="left", fontsize=8.5, color=MUTED
    )

ax_r.set_yticks(y_pos)
ax_r.set_yticklabels(
    [n[:38] for n in df_rs["nombre_producto"]],
    fontsize=9, color=TEXT
)
ax_r.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: fmt_money(v)))
ax_r.tick_params(axis="x", colors=MUTED, labelsize=9)
ax_r.set_xlim(right=df_rs["ganancia"].max() * 1.28)

# ── Métodos de pago ────────────────────────────────────────────────────────────
ax_pg = fig.add_subplot(gs2[0, 8:])
clean_ax(ax_pg, "Métodos de Pago\n(% de transacciones)")

df_pg       = df_pago
x_pg        = np.arange(len(df_pg))
total_ped   = float(df_pg["pedidos"].sum())
colores_pg  = ACCENT[:len(df_pg)]

bars_pg = ax_pg.bar(x_pg, df_pg["pedidos"], color=colores_pg,
                     alpha=0.90, width=0.65, zorder=3)

for bar, ped in zip(bars_pg, df_pg["pedidos"]):
    pct = ped / total_ped * 100
    ax_pg.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + total_ped * 0.006,
        f"{pct:.1f}%",
        ha="center", va="bottom", fontsize=9, color=TEXT, fontweight="bold"
    )

ax_pg.set_xticks(x_pg)
ax_pg.set_xticklabels(df_pg["metodo"], rotation=32, ha="right", fontsize=8.5, color=MUTED)
ax_pg.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
ax_pg.tick_params(axis="y", colors=MUTED, labelsize=9)

# ════════════════════════════════════════════════════════════════════════════
# FILA 3 — Inventario crítico [0:6] + Tabla VIP [6:12]
# ════════════════════════════════════════════════════════════════════════════

# ── Inventario crítico ────────────────────────────────────────────────────────
ax_iv = fig.add_subplot(gs3[0, :6])
clean_ax(ax_iv, "Inventario Crítico · Stock Actual vs Unidades Despachadas", grid_axis="x")

df_iv = df_inv.sort_values("stock_actual", ascending=True)
y_iv  = np.arange(len(df_iv))
hw    = 0.36
max_v = max(float(df_iv["stock_actual"].max()), float(df_iv["salidas"].max()), 1)

ax_iv.barh(y_iv - hw/2, df_iv["stock_actual"], height=hw,
            color=CYAN,  alpha=0.85, label="Stock Actual",      zorder=3)
ax_iv.barh(y_iv + hw/2, df_iv["salidas"],       height=hw,
            color=AMBER, alpha=0.85, label="Unidades Salidas",   zorder=3)

for i, (st, sa) in enumerate(zip(df_iv["stock_actual"], df_iv["salidas"])):
    c = ROSE if st == 0 else MUTED
    ax_iv.text(st + max_v * 0.01, i - hw/2, f"{int(st):,}", va="center", fontsize=8, color=c)
    ax_iv.text(sa + max_v * 0.01, i + hw/2, f"{int(sa):,}", va="center", fontsize=8, color=MUTED)

ax_iv.set_yticks(y_iv)
ax_iv.set_yticklabels([n[:30] for n in df_iv["nombre_producto"]], fontsize=9, color=TEXT)
ax_iv.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
ax_iv.tick_params(axis="x", colors=MUTED, labelsize=9)
ax_iv.set_xlim(right=max_v * 1.22)
ax_iv.legend(facecolor=BG_CARD2, edgecolor=GRID, labelcolor=TEXT, fontsize=9, loc="lower right")

# ── Tabla VIP ─────────────────────────────────────────────────────────────────
ax_cl = fig.add_subplot(gs3[0, 6:])
ax_cl.set_facecolor(BG_CARD); ax_cl.axis("off")
ax_cl.set_title("Top 5 Clientes VIP", color=TEXT, fontsize=12,
                 fontweight="bold", pad=12, loc="left", x=0.03)

# Encabezados
hdrs  = ["#", "Cliente",      "Segmento",  "Pedidos", "Total Comprado", "% del Total"]
hx    = [0.02, 0.10, 0.42,   0.60,         0.73,       0.90]
hclrs = [MUTED, PURPLE, PURPLE, PURPLE,    PURPLE,     PURPLE]

ax_cl.axhline(0.87, xmin=0.01, xmax=0.99, color=PURPLE, linewidth=1.5, alpha=0.7)
for cx, h, hc in zip(hx, hdrs, hclrs):
    ax_cl.text(cx, 0.90, h, fontsize=9.5, color=hc,
               fontweight="bold", transform=ax_cl.transAxes, va="center")
ax_cl.axhline(0.85, xmin=0.01, xmax=0.99, color=GRID, linewidth=0.8)

gran     = float(df_cli["total"].sum())
row_bgs  = [BG_CARD, BG_CARD2]

for i, row in df_cli.reset_index(drop=True).iterrows():
    pct  = row["total"] / gran * 100 if gran else 0
    yr   = 0.73 - i * 0.155

    ax_cl.add_patch(FancyBboxPatch(
        (0.01, yr - 0.055), 0.98, 0.13,
        boxstyle="round,pad=0.01", linewidth=0,
        facecolor=row_bgs[i % 2],
        transform=ax_cl.transAxes, zorder=0
    ))

    vals  = [str(i+1), row["cliente"][:24], row["segmento"],
             f"{int(row['pedidos']):,}", fmt_money(row["total"]), f"{pct:.1f}%"]
    vclrs = [MUTED, TEXT, CYAN, MUTED, GREEN, AMBER]

    for cx, val, vc in zip(hx, vals, vclrs):
        ax_cl.text(cx, yr, val, fontsize=9.5, color=vc,
                   transform=ax_cl.transAxes, va="center")

    # Separador
    ax_cl.axhline(yr - 0.06, xmin=0.01, xmax=0.99, color=GRID, linewidth=0.5, alpha=0.5)

# ════════════════════════════════════════════════════════════════════════════
# FILA 4 — Banda de resumen ejecutivo
# ════════════════════════════════════════════════════════════════════════════
ax_res = fig.add_subplot(gs4[0])
ax_res.set_facecolor(BG_CARD2); ax_res.axis("off")
ax_res.axhline(0.95, xmin=0.01, xmax=0.99, color=CYAN, linewidth=1, alpha=0.45)
ax_res.axhline(0.05, xmin=0.01, xmax=0.99, color=CYAN, linewidth=1, alpha=0.45)

SUMMARY = [
    ("INGRESOS TOTALES",    fmt_money(total_ingresos),   CYAN),
    ("TICKET PROMEDIO",     fmt_money(ticket_prom),      PURPLE),
    ("CRECIMIENTO MoM",     fmt_pct(crecimiento_mom),    GREEN if crecimiento_mom >= 0 else ROSE),
    ("MARGEN PROMEDIO",     f"{margen_prom:.2f}%",        AMBER),
    ("UTILIDAD NETA (T10)", fmt_money(ganancia_total),   GREEN),
    ("CANAL ESTRELLA",      canal_top,                   CYAN),
    ("PAGO FAVORITO",       pago_top,                    PURPLE),
    ("DESCUENTOS",          fmt_money(desc_total),        AMBER),
    ("PROD. AGOTADOS",      str(prod_agotados),           ROSE),
    ("TRANSACCIONES",       f"{int(total_pedidos):,}",   GREEN),
]

n_s = len(SUMMARY)
dx  = 1.0 / n_s

for i, (tit, val, clr) in enumerate(SUMMARY):
    xc = dx * i + dx / 2
    ax_res.text(xc, 0.78, tit, ha="center", va="center",
                fontsize=8, color=MUTED, fontweight="bold",
                transform=ax_res.transAxes)
    ax_res.text(xc, 0.38, val, ha="center", va="center",
                fontsize=15, color=clr, fontweight="bold",
                transform=ax_res.transAxes)
    if i < n_s - 1:
        ax_res.axvline(dx * (i+1), ymin=0.08, ymax=0.92,
                       color=GRID, linewidth=0.8)

ax_res.text(0.5, -0.12,
            "Generado por el Pipeline DataCommerce GT  |  Fuente: datacommerce_dw.db (SQLite)  |  "
            "python src/analytics/dashboard_general.py",
            ha="center", fontsize=8, color=MUTED, transform=ax_res.transAxes)

# ─── Guardar ──────────────────────────────────────────────────────────────────
plt.savefig(OUT_PATH, dpi=160, bbox_inches="tight",
            facecolor=BG, edgecolor="none")
print(f"Dashboard General guardado en: {OUT_PATH}")
plt.close("all")
