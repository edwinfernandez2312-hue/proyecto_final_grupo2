-- Ventas diarias en el tiempo
SELECT
    t.fecha,
    t.anio,
    t.nombre_mes,
    COUNT(DISTINCT v.venta_id) AS transacciones,
    ROUND(SUM(v.total_venta), 2) AS ventas_diarias
FROM fact_ventas v
JOIN dim_tiempo t ON v.fecha_key = t.fecha_key
GROUP BY t.fecha, t.anio, t.nombre_mes
ORDER BY t.fecha;
