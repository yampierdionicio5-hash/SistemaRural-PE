from sistema_rural.utilidades.validaciones import texto_obligatorio


class AtencionClinica:
    """Atención realizada a partir de una cita: motivo, diagnóstico y tratamiento (RF-04)."""
    def __init__(self, cita, motivo_consulta, diagnostico, tratamiento):
        self._cita = cita
        self._motivo_consulta = texto_obligatorio(motivo_consulta, "motivo de consulta")
        self._diagnostico = texto_obligatorio(diagnostico, "diagnóstico")
        self._tratamiento = texto_obligatorio(tratamiento, "tratamiento")

    @property
    def cita(self):
        return self._cita

    @property
    def paciente(self):
        return self._cita.paciente

    @property
    def fecha(self):
        return self._cita.fecha

    @property
    def profesional(self):
        return self._cita.profesional

    @property
    def motivo_consulta(self):
        return self._motivo_consulta

    @property
    def diagnostico(self):
        return self._diagnostico

    @property
    def tratamiento(self):
        return self._tratamiento

    def registrar(self):
        self._cita.marcar_atendida()

    def a_diccionario(self):
        return {
            "id_cita": self._cita.id_cita,
            "motivo_consulta": self._motivo_consulta,
            "diagnostico": self._diagnostico,
            "tratamiento": self._tratamiento,
        }
