import pandas as pd

def transformar_productos_excel(df_productos):
    try:
        # 1. Eliminar duplicados
        df = df_productos.drop_duplicates(subset=['id_producto'], keep='last').copy()
        
        # 2. Estandarización de tipos de datos
        df['precio_unitario'] = pd.to_numeric(df['precio_unitario'], errors='coerce')
        df['costo_unitario'] = pd.to_numeric(df['costo_unitario'], errors='coerce')
        
        # 3. Manejo de nulos
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].fillna("No disponible")
        for col in df.select_dtypes(include=['number']).columns:
            df[col] = df[col].fillna(0.0)
            
        print("✅ Limpieza de Productos completada.")
        
        # Inspección visual
        print("\n--- Primeros 3 registros de Productos (Limpios) ---")
        print(df.head(3))
        print("---------------------------------------------------\n")
        
        return df
    except Exception as e:
        print(f"Error al limpiar productos: {e}")
        return None