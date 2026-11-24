from datetime import date, timedelta

from sistema_rural.dominio.medicamento import Medicamento
from sistema_rural.excepciones import DatoInvalidoError, DuplicadoError, StockInsuficienteError
from tests.base import BaseTest


class TestInventario(BaseTest):
    def test_agregar_medicamento(self):
        medicamento = Medicamento("MED-01", "Gasas", 20,
                                  (date.today() + timedelta(days=200)).isoformat())
        self.sistema.inventario.agregar_medicamento(medicamento)
        self.assertEqual(len(self.sistema.inventario.medicamentos), 1)

    def test_rechaza_codigo_duplicado(self):
        medicamento = Medicamento("MED-01", "Gasas", 20,
                                  (date.today() + timedelta(days=200)).isoformat())
        self.sistema.inventario.agregar_medicamento(medicamento)
        with self.assertRaises(DuplicadoError):
            self.sistema.inventario.agregar_medicamento(medicamento)

    def test_registrar_ingreso_aumenta_stock(self):
        medicamento = Medicamento("MED-01", "Gasas", 10,
                                  (date.today() + timedelta(days=200)).isoformat())
        self.sistema.inventario.agregar_medicamento(medicamento)
        self.sistema.inventario.registrar_ingreso("MED-01", 5)
        self.assertEqual(medicamento.stock, 15)

    def test_registrar_salida_disminuye_stock_y_guarda_movimiento(self):
        medicamento = Medicamento("MED-01", "Gasas", 10,
                                  (date.today() + timedelta(days=200)).isoformat())
        self.sistema.inventario.agregar_medicamento(medicamento)
        self.sistema.inventario.registrar_salida("MED-01", 3)
        self.assertEqual(medicamento.stock, 7)
        self.assertEqual(len(self.sistema.inventario.salidas), 1)
        self.assertEqual(self.sistema.inventario.salidas[0].cantidad, 3)

    def test_rechaza_salida_mayor_al_stock(self):
        medicamento = Medicamento("MED-01", "Gasas", 2,
                                  (date.today() + timedelta(days=200)).isoformat())
        self.sistema.inventario.agregar_medicamento(medicamento)
        with self.assertRaises(StockInsuficienteError):
            self.sistema.inventario.registrar_salida("MED-01", 3)

    def test_buscar_codigo_inexistente_lanza_error(self):
        with self.assertRaises(DatoInvalidoError):
            self.sistema.inventario.registrar_salida("NO-EXISTE", 1)

    def test_alertas_detectan_stock_critico_y_vencimiento(self):
        critico = Medicamento("MED-01", "Gasas", 1,
                              (date.today() + timedelta(days=200)).isoformat())
        vencimiento = Medicamento("MED-02", "Suero", 20,
                                  (date.today() + timedelta(days=5)).isoformat())
        self.sistema.inventario.agregar_medicamento(critico)
        self.sistema.inventario.agregar_medicamento(vencimiento)
        alertas = self.sistema.inventario.generar_alertas()
        self.assertTrue(any("STOCK CRÍTICO" in alerta for alerta in alertas))
        self.assertTrue(any("POR VENCER" in alerta for alerta in alertas))
