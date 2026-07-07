-- Ventas por segmento demográfico (segmento, género, departamento)
SELECT
    c.segmento_cliente,
    c.genero,
    c.departamento,
    COUNT(DISTINCT v.venta_id) AS transacciones,
    ROUND(SUM(v.total_venta), 2) AS ventas_totales
FROM fact_ventas v
JOIN dim_cliente c ON v.cliente_key = c.cliente_key
WHERE c.nombre != 'Cliente no registrado'
GROUP BY c.segmento_cliente, c.genero, c.departamento
ORDER BY ventas_totales DESC;
