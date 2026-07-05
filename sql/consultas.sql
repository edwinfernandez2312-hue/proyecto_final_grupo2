-- =====================================================
-- PROYECTO FINAL INTEGRADOR
-- INGENIERÍA DE DATOS
--  - CONSULTAS SQL ANALÍTICAS
-- =====================================================

-- =====================================================
-- Consulta 1: Visualizar registros de la tabla de ventas
-- Objetivo:
-- Verificar la estructura y contenido de la tabla fact_ventas.
-- =====================================================

SELECT *
FROM `proyectofinalg2.proyectofinalG2.fact_ventas`
LIMIT 10;

-- =====================================================
-- Consulta 2: Ventas totales
-- Objetivo:
-- Calcular el monto total de ventas realizadas por la empresa.
-- KPI: Ventas Totales
-- =====================================================

SELECT
    SUM(total_venta) AS ventas_totales
FROM `proyectofinalg2.proyectofinalG2.fact_ventas`;

-- =====================================================
-- Consulta 3: Ticket promedio por venta
-- Objetivo:
-- Calcular el valor promedio de cada venta realizada.
-- KPI: Ticket Promedio
-- =====================================================

SELECT
    AVG(total_venta) AS ticket_promedio
FROM `proyectofinalg2.proyectofinalG2.fact_ventas`;

-- =====================================================
-- Consulta 4: Total de productos vendidos
-- Objetivo:
-- Conocer la cantidad total de productos vendidos.
-- KPI: Productos Vendidos
-- =====================================================

SELECT
    SUM(cantidad) AS productos_vendidos
FROM `proyectofinalg2.proyectofinalG2.fact_ventas`;

-- =====================================================
-- Consulta 5: Ventas por canal de venta
-- Objetivo:
-- Identificar cuál canal genera el mayor volumen de ventas.
-- KPI: Ventas por canal
-- =====================================================

SELECT
    c.canal_venta,
    SUM(f.total_venta) AS ventas_totales
FROM `proyectofinalg2.proyectofinalG2.fact_ventas` f
JOIN `proyectofinalg2.proyectofinalG2.dim_canal` c
    ON f.canal_key = c.canal_key
GROUP BY c.canal_venta
ORDER BY ventas_totales DESC;

-- =====================================================
-- Consulta 6: Ventas por sucursal
-- Objetivo:
-- Determinar cuál sucursal genera mayores ingresos.
-- KPI: Ventas por sucursal
-- =====================================================

SELECT
    s.nombre_sucursal,
    SUM(f.total_venta) AS ventas_totales
FROM `proyectofinalg2.proyectofinalG2.fact_ventas` f
JOIN `proyectofinalg2.proyectofinalG2.dim_sucursal` s
    ON f.sucursal_key = s.sucursal_key
GROUP BY s.nombre_sucursal
ORDER BY ventas_totales DESC;

-- =====================================================
-- Consulta 7: Ventas por categoría de producto
-- Objetivo:
-- Identificar qué categoría de productos genera mayores ingresos.
-- KPI: Ventas por categoría
-- =====================================================

SELECT
    p.categoria,
    SUM(f.total_venta) AS ventas_totales
FROM `proyectofinalg2.proyectofinalG2.fact_ventas` f
JOIN `proyectofinalg2.proyectofinalG2.dim_producto` p
    ON f.producto_key = p.producto_key
GROUP BY p.categoria
ORDER BY ventas_totales DESC;

-- =====================================================
-- Consulta 8: Productos más vendidos
-- Objetivo:
-- Identificar los productos con mayor cantidad de unidades vendidas.
-- KPI: Ranking de productos
-- =====================================================

SELECT
    p.nombre_producto,
    SUM(f.cantidad) AS unidades_vendidas
FROM `proyectofinalg2.proyectofinalG2.fact_ventas` f
JOIN `proyectofinalg2.proyectofinalG2.dim_producto` p
    ON f.producto_key = p.producto_key
GROUP BY p.nombre_producto
ORDER BY unidades_vendidas DESC;

-- =====================================================
-- Consulta 9: Ventas por marca
-- Objetivo:
-- Determinar qué marca genera mayores ingresos.
-- KPI: Ventas por marca
-- =====================================================

