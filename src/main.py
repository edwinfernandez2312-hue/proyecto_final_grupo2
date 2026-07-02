# main.py
from pipeline_manager import run_etl_pipeline

def main():
    """
    Punto de entrada principal del proyecto ETL.
    """
    try:
        # Llamamos al orquestador que dirige todo el proceso
        run_etl_pipeline()
    except Exception as e:
        print(f"\n❌ Error crítico en la ejecución del pipeline: {e}")

if __name__ == "__main__":
    main()