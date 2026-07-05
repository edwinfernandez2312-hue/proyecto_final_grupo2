SELECT
    t.anio,
    t.nombre_mes,
    c.plataforma,
    SUM(m.impresiones) AS impresiones_totales,
    SUM(m.clics) AS clics_totales,
    SUM(m.costo) AS inversion_total,
    SUM(m.leads) AS leads_generados,
    SUM(m.conversiones) AS conversiones_totales,
    -- Métricas calculadas nativas
    ROUND(SAFE_DIVIDE(SUM(m.clics), SUM(m.impresiones)) * 100, 2) AS click_through_rate_pct,
    ROUND(SAFE_DIVIDE(SUM(m.costo), SUM(m.conversiones)), 2) AS costo_por_conversion
FROM `proyectofinalg2.proyectofinalG2.fact_marketing` m
JOIN `proyectofinalg2.proyectofinalG2.dim_campana` c ON m.campana_key = c.campana_key
JOIN `proyectofinalg2.proyectofinalG2.dim_tiempo` t ON m.fecha_key = t.fecha_key
GROUP BY 1, 2, 3
ORDER BY inversion_total DESC;