SELECT
    p.marca,
    SUM(f.total_venta) AS ventas_totales
FROM `proyectofinalg2.proyectofinalG2.fact_ventas` f
JOIN `proyectofinalg2.proyectofinalG2.dim_producto` p
ON f.producto_key = p.producto_key
GROUP BY p.marca
ORDER BY ventas_totales DESC;

-- =====================================================
-- Consulta 10: Ventas por subcategoría
-- Objetivo:
-- Identificar qué subcategoría de productos genera mayores ingresos.
-- KPI: Ventas por subcategoría
-- =====================================================

SELECT
    p.subcategoria,
    SUM(f.total_venta) AS ventas_totales
FROM `proyectofinalg2.proyectofinalG2.fact_ventas` f
JOIN `proyectofinalg2.proyectofinalG2.dim_producto` p
    ON f.producto_key = p.producto_key
GROUP BY p.subcategoria
ORDER BY ventas_totales DESC;

-- =====================================================
-- Consulta 11: Total de descuentos otorgados
-- Objetivo:
-- Calcular el monto total de descuentos aplicados.
-- KPI: Descuentos otorgados
-- =====================================================

SELECT
    SUM(descuento) AS descuentos_otorgados
FROM `proyectofinalg2.proyectofinalG2.fact_ventas`;

-- =====================================================
-- Consulta 12: Número total de ventas
-- Objetivo:
-- Contabilizar la cantidad total de ventas registradas.
-- KPI: Número de ventas
-- =====================================================

SELECT
    COUNT(*) AS numero_ventas
FROM `proyectofinalg2.proyectofinalG2.fact_ventas`;

-- =====================================================
-- Consulta 13: Venta de mayor valor
-- Objetivo:
-- Identificar la venta con el monto más alto.
-- KPI: Venta máxima
-- =====================================================

SELECT
    MAX(total_venta) AS venta_mas_alta
FROM `proyectofinalg2.proyectofinalG2.fact_ventas`;

-- =====================================================
-- Consulta 14: Venta de menor valor
-- Objetivo:
-- Identificar la venta con el monto más bajo.
-- KPI: Venta mínima
-- =====================================================

SELECT
    MIN(total_venta) AS venta_mas_baja
FROM `proyectofinalg2.proyectofinalG2.fact_ventas`;

-- =====================================================
-- Consulta 15: Descuento promedio por venta
-- Objetivo:
-- Calcular el descuento promedio aplicado a las ventas.
-- KPI: Descuento promedio
-- =====================================================

SELECT
    AVG(descuento) AS descuento_promedio
FROM `proyectofinalg2.proyectofinalG2.fact_ventas`;

-- =====================================================
-- Consulta 16: Comparación entre ventas y descuentos
-- Objetivo:
-- Comparar el total vendido con el total descontado.
-- KPI: Ventas vs descuentos
-- =====================================================

SELECT
    SUM(descuento) AS total_descuentos,
    SUM(total_venta) AS total_ventas
FROM `proyectofinalg2.proyectofinalG2.fact_ventas`;

-- =====================================================
-- Consulta 17: Ventas por fecha
-- Objetivo:
-- Analizar el comportamiento de las ventas a lo largo del tiempo.
-- KPI: Ventas diarias
-- =====================================================

SELECT
    t.fecha,
    SUM(f.total_venta) AS ventas
FROM `proyectofinalg2.proyectofinalG2.fact_ventas` f
JOIN `proyectofinalg2.proyectofinalG2.dim_tiempo` t
    ON f.fecha_key = t.fecha_key
GROUP BY t.fecha
ORDER BY t.fecha;

-- =====================================================
-- Consulta 18: Clientes con mayor monto de compra
-- Objetivo:
-- Identificar los clientes que generan mayores ingresos.
-- KPI: Top clientes
-- =====================================================

SELECT
    c.nombre,
    SUM(f.total_venta) AS total_comprado
FROM `proyectofinalg2.proyectofinalG2.fact_ventas` f
JOIN `proyectofinalg2.proyectofinalG2.dim_cliente` c
    ON f.cliente_key = c.cliente_key
GROUP BY c.nombre
ORDER BY total_comprado DESC;

