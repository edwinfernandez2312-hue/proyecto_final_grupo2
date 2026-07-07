WITH agregacion_movimientos AS (
    SELECT
        producto_key,
        SUM(CASE WHEN tipo_movimiento = 'Entrada' THEN cantidad ELSE 0 END) AS total_entradas,
        SUM(CASE WHEN tipo_movimiento = 'Salida' THEN cantidad ELSE 0 END) AS total_salidas
    FROM `proyectofinalg2.proyectofinalG2.fact_movimientos_inventario`
    GROUP BY producto_key
),

agregacion_existencias AS (
    SELECT
        i.producto_key,
        b.nombre_bodega,
        SUM(i.existencia) AS stock_actual
    FROM `proyectofinalg2.proyectofinalG2.fact_inventario` i
    JOIN `proyectofinalg2.proyectofinalG2.dim_bodega` b 
        ON i.bodega_key = b.bodega_key
    GROUP BY 
        i.producto_key,
        b.nombre_bodega
)

SELECT
    p.nombre_producto,
    p.categoria,
    e.nombre_bodega,
    e.stock_actual,
    COALESCE(m.total_entradas, 0) AS unidades_ingresadas,
    COALESCE(m.total_salidas, 0) AS unidades_retiradas,

    CASE
        WHEN e.stock_actual <= 0 THEN 'Agotado'
        WHEN e.stock_actual <= 10 THEN 'Stock critico'
        WHEN e.stock_actual <= 25 THEN 'Stock bajo'
        ELSE 'Disponible'
    END AS estado_stock

FROM agregacion_existencias e
JOIN `proyectofinalg2.proyectofinalG2.dim_producto` p 
    ON e.producto_key = p.producto_key
LEFT JOIN agregacion_movimientos m 
    ON e.producto_key = m.producto_key
ORDER BY e.stock_actual ASC;