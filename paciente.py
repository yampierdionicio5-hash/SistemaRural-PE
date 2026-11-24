from sistema_rural.dominio.persona import Persona
from sistema_rural.utilidades.validaciones import texto_obligatorio


class Paciente(Persona):
    """Paciente atendido en el puesto de salud (RF-01)."""
    def __init__(self, dni, nombres, apellidos, fecha_nacimiento, sexo, direccion):
        super().__init__(dni, nombres, apellidos, fecha_nacimiento, sexo)
        self.direccion = direccion

    @property
    def direccion(self):
        return self._direccion

    @direccion.setter
    def direccion(self, valor):
        self._direccion = texto_obligatorio(valor, "dirección")

    def obtener_resumen(self):
        return f"{self._dni} - {self.nombre_completo()}"

    def a_diccionario(self):
        return {
            "dni": self._dni,
            "nombres": self._nombres,
            "apellidos": self._apellidos,
            "fecha_nacimiento": self._fecha_nacimiento.isoformat(),
            "sexo": self._sexo,
            "direccion": self._direccion,
        }
