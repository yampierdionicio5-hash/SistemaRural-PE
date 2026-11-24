from datetime import date, datetime

from sistema_rural.excepciones import DatoInvalidoError


def parsear_fecha(valor):
    """Convierte un texto AAAA-MM-DD (o un date) en un objeto date."""
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    try:
        return datetime.strptime(str(valor).strip(), "%Y-%m-%d").date()
    except ValueError:
        raise DatoInvalidoError("La fecha debe tener el formato AAAA-MM-DD.")


def texto_obligatorio(valor, nombre_campo):
    valor = str(valor).strip()
    if not valor:
        raise DatoInvalidoError(f"El campo '{nombre_campo}' es obligatorio.")
    return valor


def validar_cantidad(valor, permitir_cero=False):
    try:
        cantidad = int(valor)
    except (TypeError, ValueError):
        raise DatoInvalidoError("La cantidad debe ser un número entero.")
    if cantidad < (0 if permitir_cero else 1):
        raise DatoInvalidoError("La cantidad indicada no es válida.")
    return cantidad
