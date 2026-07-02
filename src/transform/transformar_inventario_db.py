import pandas as pd

def transformar_inventario_db(df_inventario):
    try:
        # 1. Eliminar duplicados
        df = df_inventario.drop_duplicates(subset=['id_inventario'], keep='last').copy()
        
        # 2. Manejo de nulos
        df.fillna("No disponible", inplace=True)
        
        print("✅ Limpieza de Inventario completada.")
        
        # Inspección visual
        print("\n--- Primeros 3 registros de Inventario (Limpios) ---")
        print(df.head(3))
        print("----------------------------------------------------\n")
        
        return df
    except Exception as e:
        print(f"Error al limpiar inventario: {e}")
        return None