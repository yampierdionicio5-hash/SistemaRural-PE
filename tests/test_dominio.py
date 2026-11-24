from sistema_rural.excepciones import DatoInvalidoError, DuplicadoError
from tests.base import DATOS_PACIENTE, BaseTest, fecha_futura


class TestPacientes(BaseTest):
    def test_dni_con_menos_de_8_digitos_es_rechazado(self):
        with self.assertRaises(DatoInvalidoError):
            self.sistema.registrar_paciente(**{**DATOS_PACIENTE, "dni": "1234567"})

    def test_dni_con_letras_es_rechazado(self):
        with self.assertRaises(DatoInvalidoError):
            self.sistema.registrar_paciente(**{**DATOS_PACIENTE, "dni": "1234567A"})

    def test_dni_duplicado_es_rechazado(self):
        self.sistema.registrar_paciente(**DATOS_PACIENTE)
        with self.assertRaises(DuplicadoError):
            self.sistema.registrar_paciente(**DATOS_PACIENTE)

    def test_campos_obligatorios_vacios_son_rechazados(self):
        with self.assertRaises(DatoInvalidoError):
            self.sistema.registrar_paciente(**{**DATOS_PACIENTE, "nombres": "  "})

    def test_busqueda_por_apellido_y_dni(self):
        self.sistema.registrar_paciente(**DATOS_PACIENTE)
        self.assertEqual(len(self.sistema.buscar_pacientes(apellido="quispe")), 1)
        self.assertEqual(len(self.sistema.buscar_pacientes(dni="1234")), 1)
        self.assertEqual(len(self.sistema.buscar_pacientes(apellido="perez")), 0)

    def test_actualizar_direccion(self):
        self.sistema.registrar_paciente(**DATOS_PACIENTE)
        self.sistema.actualizar_paciente("12345678", direccion="Mz C Lt 9")
        self.assertEqual(self.sistema.obtener_paciente("12345678").direccion, "Mz C Lt 9")

    def test_repr_no_expone_el_dni_completo(self):
        paciente = self.sistema.registrar_paciente(**DATOS_PACIENTE)
        self.assertNotIn("12345678", repr(paciente))


class TestCitasYAtenciones(BaseTest):
    def setUp(self):
        super().setUp()
        self.sistema.registrar_paciente(**DATOS_PACIENTE)

    def test_cita_en_fecha_pasada_es_rechazada(self):
        with self.assertRaises(DatoInvalidoError):
            self.sistema.programar_cita("12345678", "CMP-10001", "2020-01-01", "Medicina General")

    def test_cita_con_fecha_mal_escrita_es_rechazada(self):
        with self.assertRaises(DatoInvalidoError):
            self.sistema.programar_cita("12345678", "CMP-10001", "01/12/2030", "Medicina General")

    def test_cita_se_puede_reprogramar_y_cancelar(self):
        cita = self.sistema.programar_cita("12345678", "CMP-10001", fecha_futura(), "Medicina General")
        cita.reprogramar(fecha_futura(10))
        cita.cancelar()
        self.assertEqual(cita.estado, "CANCELADA")
        with self.assertRaises(DatoInvalidoError):
            cita.cancelar()

    def test_la_cita_toma_la_especialidad_del_profesional(self):
        cita = self.sistema.programar_cita("12345678", "CMP-10002", fecha_futura())
        self.assertEqual(cita.especialidad, "Obstetricia")

    def test_ficha_completa_muestra_datos_citas_y_atenciones(self):
        cita = self.sistema.programar_cita("12345678", "CMP-10001", fecha_futura(), "Medicina General")
        self.sistema.registrar_atencion(cita.id_cita, "Tos", "Faringitis", "Reposo")
        ficha = self.sistema.ficha_paciente("12345678")
        for dato in ("12345678", "Juan Quispe Rojas", "Mz B Lt 5", "Faringitis", "Reposo", "ATENDIDA"):
            self.assertIn(dato, ficha)

    def test_atencion_marca_la_cita_como_atendida_y_no_se_repite(self):
        cita = self.sistema.programar_cita("12345678", "CMP-10001", fecha_futura(), "Medicina General")
        self.sistema.registrar_atencion(cita.id_cita, "Tos", "Faringitis", "Reposo")
        self.assertEqual(cita.estado, "ATENDIDA")
        with self.assertRaises(DatoInvalidoError):
            self.sistema.registrar_atencion(cita.id_cita, "Tos", "Faringitis", "Reposo")
