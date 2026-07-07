-- KPIs globales consolidados (SQLite / BigQuery compatible)
SELECT
    COUNT(DISTINCT v.venta_id) AS numero_ventas,
    SUM(v.cantidad) AS productos_vendidos,
    ROUND(SUM(v.total_venta), 2) AS ventas_totales,
    ROUND(AVG(v.total_venta), 2) AS ticket_promedio,
    ROUND(SUM(v.descuento), 2) AS descuentos_otorgados,
    ROUND(AVG(v.descuento), 2) AS descuento_promedio,
    ROUND(MAX(v.total_venta), 2) AS venta_maxima,
    ROUND(MIN(v.total_venta), 2) AS venta_minima
FROM fact_ventas v;
