from sistema_rural.dominio.persona import Persona
from sistema_rural.utilidades.validaciones import texto_obligatorio


class ProfesionalSalud(Persona):
    """Profesional de salud que atiende las citas; su especialidad define el servicio."""
    def __init__(self, dni, nombres, apellidos, fecha_nacimiento, sexo, nro_colegiatura, especialidad):
        super().__init__(dni, nombres, apellidos, fecha_nacimiento, sexo)
        self._nro_colegiatura = texto_obligatorio(nro_colegiatura, "colegiatura")
        self._especialidad = texto_obligatorio(especialidad, "especialidad")

    @property
    def nro_colegiatura(self):
        return self._nro_colegiatura

    @property
    def especialidad(self):
        return self._especialidad

    def obtener_resumen(self):
        return f"{self.nombre_completo()} ({self._especialidad}) - {self._nro_colegiatura}"
