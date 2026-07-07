SELECT
    t.anio,
    t.nombre_mes,
    c.plataforma,
    SUM(m.impresiones) AS impresiones_totales,
    SUM(m.clics) AS clics_totales,
    SUM(m.costo) AS inversion_total,
    SUM(m.leads) AS leads_generados,
    SUM(m.conversiones) AS conversiones_totales,

    -- CTR = clics / impresiones * 100
    ROUND(
        (SUM(m.clics) * 1.0 / NULLIF(SUM(m.impresiones), 0)) * 100,
        2
    ) AS click_through_rate_pct,

    -- Costo por conversión = inversión / conversiones
    ROUND(
        SUM(m.costo) * 1.0 / NULLIF(SUM(m.conversiones), 0),
        2
    ) AS costo_por_conversion

FROM fact_marketing m
JOIN dim_campana c 
    ON m.campana_key = c.campana_key
JOIN dim_tiempo t 
    ON m.fecha_key = t.fecha_key
GROUP BY 
    t.anio,
    t.nombre_mes,
    c.plataforma
ORDER BY inversion_total DESC;