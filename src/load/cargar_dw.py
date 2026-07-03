import sqlite3

from config import DW_PATH


def cargar_data_warehouse(dimensiones, hechos):
  DW_PATH.parent.mkdir(parents=True, exist_ok=True)

  with sqlite3.connect(DW_PATH) as conn:
    for nombre, df in dimensiones.items():
      df.to_sql(nombre, conn, if_exists="replace", index=False)

    for nombre, df in hechos.items():
      df.to_sql(nombre, conn, if_exists="replace", index=False)

  print(f"\n✅ Data Warehouse cargado en: {DW_PATH}")
  print("   Tablas creadas:")
  for nombre in list(dimensiones.keys()) + list(hechos.keys()):
    print(f"   - {nombre}")

  return DW_PATH
