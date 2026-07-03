# Hallazgos de calidad de datos — Día 2


## Fuentes analizadas

| Fuente | Archivo | Registros |
|--------|---------|-----------|
| Ventas | `ventas.csv` | 5 |
| Productos | `productos.xlsx` | 4 |
| Clientes | `clientes.json` | 3 |
| Inventario | `inventario.db` | 3 existencias + 2 movimientos |
| Marketing | `api_marketing_response.json` | 2 campañas |

---

## 1. Ventas (`ventas.csv`)

- **Fechas en formatos mixtos:** `2026-07-01`, `01/07/2026`, `2026/07/02`
- **Cliente huérfano:** `venta_id=1005` referencia `cliente_id=504`, que no existe en `clientes.json`
- **Canales inconsistentes:** valores como `Web` que se alinean al canal corporativo `E-commerce`

### Reglas aplicadas
1. Estandarizar `fecha_venta` a formato ISO `YYYY-MM-DD` con `pd.to_datetime(dayfirst=True)`
2. Eliminar duplicados por `venta_id` (conservar el último)
3. Normalizar `canal_venta` (Title Case; `Web` → `E-commerce`)
4. Rellenar `metodo_pago` nulo con `"No disponible"`
5. Descartar filas sin `venta_id`, `cliente_id`, `producto_id` o fecha válida

---

## 2. Productos (`productos.xlsx`)

- Hoja única llamada `Sheet` (no `Productos`)
- Columna de precio se llama `precio_lista` (no `precio_unitario`)

### Reglas aplicadas
1. Eliminar duplicados por `producto_id`
2. Convertir `costo_unitario` y `precio_lista` a numérico
3. Rellenar textos vacíos o nulos con `"No disponible"`
4. Rellenar numéricos nulos con `0`

---

## 3. Clientes (`clientes.json`)

- `cliente_id=503` tiene `municipio` vacío (`""`)
- Solo 3 clientes registrados vs. 4 clientes distintos en ventas

### Reglas aplicadas
1. Eliminar duplicados por `cliente_id`
2. Reemplazar `municipio` vacío por `"No disponible"`
3. Estandarizar `fecha_registro` a `YYYY-MM-DD`
4. Rellenar nulos en columnas de texto con `"No disponible"`

---

## 4. Inventario (`inventario.db`)

- Dos tablas: `inventario_actual` y `movimientos_inventario` (no una sola tabla `inventario`)
- Movimientos con tipos `Entrada` y `Salida`

### Reglas aplicadas
1. Deduplicar existencias por `producto_id` + `bodega`
2. Deduplicar movimientos por `id`
3. Estandarizar `bodega` y `tipo` (Title Case)
4. Convertir cantidades a entero; descartar movimientos sin fecha o producto

---

## 5. Marketing (`api_marketing_response.json`)

- Respuesta anidada bajo la clave `campaigns` (simula API REST)
- Columna `campaña_id` con carácter especial (ñ)

### Reglas aplicadas
1. Aplanar JSON con `pd.json_normalize`
2. Renombrar `campaña_id` → `campana_id` para consistencia SQL
3. Estandarizar `fecha` a `YYYY-MM-DD`
4. Validar métricas numéricas (`impresiones`, `clics`, `costo`, `leads`, `conversiones`)

---

