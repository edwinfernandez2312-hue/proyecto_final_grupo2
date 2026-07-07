-- Top Clientes: Ranking por ingresos y volumen de compra
-- Corrección: excluye clientes sintéticos "Cliente no registrado"
-- y agrupa por cliente_key para no mezclar clientes distintos con el mismo nombre.

SELECT 
    c.cliente_key,
    c.nombre AS nombre_cliente,
    c.segmento_cliente,
    COUNT(DISTINCT f.venta_id) AS frecuencia_compras,
    SUM(f.total_venta) AS total_comprado,
    AVG(f.total_venta) AS ticket_promedio
FROM `proyectofinalg2.proyectofinalG2.fact_ventas` f
JOIN `proyectofinalg2.proyectofinalG2.dim_cliente` c
    ON f.cliente_key = c.cliente_key
WHERE c.nombre != 'Cliente no registrado'
GROUP BY 1, 2, 3
ORDER BY total_comprado DESC