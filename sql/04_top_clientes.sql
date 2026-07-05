
SELECT 
    c.nombre,
    c.segmento_cliente,
    c.municipio,
    COUNT(DISTINCT v.venta_id) AS frecuencia_compras,
    SUM(v.cantidad) AS total_articulos_comprados,
    SUM(v.total_venta) AS valor_total_cliente
FROM `proyectofinalg2.proyectofinalG2.fact_ventas` v
JOIN `proyectofinalg2.proyectofinalG2.dim_cliente` c ON v.cliente_key = c.cliente_key
WHERE c.nombre != 'Cliente no registrado'
GROUP BY 1, 2, 3
ORDER BY valor_total_cliente DESC
LIMIT 10;
