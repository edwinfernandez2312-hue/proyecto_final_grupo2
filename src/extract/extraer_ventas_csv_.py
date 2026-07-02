# EXTRAER ARCHIVO CSV DE VENTAS
import pandas as pd

def extraer_ventas_csv():
    try:
        # Leer el archivo CSV de ventas
        ventas_df = pd.read_csv('../data/ventas_temporal.csv')

        # Mostrar el total de registros
        print("Ventas extraídas correctamente. Total de registros:", len(ventas_df))
        
        # Mostrar los 3 primeros registros
        print("\n--- Primeros 3 registros de Ventas ---")
        print(ventas_df.head(3))
        print("--------------------------------------\n")

        return ventas_df

    except Exception as e:
        print(f"Error al extraer el archivo CSV de ventas: {e}")
        return None