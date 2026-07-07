-- Ventas por canal con participación porcentual
SELECT
    c.canal_venta,
    COUNT(DISTINCT v.venta_id) AS transacciones,
    SUM(v.cantidad) AS unidades,
    ROUND(SUM(v.total_venta), 2) AS ventas_totales,
    ROUND(
        SUM(v.total_venta) * 100.0 / SUM(SUM(v.total_venta)) OVER (),
        2
    ) AS participacion_pct
FROM fact_ventas v
JOIN dim_canal c ON v.canal_key = c.canal_key
GROUP BY c.canal_venta
ORDER BY ventas_totales DESC;
