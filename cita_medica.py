from datetime import date

from sistema_rural.excepciones import DatoInvalidoError
from sistema_rural.utilidades.validaciones import parsear_fecha, texto_obligatorio


class CitaMedica:
    """Cita médica. Estados: PENDIENTE, PROGRAMADA, ATENDIDA y CANCELADA (RF-02)."""
    def __init__(self, id_cita, paciente, profesional, fecha, especialidad, estado="PENDIENTE"):
        self._id_cita = id_cita
        self._paciente = paciente
        self._profesional = profesional
        self._fecha = parsear_fecha(fecha)
        self._especialidad = texto_obligatorio(especialidad, "especialidad")
        self._estado = estado

    @property
    def id_cita(self):
        return self._id_cita

    @property
    def paciente(self):
        return self._paciente

    @property
    def profesional(self):
        return self._profesional

    @property
    def fecha(self):
        return self._fecha

    @property
    def especialidad(self):
        return self._especialidad

    @property
    def estado(self):
        return self._estado

    def programar(self):
        if self._fecha < date.today():
            raise DatoInvalidoError("No se puede programar una cita en una fecha pasada.")
        self._estado = "PROGRAMADA"

    def reprogramar(self, nueva_fecha):
        if self._estado != "PROGRAMADA":
            raise DatoInvalidoError("Solo se pueden reprogramar citas en estado PROGRAMADA.")
        nueva_fecha = parsear_fecha(nueva_fecha)
        if nueva_fecha < date.today():
            raise DatoInvalidoError("La nueva fecha no puede ser pasada.")
        self._fecha = nueva_fecha

    def cancelar(self):
        if self._estado != "PROGRAMADA":
            raise DatoInvalidoError("Solo se pueden cancelar citas en estado PROGRAMADA.")
        self._estado = "CANCELADA"

    def marcar_atendida(self):
        if self._estado != "PROGRAMADA":
            raise DatoInvalidoError("La cita debe estar PROGRAMADA para registrar su atención.")
        self._estado = "ATENDIDA"

    def a_diccionario(self):
        return {
            "id_cita": self._id_cita,
            "dni_paciente": self._paciente.dni,
            "nro_colegiatura": self._profesional.nro_colegiatura,
            "fecha": self._fecha.isoformat(),
            "especialidad": self._especialidad,
            "estado": self._estado,
        }
