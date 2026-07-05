SELECT 
    p.categoria,
    p.nombre_producto,
    SUM(v.cantidad) AS volumen_vendido,
    SUM(v.total_venta) AS ingresos_brutos,
    SUM(v.descuento) AS dinero_cedido_en_descuentos,
    SUM(v.cantidad * p.costo_unitario) AS costo_bienes_vendidos,
    -- Cálculo del margen de ganancia (Ingresos - Costos)
    (SUM(v.total_venta) - SUM(v.cantidad * p.costo_unitario)) AS ganancia_neta,
    -- Porcentaje de rentabilidad
    ROUND(SAFE_DIVIDE((SUM(v.total_venta) - SUM(v.cantidad * p.costo_unitario)), SUM(v.total_venta)) * 100, 2) AS margen_rentabilidad_pct
FROM `proyectofinalg2.proyectofinalG2.fact_ventas` v
JOIN `proyectofinalg2.proyectofinalG2.dim_producto` p ON v.producto_key = p.producto_key
GROUP BY 1, 2
ORDER BY ganancia_neta DESC;
