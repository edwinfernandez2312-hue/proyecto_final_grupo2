-- Ventas por sucursal con participación
SELECT
    s.nombre_sucursal,
    COUNT(DISTINCT v.venta_id) AS transacciones,
    ROUND(SUM(v.total_venta), 2) AS ventas_totales,
    ROUND(
        SUM(v.total_venta) * 100.0 / SUM(SUM(v.total_venta)) OVER (),
        2
    ) AS participacion_pct
FROM fact_ventas v
JOIN dim_sucursal s ON v.sucursal_key = s.sucursal_key
GROUP BY s.nombre_sucursal
ORDER BY ventas_totales DESC;
