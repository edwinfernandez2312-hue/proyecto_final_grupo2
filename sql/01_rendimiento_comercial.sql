SELECT
    t.anio,
    t.nombre_mes,
    s.nombre_sucursal,
    c.canal_venta,
    p.categoria,
    mp.metodo_pago,
    COUNT(DISTINCT v.venta_id) AS transacciones_totales,
    SUM(v.cantidad) AS unidades_vendidas,
    SUM(v.total_venta) AS ingresos_totales,
    ROUND(SUM(v.descuento), 2) AS descuentos_aplicados
FROM `proyectofinalg2.proyectofinalG2.fact_ventas` v
JOIN `proyectofinalg2.proyectofinalG2.dim_tiempo` t ON v.fecha_key = t.fecha_key
JOIN `proyectofinalg2.proyectofinalG2.dim_sucursal` s ON v.sucursal_key = s.sucursal_key
JOIN `proyectofinalg2.proyectofinalG2.dim_canal` c ON v.canal_key = c.canal_key
JOIN `proyectofinalg2.proyectofinalG2.dim_producto` p ON v.producto_key = p.producto_key
JOIN `proyectofinalg2.proyectofinalG2.dim_metodo_pago` mp ON v.metodo_pago_key = mp.metodo_pago_key
GROUP BY 1, 2, 3, 4, 5, 6
ORDER BY ingresos_totales DESC;
