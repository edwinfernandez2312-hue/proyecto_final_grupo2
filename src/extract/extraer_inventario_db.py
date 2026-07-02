import pandas as pd
import sqlite3 as sqlite3

# --- EXTRAER BASE DE DATOS SQLITE DE INVENTARIO ---
def extraer_inventario_db():
    try:
        # Conectar a la base de datos SQLite usando un context manager (with)
        with sqlite3.connect('../data/inventario_temporal.db') as conn:
            # Escribir la consulta SQL para extraer la tabla deseada
            query = "SELECT * FROM inventario;"
            
            # Leer los datos usando pandas
            inventario_df = pd.read_sql_query(query, conn)

        # Mostrar el total de registros
        print("Inventario extraído correctamente. Total de registros:", len(inventario_df))
        
        # Mostrar los 3 primeros registros
        print("\n--- Primeros 3 registros de Inventario ---")
        print(inventario_df.head(3))
        print("------------------------------------------\n")

        return inventario_df

    except Exception as e:
        print(f"Error al extraer la base de datos SQLite de inventario: {e}")
        return None