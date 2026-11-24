from pathlib import Path

# Reglas de negocio del puesto de salud
UMBRAL_STOCK_CRITICO = 10
DIAS_POR_VENCER = 30

# La carpeta "datos" queda junto al proyecto, sin importar desde dónde se ejecute.
CARPETA_DATOS = Path(__file__).resolve().parent.parent / "datos"
NOMBRE_ARCHIVO_DATOS = "datos_rural.json"
NOMBRE_ARCHIVO_CLAVE = "clave.key"