-- =====================================================
-- Consulta 19: Participación de ventas por canal
-- Objetivo:
-- Calcular qué porcentaje de las ventas representa cada canal.
-- KPI: Participación por canal
-- =====================================================

SELECT
    c.canal_venta,
    SUM(f.total_venta) AS ventas,
    ROUND(
        SUM(f.total_venta) * 100 /
        SUM(SUM(f.total_venta)) OVER (),
        2
    ) AS porcentaje
FROM `proyectofinalg2.proyectofinalG2.fact_ventas` f
JOIN `proyectofinalg2.proyectofinalG2.dim_canal` c
ON f.canal_key = c.canal_key
GROUP BY c.canal_venta
ORDER BY ventas DESC;

-- =====================================================
-- Consulta 20: Participación de ventas por sucursal
-- Objetivo:
-- Calcular el porcentaje de ventas por sucursal.
-- KPI: Participación por sucursal
-- =====================================================

SELECT
    s.nombre_sucursal,
    SUM(f.total_venta) AS ventas,
    ROUND(
        SUM(f.total_venta) * 100 /
        SUM(SUM(f.total_venta)) OVER (),
        2
    ) AS porcentaje
FROM `proyectofinalg2.proyectofinalG2.fact_ventas` f
JOIN `proyectofinalg2.proyectofinalG2.dim_sucursal` s
ON f.sucursal_key = s.sucursal_key
GROUP BY s.nombre_sucursal
ORDER BY ventas DESC;

-- =====================================================
-- Consulta 21: Ventas por segmento de cliente
-- Objetivo:
-- Analizar qué segmento de clientes genera mayores ingresos.
-- KPI: Ventas por segmento
-- =====================================================

SELECT
    c.segmento_cliente,
    SUM(f.total_venta) AS ventas
FROM `proyectofinalg2.proyectofinalG2.fact_ventas` f
JOIN `proyectofinalg2.proyectofinalG2.dim_cliente` c
ON f.cliente_key = c.cliente_key
GROUP BY c.segmento_cliente
ORDER BY ventas DESC;

-- =====================================================
-- Consulta 22: Ventas por género
-- Objetivo:
-- Analizar el comportamiento de compra por género.
-- KPI: Ventas por género
-- =====================================================

SELECT
    c.genero,
    SUM(f.total_venta) AS ventas
FROM `proyectofinalg2.proyectofinalG2.fact_ventas` f
JOIN `proyectofinalg2.proyectofinalG2.dim_cliente` c
ON f.cliente_key = c.cliente_key
GROUP BY c.genero
ORDER BY ventas DESC;

-- =====================================================
-- Consulta 23: Ventas por departamento
-- Objetivo:
-- Identificar los departamentos con mayores ingresos.
-- KPI: Ventas por departamento
-- =====================================================

SELECT
    c.departamento,
    SUM(f.total_venta) AS ventas
FROM `proyectofinalg2.proyectofinalG2.fact_ventas` f
JOIN `proyectofinalg2.proyectofinalG2.dim_cliente` c
ON f.cliente_key = c.cliente_key
GROUP BY c.departamento
ORDER BY ventas DESC;

-- =====================================================
-- Consulta 24: Precio promedio de venta por categoría
-- Objetivo:
-- Calcular el precio promedio vendido por categoría.
-- KPI: Precio promedio por categoría
-- =====================================================

SELECT
    p.categoria,
    AVG(f.precio_unitario) AS precio_promedio
FROM `proyectofinalg2.proyectofinalG2.fact_ventas` f
JOIN `proyectofinalg2.proyectofinalG2.dim_producto` p
ON f.producto_key = p.producto_key
GROUP BY p.categoria
ORDER BY precio_promedio DESC;

-- =====================================================
-- Consulta 25: Ranking de clientes
-- Objetivo:
-- Mostrar el ranking de clientes según el monto total comprado.
-- KPI: Ranking de clientes
-- =====================================================

SELECT
    c.nombre,
    SUM(f.total_venta) AS total_comprado
FROM `proyectofinalg2.proyectofinalG2.fact_ventas` f
JOIN `proyectofinalg2.proyectofinalG2.dim_cliente` c
ON f.cliente_key = c.cliente_key
GROUP BY c.nombre
ORDER BY total_comprado DESC
LIMIT 10;

