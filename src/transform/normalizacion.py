import re
import unicodedata


def _reparar_codificacion(texto):
  if not isinstance(texto, str):
    return str(texto)

  texto = texto.strip()
  if "Ã" in texto:
    try:
      texto = texto.encode("latin-1").decode("utf-8")
    except (UnicodeDecodeError, UnicodeEncodeError):
      pass
  return texto


def _clave(texto):
  texto = _reparar_codificacion(texto)
  texto = unicodedata.normalize("NFKD", texto)
  texto = "".join(ch for ch in texto if not unicodedata.combining(ch))
  texto = re.sub(r"\s+", " ", texto.strip().lower())
  return texto


CANAL_EXACTO = {
  "web": "E-commerce",
  "e-commerce": "E-commerce",
  "online": "E-commerce",
  "onlin": "E-commerce",
  "sitio": "E-commerce",
  "siti": "E-commerce",
  "pagina web": "E-commerce",
  "pagina we": "E-commerce",
  "tienda": "Tienda",
  "tiend": "Tienda",
  "tienda fisica": "Tienda",
  "tienda fisic": "Tienda",
  "whatsapp": "WhatsApp",
  "whatsap": "WhatsApp",
  "wa": "WhatsApp",
  "we": "WhatsApp",
  "w": "WhatsApp",
}

PAGO_EXACTO = {
  "efectivo": "Efectivo",
  "efectiv": "Efectivo",
  "cash": "Efectivo",
  "tarjeta": "Tarjeta",
  "tarjet": "Tarjeta",
  "tc": "Tarjeta",
  "t": "Tarjeta",
  "credito": "Tarjeta",
  "credit": "Tarjeta",
  "visa": "Tarjeta",
  "vis": "Tarjeta",
  "mastercard": "Tarjeta",
  "mastercar": "Tarjeta",
  "tarjeta credito": "Tarjeta",
  "tarjeta credit": "Tarjeta",
  "transferencia": "Transferencia",
  "transferenci": "Transferencia",
  "transf.": "Transferencia",
  "transf": "Transferencia",
  "deposito": "Transferencia",
  "deposit": "Transferencia",
}

TIPO_MOVIMIENTO_EXACTO = {
  "entrada": "Entrada",
  "ingreso": "Entrada",
  "compra": "Entrada",
  "e": "Entrada",
  "salida": "Salida",
  "venta": "Salida",
  "s": "Salida",
  "ajuste": "Ajuste",
  "ajuste manual": "Ajuste",
}


def normalizar_canal_venta(valor):
  if valor is None or (isinstance(valor, float) and str(valor) == "nan"):
    return "No disponible"

  clave = _clave(valor)
  if not clave:
    return "No disponible"

  if clave in CANAL_EXACTO:
    return CANAL_EXACTO[clave]

  if "whatsapp" in clave or "whatsap" in clave or clave in {"wa", "we"}:
    return "WhatsApp"
  if "tiend" in clave or "fisic" in clave:
    return "Tienda"
  if any(palabra in clave for palabra in ("web", "sitio", "siti", "online", "onlin", "pagina")):
    return "E-commerce"

  return _reparar_codificacion(str(valor)).strip().title()


def normalizar_metodo_pago(valor):
  if valor is None or (isinstance(valor, float) and str(valor) == "nan"):
    return "No disponible"

  clave = _clave(valor)
  if not clave:
    return "No disponible"

  if clave in PAGO_EXACTO:
    return PAGO_EXACTO[clave]

  if "efect" in clave or "cash" in clave:
    return "Efectivo"
  if any(palabra in clave for palabra in ("tarjeta", "tarjet", "credito", "credit", "visa", "master", " tc", "tc ")):
    return "Tarjeta"
  if clave == "tc" or clave.startswith("tc ") or clave.endswith(" tc"):
    return "Tarjeta"
  if "transf" in clave or "deposit" in clave:
    return "Transferencia"

  return _reparar_codificacion(str(valor)).strip().title()


def normalizar_tipo_movimiento(valor):
  if valor is None or (isinstance(valor, float) and str(valor) == "nan"):
    return "No disponible"

  clave = _clave(valor)
  if clave in TIPO_MOVIMIENTO_EXACTO:
    return TIPO_MOVIMIENTO_EXACTO[clave]

  if "entr" in clave or "ingr" in clave or "compr" in clave:
    return "Entrada"
  if "salid" in clave or "vent" in clave:
    return "Salida"
  if "ajust" in clave:
    return "Ajuste"

  return _reparar_codificacion(str(valor)).strip().title()


def limpiar_existencia_serie(serie):
  import pandas as pd

  existencia = pd.to_numeric(serie, errors="coerce").fillna(0)
  return existencia.clip(lower=0).astype(int)


def normalizar_fecha_iso(serie):
  import pandas as pd

  fechas = pd.to_datetime(serie, errors="coerce", format="mixed")
  return fechas.dt.strftime("%Y-%m-%d")
