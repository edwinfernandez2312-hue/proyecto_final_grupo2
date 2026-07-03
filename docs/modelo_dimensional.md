# Modelo dimensional — Día 3

Esquema en estrella (Star Schema) para el Data Warehouse de **DataCommerce GT**, almacenado en `data/datacommerce_dw.db` (SQLite).


## Tablas de dimensiones

| Tabla | Descripción | Clave surrogate |
|-------|-------------|-----------------|
| `dim_tiempo` | Calendario derivado de fechas de ventas, movimientos y campañas | `fecha_key` (YYYYMMDD) |
| `dim_cliente` | Perfil de clientes + clientes huérfanos de ventas | `cliente_key` |
| `dim_producto` | Catálogo de productos | `producto_key` |
| `dim_sucursal` | Sucursales físicas (1=Centro, 2=Norte, 3=Sur) | `sucursal_key` |
| `dim_canal` | Canales de venta (Tienda, WhatsApp, E-commerce) | `canal_key` |
| `dim_bodega` | Bodegas de inventario | `bodega_key` |
| `dim_metodo_pago` | Métodos de pago | `metodo_pago_key` |
| `dim_campana` | Campañas de marketing por plataforma | `campana_key` |

## Tablas de hechos

| Tabla | Granularidad | Medidas |
|-------|--------------|---------|
| `fact_ventas` | Una línea por venta | cantidad, precio_unitario, descuento, total_venta |
| `fact_inventario` | Existencia por producto y bodega | existencia |
| `fact_movimientos_inventario` | Un movimiento de inventario | cantidad |
| `fact_marketing` | Una campaña por día | impresiones, clics, costo, leads, conversiones |

## Cómo ejecutar

```bash
cd src
python main.py
```

El pipeline extrae, limpia, construye dimensiones/hechos y carga `data/datacommerce_dw.db`.
