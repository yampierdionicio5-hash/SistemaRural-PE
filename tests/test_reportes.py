from sistema_rural.dominio.medicamento import Medicamento
from sistema_rural.excepciones import StockInsuficienteError
from sistema_rural.servicios.reportes import MotorReportes
from tests.base import DATOS_PACIENTE, BaseTest, fecha_futura


class TestReportes(BaseTest):
    def test_morbilidad_cuenta_diagnosticos_con_reduce(self):
        self.sistema.registrar_paciente(**DATOS_PACIENTE)
        for diagnostico in ("Faringitis", "Faringitis", "Anemia"):
            cita = self.sistema.programar_cita("12345678", "CMP-10001", fecha_futura(), "Medicina General")
            self.sistema.registrar_atencion(cita.id_cita, "Control", diagnostico, "Indicado")
        resultado = MotorReportes.morbilidad_por_diagnostico(self.sistema.atenciones)
        self.assertEqual(resultado, {"Faringitis": 2, "Anemia": 1})

    def test_resumen_de_pacientes_incluye_sus_datos(self):
        self.sistema.registrar_paciente(**DATOS_PACIENTE)
        resumen = MotorReportes.resumen_pacientes(self.sistema.pacientes)
        self.assertEqual(resumen[0]["dni"], "12345678")
        self.assertEqual(resumen[0]["nombre"], "Juan Quispe Rojas")
        self.assertEqual(resumen[0]["direccion"], "Mz B Lt 5")

    def test_reporte_muestra_la_informacion_del_paciente_y_la_atencion(self):
        self.sistema.registrar_paciente(**DATOS_PACIENTE)
        cita = self.sistema.programar_cita("12345678", "CMP-10001", fecha_futura(0), "Medicina General")
        self.sistema.registrar_atencion(cita.id_cita, "Tos", "Faringitis", "Reposo")
        reporte = self.sistema.generar_reporte(7)
        for dato in ("12345678", "Juan Quispe Rojas", "Ana Torres Vega", "Tos", "Faringitis", "Reposo", "Mz B Lt 5"):
            self.assertIn(dato, reporte)

    def test_reporte_incluye_consumo_por_medicamento(self):
        inv = self.sistema.inventario
        inv.agregar_medicamento(Medicamento("P1", "Paracetamol", 100, fecha_futura(400)))
        inv.registrar_salida("P1", 12)
        self.assertIn("Paracetamol: 12", self.sistema.generar_reporte(7))

    def test_stock_critico_se_filtra_con_el_umbral(self):
        inv = self.sistema.inventario
        inv.agregar_medicamento(Medicamento("P1", "Paracetamol", 5, fecha_futura(400)))
        inv.agregar_medicamento(Medicamento("A1", "Amoxicilina", 50, fecha_futura(400)))
        criticos = MotorReportes.filtrar_stock_critico(inv.medicamentos, 10)
        self.assertEqual([m.codigo for m in criticos], ["P1"])

    def test_salida_mayor_al_stock_lanza_error(self):
        inv = self.sistema.inventario
        inv.agregar_medicamento(Medicamento("P1", "Paracetamol", 5, fecha_futura(400)))
        with self.assertRaises(StockInsuficienteError):
            inv.registrar_salida("P1", 6)

    def test_consumo_total_suma_las_salidas(self):
        inv = self.sistema.inventario
        inv.agregar_medicamento(Medicamento("P1", "Paracetamol", 100, fecha_futura(400)))
        inv.registrar_salida("P1", 10)
        inv.registrar_salida("P1", 15)
        self.assertEqual(MotorReportes.consumo_total(inv.salidas), 25)

    def test_alerta_de_medicamento_por_vencer(self):
        inv = self.sistema.inventario
        inv.agregar_medicamento(Medicamento("P1", "Paracetamol", 100, fecha_futura(10)))
        self.assertTrue(any("POR VENCER" in a for a in inv.generar_alertas()))
