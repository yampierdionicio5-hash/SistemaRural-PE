import tempfile
import unittest
from pathlib import Path

from sistema_rural.excepciones import ErrorAlmacenamiento
from sistema_rural.servicios.seguridad import ServicioSeguridad


class TestSeguridad(unittest.TestCase):
    def setUp(self):
        self.carpeta = tempfile.TemporaryDirectory()
        self.seguridad = ServicioSeguridad(Path(self.carpeta.name) / "clave.key")

    def tearDown(self):
        self.carpeta.cleanup()

    def test_cifrar_y_descifrar_devuelve_el_texto_original(self):
        token = self.seguridad.cifrar("Juan Pérez Quispe")
        self.assertNotIn("Juan", token)
        self.assertEqual(self.seguridad.descifrar(token), "Juan Pérez Quispe")

    def test_el_mismo_texto_produce_tokens_distintos(self):
        self.assertNotEqual(self.seguridad.cifrar("12345678"), self.seguridad.cifrar("12345678"))

    def test_token_alterado_es_detectado(self):
        token = self.seguridad.cifrar("12345678")
        alterado = token[:-4] + ("AAAA" if not token.endswith("AAAA") else "BBBB")
        with self.assertRaises(ErrorAlmacenamiento):
            self.seguridad.descifrar(alterado)

    def test_otra_clave_no_puede_descifrar(self):
        token = self.seguridad.cifrar("12345678")
        otra = ServicioSeguridad(Path(self.carpeta.name) / "otra.key")
        with self.assertRaises(ErrorAlmacenamiento):
            otra.descifrar(token)

    def test_la_clave_se_reutiliza_al_reabrir(self):
        token = self.seguridad.cifrar("dato")
        reabierto = ServicioSeguridad(Path(self.carpeta.name) / "clave.key")
        self.assertEqual(reabierto.descifrar(token), "dato")

    def test_enmascarado_de_dni_para_registros_internos(self):
        self.assertEqual(ServicioSeguridad.enmascarar_dni("12345678"), "12****78")
