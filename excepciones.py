class ErrorRural(Exception):
    """Clase base de los errores propios del sistema."""


class DatoInvalidoError(ErrorRural):
    """Un dato no cumple el formato o la regla de negocio."""


class DuplicadoError(ErrorRural):
    """Se intentó registrar algo que ya existe (por ejemplo, un DNI repetido)."""


class StockInsuficienteError(ErrorRural):
    """Se pidió una salida mayor al stock disponible."""


class ErrorAlmacenamiento(ErrorRural):
    """Falló la lectura, la escritura o el descifrado de los datos guardados."""
