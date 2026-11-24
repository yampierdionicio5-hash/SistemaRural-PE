import json

from sistema_rural.dominio.medicamento import Medicamento
from sistema_rural.excepciones import ErrorAlmacenamiento
from sistema_rural.servicios.persistencia import GestorPersistencia
from sistema_rural.servicios.reportes import MotorReportes
from sistema_rural.servicios.sistema_rural import SistemaRural, cargar_profesionales_demo
from tests.base import DATOS_PACIENTE, BaseTest, fecha_futura


class TestPersistencia(BaseTest):
    def test_datos_personales_no_aparecen_en_texto_plano_en_el_json(self):
        self.sistema.registrar_paciente(**DATOS_PACIENTE)
        cita = self.sistema.programar_cita("12345678", "CMP-10001", fecha_futura(), "Medicina General")
        self.sistema.registrar_atencion(cita.id_cita, "Dolor de garganta", "Faringitis", "Reposo")
        self.sistema.guardar()
        contenido = self.gestor.ruta.read_text(encoding="utf-8")
        for dato in ("12345678", "Juan", "Quispe", "Mz B", "Faringitis", "Reposo", "garganta"):
            self.assertNotIn(dato, contenido)

    def test_los_datos_guardados_se_recuperan_al_cargar(self):
        self.sistema.registrar_paciente(**DATOS_PACIENTE)
        cita = self.sistema.programar_cita("12345678", "CMP-10001", fecha_futura(), "Medicina General")
        self.sistema.registrar_atencion(cita.id_cita, "Tos", "Faringitis", "Reposo")
        self.sistema.inventario.agregar_medicamento(Medicamento("P1", "Paracetamol", 30, fecha_futura(400)))
        self.sistema.inventario.registrar_salida("P1", 4)
        self.sistema.guardar()

        otro = SistemaRural(self.gestor)
        cargar_profesionales_demo(otro)
        otro.cargar()
        self.assertEqual(otro.obtener_paciente("12345678").apellidos, "Quispe Rojas")
        self.assertEqual(otro.citas[0].estado, "ATENDIDA")
        self.assertEqual(len(otro.atenciones), 1)
        self.assertEqual(otro.inventario.medicamentos[0].stock, 26)
        self.assertEqual(MotorReportes.consumo_total(otro.inventario.salidas), 4)

    def test_archivo_alterado_es_detectado(self):
        self.sistema.registrar_paciente(**DATOS_PACIENTE)
        self.sistema.guardar()
        datos = json.loads(self.gestor.ruta.read_text(encoding="utf-8"))
        datos["pacientes"][0]["nombres"] = "token-falso"
        self.gestor.ruta.write_text(json.dumps(datos), encoding="utf-8")
        with self.assertRaises(ErrorAlmacenamiento):
            SistemaRural(self.gestor).cargar()

    def test_json_danado_lanza_error_controlado(self):
        self.gestor.ruta.write_text("{ esto no es json", encoding="utf-8")
        with self.assertRaises(ErrorAlmacenamiento):
            SistemaRural(self.gestor).cargar()

    def test_singleton_devuelve_siempre_la_misma_instancia(self):
        self.assertIs(GestorPersistencia.obtener_instancia(), self.gestor)
        with self.assertRaises(RuntimeError):
            GestorPersistencia()
