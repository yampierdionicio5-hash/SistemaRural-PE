import re
from abc import ABC, abstractmethod
from datetime import date

from sistema_rural.excepciones import DatoInvalidoError
from sistema_rural.servicios.seguridad import ServicioSeguridad
from sistema_rural.utilidades.validaciones import parsear_fecha, texto_obligatorio


class Persona(ABC):
    """Clase base abstracta de las personas del sistema.

    Los atributos son privados y se exponen mediante propiedades que validan el dato.
    """
    _PATRON_DNI = re.compile(r"^\d{8}$")

    def __init__(self, dni, nombres, apellidos, fecha_nacimiento, sexo):
        self.dni = dni
        self.nombres = nombres
        self.apellidos = apellidos
        self.fecha_nacimiento = fecha_nacimiento
        self.sexo = sexo

    @property
    def dni(self):
        return self._dni

    @dni.setter
    def dni(self, valor):
        valor = str(valor).strip()
        # RF-01 y CE-02: el DNI debe tener exactamente 8 dígitos.
        if not self._PATRON_DNI.match(valor):
            raise DatoInvalidoError("El DNI debe tener exactamente 8 dígitos.")
        self._dni = valor

    @property
    def nombres(self):
        return self._nombres

    @nombres.setter
    def nombres(self, valor):
        self._nombres = texto_obligatorio(valor, "nombres")

    @property
    def apellidos(self):
        return self._apellidos

    @apellidos.setter
    def apellidos(self, valor):
        self._apellidos = texto_obligatorio(valor, "apellidos")

    @property
    def fecha_nacimiento(self):
        return self._fecha_nacimiento

    @fecha_nacimiento.setter
    def fecha_nacimiento(self, valor):
        fecha = parsear_fecha(valor)
        if fecha > date.today():
            raise DatoInvalidoError("La fecha de nacimiento no puede ser futura.")
        self._fecha_nacimiento = fecha

    @property
    def sexo(self):
        return self._sexo

    @sexo.setter
    def sexo(self, valor):
        valor = str(valor).strip().upper()
        if valor not in ("M", "F"):
            raise DatoInvalidoError("El sexo debe ser M o F.")
        self._sexo = valor

    def nombre_completo(self):
        return f"{self._nombres} {self._apellidos}"

    def edad(self):
        hoy = date.today()
        cumplio = (hoy.month, hoy.day) >= (self._fecha_nacimiento.month, self._fecha_nacimiento.day)
        return hoy.year - self._fecha_nacimiento.year - (0 if cumplio else 1)

    @abstractmethod
    def obtener_resumen(self):
        pass

    def __repr__(self):
        # No se imprimen datos personales en logs ni en la consola.
        return f"<{type(self).__name__} dni={ServicioSeguridad.enmascarar_dni(self._dni)}>"
