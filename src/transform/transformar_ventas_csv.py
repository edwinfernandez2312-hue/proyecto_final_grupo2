import pandas as pd

def transformar_ventas_csv(df_ventas):
    try:
        # 1. Eliminar duplicados exactos: conservar el registro más reciente
        df = df_ventas.drop_duplicates(subset=['id_venta'], keep='last').copy()
        
        # 2. Estandarizar fechas a formato ISO (AAAA-MM-DD)
        # Esto asegura que todas las fechas tengan el mismo formato para el Data Warehouse
        df['fecha_venta'] = pd.to_datetime(df['fecha_venta'], errors='coerce').dt.strftime('%Y-%m-%d')
        
        # 3. Campos nulos o incompletos: Marcar como "no disponible"
        df['metodo_pago'] = df['metodo_pago'].fillna("No disponible")
        
        # 4. Limpieza básica de integridad
        # Si la venta no tiene un id_cliente, no nos sirve para el modelo estrella, así que lo descartamos
        df = df.dropna(subset=['id_cliente'])
        
        print("✅ Limpieza de Ventas completada.")
        
        # Inspección visual
        print("\n--- Primeros 3 registros de Ventas (Limpias) ---")
        print(df.head(3))
        print("------------------------------------------------\n")
        
        return df
    except Exception as e:
        print(f"Error al limpiar ventas: {e}")
        return None