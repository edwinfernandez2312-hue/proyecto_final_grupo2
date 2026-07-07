SELECT 
    p.categoria,
    p.nombre_producto,
    SUM(v.cantidad) AS volumen_vendido,
    SUM(v.total_venta) AS ingresos_brutos,
    SUM(v.descuento) AS dinero_cedido_en_descuentos,
    SUM(v.cantidad * p.costo_unitario) AS costo_bienes_vendidos,

    -- Ganancia neta = ingresos - costos
    SUM(v.total_venta) - SUM(v.cantidad * p.costo_unitario) AS ganancia_neta,

    -- Margen de rentabilidad = ganancia / ingresos * 100
    ROUND(
        (
            (SUM(v.total_venta) - SUM(v.cantidad * p.costo_unitario)) * 1.0
            / NULLIF(SUM(v.total_venta), 0)
        ) * 100,
        2
    ) AS margen_rentabilidad_pct

FROM fact_ventas v
JOIN dim_producto p 
    ON v.producto_key = p.producto_key
GROUP BY 
    p.categoria,
    p.nombre_producto
ORDER BY ganancia_neta DESC;