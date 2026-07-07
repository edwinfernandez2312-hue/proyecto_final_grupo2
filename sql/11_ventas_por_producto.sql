-- Ventas por categoría y ranking de productos
SELECT
    p.categoria,
    p.subcategoria,
    p.marca,
    p.nombre_producto,
    SUM(v.cantidad) AS unidades_vendidas,
    ROUND(SUM(v.total_venta), 2) AS ventas_totales,
    ROUND(AVG(v.precio_unitario), 2) AS precio_promedio
FROM fact_ventas v
JOIN dim_producto p ON v.producto_key = p.producto_key
GROUP BY p.categoria, p.subcategoria, p.marca, p.nombre_producto
ORDER BY ventas_totales DESC;
