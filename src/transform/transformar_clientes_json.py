import pandas as pd
import numpy as np

def transformar_clientes_json(df_clientes):
    try:
        # 1. Eliminar duplicados: conservar el registro más reciente (o el último en el df)
        df = df_clientes.drop_duplicates(subset=['id_cliente'], keep='last').copy()
        
        # 2. Manejo de nulos: Marcar como "no disponible"
        df.fillna("No disponible", inplace=True)
        
        # 3. Estandarización de columnas (minúsculas y sin espacios extra)
        df.columns = df.columns.str.lower().str.strip()
        
        print("✅ Limpieza de Clientes completada.")
        
        # Muestra de las 3 primeras filas limpias para inspección visual
        print("\n--- Primeros 3 registros de Clientes (Limpios) ---")
        print(df.head(3))
        print("--------------------------------------------------\n")
        
        return df
    except Exception as e:
        print(f"Error al limpiar clientes: {e}")
        return None