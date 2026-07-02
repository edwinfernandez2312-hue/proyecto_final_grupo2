import pandas as pd


# --- EXTRAER ARCHIVO JSON DE CLIENTES ---
def extraer_clientes_json():
    try:
        # Leer el archivo JSON de clientes
        clientes_df = pd.read_json('../data/clientes_temporal.json')

        # Mostrar el total de registros
        print("Clientes extraídos correctamente. Total de registros:", len(clientes_df))
        
        # Mostrar los 3 primeros registros
        print("\n--- Primeros 3 registros de Clientes ---")
        print(clientes_df.head(3))
        print("----------------------------------------\n")

        return clientes_df

    except Exception as e:
        print(f"Error al extraer el archivo JSON de clientes: {e}")
        return None