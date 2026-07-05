SELECT 
    c.departamento,
    c.genero,
    cn.canal_venta,
    mp.metodo_pago,
    COUNT(DISTINCT v.venta_id) AS cantidad_pedidos,
    SUM(v.total_venta) AS ingresos_generados
FROM `proyectofinalg2.proyectofinalG2.fact_ventas` v
JOIN `proyectofinalg2.proyectofinalG2.dim_cliente` c ON v.cliente_key = c.cliente_key
JOIN `proyectofinalg2.proyectofinalG2.dim_canal` cn ON v.canal_key = cn.canal_key
JOIN `proyectofinalg2.proyectofinalG2.dim_metodo_pago` mp ON v.metodo_pago_key = mp.metodo_pago_key
WHERE c.nombre != 'Cliente no registrado'
GROUP BY 1, 2, 3, 4
ORDER BY ingresos_generados DESC;
