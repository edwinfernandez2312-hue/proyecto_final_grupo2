-- Top Clientes: Ranking por ingresos y volumen de compra
SELECT 
    c.nombre AS nombre_cliente,
    c.segmento_cliente,
    COUNT(f.total_venta) AS frecuencia_compras,
    SUM(f.total_venta) AS total_comprado,
    AVG(f.total_venta) AS ticket_promedio
FROM `proyectofinalg2.proyectofinalG2.fact_ventas` f
JOIN `proyectofinalg2.proyectofinalG2.dim_cliente` c
    ON f.cliente_key = c.cliente_key
GROUP BY 1, 2
ORDER BY total_comprado DESC
LIMIT 10;