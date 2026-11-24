from sistema_rural.dominio.medicamento import Medicamento
from sistema_rural.excepciones import DatoInvalidoError
from tests.base import BaseTest
from sistema_rural.servicios.sistema_rural import cargar_datos_prueba


class TestEliminacionesSeguras(BaseTest):
    def test_eliminar_paciente_sin_citas_ni_historial(self):
        paciente = self.sistema.registrar_paciente(
            dni="12345678", nombres="Eva", apellidos="Prueba",
            fecha_nacimiento="1990-05-20", sexo="F", direccion="Sector 1",
        )
        self.sistema.eliminar_paciente(paciente.dni)
        self.assertEqual(self.sistema.pacientes, [])

    def test_no_eliminar_paciente_con_citas_aunque_esten_canceladas(self):
        cargar_datos_prueba(self.sistema)
        cita = self.sistema.citas[1]
        cita.cancelar()
        with self.assertRaises(DatoInvalidoError):
            self.sistema.eliminar_paciente("70000002")
        self.assertEqual(len(self.sistema.pacientes), 3)

    def test_no_eliminar_paciente_con_atencion_clinica(self):
        cargar_datos_prueba(self.sistema)
        with self.assertRaises(DatoInvalidoError):
            self.sistema.eliminar_paciente("70000001")

    def test_baja_medicamento_sin_stock_conserva_movimientos(self):
        medicamento = Medicamento("MED-000", "Medicamento", 0, "2027-12-31")
        self.sistema.inventario.agregar_medicamento(medicamento)
        self.sistema.inventario.dar_de_baja("MED-000")
        self.assertEqual(self.sistema.inventario.medicamentos, ())

    def test_no_dar_de_baja_medicamento_con_stock(self):
        medicamento = Medicamento("MED-001", "Medicamento", 5, "2027-12-31")
        self.sistema.inventario.agregar_medicamento(medicamento)
        with self.assertRaises(DatoInvalidoError):
            self.sistema.inventario.dar_de_baja("MED-001")
        self.assertEqual(len(self.sistema.inventario.medicamentos), 1)

    def test_json_se_conserva_despues_de_eliminar_paciente(self):
        self.sistema.registrar_paciente(
            dni="12345678", nombres="Eva", apellidos="Prueba",
            fecha_nacimiento="1990-05-20", sexo="F", direccion="Sector 1",
        )
        self.sistema.guardar()
        ruta = self.gestor.ruta
        self.sistema.eliminar_paciente("12345678")
        self.sistema.guardar()
        self.assertTrue(ruta.exists())
        self.assertEqual(self.gestor.cargar("pacientes", ("dni", "nombres", "apellidos", "fecha_nacimiento", "sexo", "direccion")), [])
