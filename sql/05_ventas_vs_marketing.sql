-- Ventas vs Marketing mensual
-- Corrección: usa t.mes para ordenar cronológicamente.
-- Antes ordenaba por nombre_mes, lo cual puede dar meses incorrectos por orden alfabético.

WITH ventas_mensuales AS (
    SELECT 
        fecha_key,
        SUM(total_venta) AS ingresos_ventas
    FROM `proyectofinalg2.proyectofinalG2.fact_ventas`
    GROUP BY fecha_key
),
marketing_mensual AS (
    SELECT 
        fecha_key,
        SUM(costo) AS inversion_marketing,
        SUM(conversiones) AS total_conversiones
    FROM `proyectofinalg2.proyectofinalG2.fact_marketing`
    GROUP BY fecha_key
)
SELECT 
    t.anio,
    t.mes,
    t.nombre_mes,
    COALESCE(SUM(v.ingresos_ventas), 0) AS ingresos_totales,
    COALESCE(SUM(m.inversion_marketing), 0) AS inversion_total,
    COALESCE(SUM(m.total_conversiones), 0) AS conversiones_marketing
FROM `proyectofinalg2.proyectofinalG2.dim_tiempo` t
LEFT JOIN ventas_mensuales v ON t.fecha_key = v.fecha_key
LEFT JOIN marketing_mensual m ON t.fecha_key = m.fecha_key
WHERE v.ingresos_ventas IS NOT NULL OR m.inversion_marketing IS NOT NULL
GROUP BY 1, 2, 3
ORDER BY t.anio ASC, t.mes ASC;
