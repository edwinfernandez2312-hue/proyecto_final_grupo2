# --- EXTRAER ARCHIVO EXCEL DE PRODUCTOS ---
import pandas as pd
import openpyxl as openpyxl
def extraer_productos_excel():
    try:
        # Leer el archivo Excel de productos (se puede especificar la hoja con sheet_name='Productos')
        productos_df = pd.read_excel('../data/productos_temporal.xlsx', sheet_name='Productos')

        # Mostrar el total de registros
        print("Productos extraídos correctamente. Total de registros:", len(productos_df))
        
        # Mostrar los 3 primeros registros
        print("\n--- Primeros 3 registros de Productos ---")
        print(productos_df.head(3))
        print("-----------------------------------------\n")

        return productos_df

    except Exception as e:
        print(f"Error al extraer el archivo Excel de productos: {e}")
        return None 