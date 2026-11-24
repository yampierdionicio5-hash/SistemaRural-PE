import tempfile
import unittest
from datetime import date, timedelta

from sistema_rural.servicios.persistencia import GestorPersistencia
from sistema_rural.servicios.sistema_rural import SistemaRural, cargar_profesionales_demo

DATOS_PACIENTE = dict(
    dni="12345678", nombres="Juan", apellidos="Quispe Rojas",
    fecha_nacimiento="1990-05-20", sexo="M", direccion="Mz B Lt 5",
)


def fecha_futura(dias=5):
    return (date.today() + timedelta(days=dias)).isoformat()


class BaseTest(unittest.TestCase):
    """Cada prueba trabaja con una carpeta temporal, sin tocar los datos reales."""

    def setUp(self):
        GestorPersistencia.reiniciar()
        self.carpeta = tempfile.TemporaryDirectory()
        self.gestor = GestorPersistencia.obtener_instancia(self.carpeta.name)
        self.sistema = SistemaRural(self.gestor)
        cargar_profesionales_demo(self.sistema)

    def tearDown(self):
        GestorPersistencia.reiniciar()
        self.carpeta.cleanup()
