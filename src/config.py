from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DW_PATH = DATA_DIR / "datacommerce_dw.db"

VENTAS_CSV = DATA_DIR / "ventas_masivo.csv"
PRODUCTOS_XLSX = DATA_DIR / "productos_masivo.xlsx"
CLIENTES_JSON = DATA_DIR / "clientes_masivo.json"
INVENTARIO_DB = DATA_DIR / "inventario_masivo.db"
MARKETING_JSON = DATA_DIR / "api_marketing_response_masivo.json"
