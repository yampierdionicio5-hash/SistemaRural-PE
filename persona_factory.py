from sistema_rural.dominio.paciente import Paciente
from sistema_rural.dominio.profesional_salud import ProfesionalSalud
from sistema_rural.excepciones import DatoInvalidoError


class PersonaFactory:
    """Patrón Factory: decide qué clase concreta de Persona se crea."""

    _TIPOS = {"paciente": Paciente, "profesional": ProfesionalSalud}

    @staticmethod
    def crear(tipo, **datos):
        clase = PersonaFactory._TIPOS.get(tipo)
        if clase is None:
            raise DatoInvalidoError(f"Tipo de persona desconocido: {tipo}")
        try:
            return clase(**datos)
        except TypeError:
            raise DatoInvalidoError("Faltan datos o hay datos de más para crear la persona.")
