from datetime import date

from tests.base import BaseTest
from sistema_rural.servicios.sistema_rural import cargar_datos_prueba


class TestDatosPrueba(BaseTest):
    def test_carga_pacientes_citas_atencion_e_inventario(self):
        self.assertTrue(cargar_datos_prueba(self.sistema))
        self.assertEqual(len(self.sistema.pacientes), 3)
        self.assertEqual(len(self.sistema.citas), 3)
        self.assertEqual(len(self.sistema.atenciones), 1)
        self.assertEqual(len(self.sistema.inventario.medicamentos), 4)
        self.assertEqual(len(self.sistema.inventario.salidas), 1)

    def test_una_cita_queda_atendida_y_dos_programadas(self):
        cargar_datos_prueba(self.sistema)
        estados = [c.estado for c in self.sistema.citas]
        self.assertEqual(estados.count("ATENDIDA"), 1)
        self.assertEqual(estados.count("PROGRAMADA"), 2)

    def test_datos_prueba_se_identifican_como_ficticios(self):
        cargar_datos_prueba(self.sistema)
        self.assertTrue(all("prueba" in m.nombre.lower()
                            for m in self.sistema.inventario.medicamentos))
        self.assertIn("ficticio", self.sistema.atenciones[0].diagnostico.lower())

    def test_no_duplica_ni_mezcla_si_ya_hay_registros(self):
        cargar_datos_prueba(self.sistema)
        self.assertFalse(cargar_datos_prueba(self.sistema))
        self.assertEqual(len(self.sistema.pacientes), 3)

    def test_no_carga_si_ya_hay_un_paciente_real(self):
        self.sistema.registrar_paciente(
            dni="12345678", nombres="Paciente", apellidos="Real",
            fecha_nacimiento="1990-05-20", sexo="M", direccion="Dirección",
        )
        self.assertFalse(cargar_datos_prueba(self.sistema))
        self.assertEqual(len(self.sistema.pacientes), 1)

    def test_guarda_y_recupera_los_datos_de_prueba(self):
        cargar_datos_prueba(self.sistema)
        self.sistema.guardar()
        otro = type(self.sistema)(self.gestor)
        from sistema_rural.servicios.sistema_rural import cargar_profesionales_demo
        cargar_profesionales_demo(otro)
        otro.cargar()
        self.assertEqual(len(otro.pacientes), 3)
        self.assertEqual(len(otro.citas), 3)
        self.assertEqual(len(otro.atenciones), 1)
        self.assertEqual(len(otro.inventario.medicamentos), 4)

    def test_eliminar_datos_prueba_conserva_json_y_registros_reales(self):
        from pathlib import Path

        cargar_datos_prueba(self.sistema)
        self.sistema.registrar_paciente(
            dni="12345678", nombres="Paciente", apellidos="Real",
            fecha_nacimiento="1990-05-20", sexo="M", direccion="Dirección real",
        )
        self.sistema.guardar()
        ruta_json = self.gestor.ruta
        ruta_clave = ruta_json.parent / "clave.key"
        self.assertTrue(ruta_json.exists())
        self.assertTrue(ruta_clave.exists())

        resumen = self.sistema.eliminar_datos_prueba()
        self.sistema.guardar()

        self.assertEqual(resumen, {
            "pacientes": 3, "citas": 3, "atenciones": 1,
            "medicamentos": 4, "salidas": 1,
        })
        self.assertEqual([p.dni for p in self.sistema.pacientes], ["12345678"])
        self.assertEqual(self.sistema.citas, [])
        self.assertEqual(self.sistema.atenciones, [])
        self.assertEqual(self.sistema.inventario.medicamentos, ())
        self.assertEqual(self.sistema.inventario.salidas, ())
        self.assertTrue(ruta_json.exists(), "El JSON debe conservarse")
        self.assertTrue(ruta_clave.exists(), "La clave debe conservarse")

        otro = type(self.sistema)(self.gestor)
        from sistema_rural.servicios.sistema_rural import cargar_profesionales_demo
        cargar_profesionales_demo(otro)
        otro.cargar()
        self.assertEqual([p.dni for p in otro.pacientes], ["12345678"])

    def test_eliminar_datos_prueba_sin_datos_no_falla(self):
        resumen = self.sistema.eliminar_datos_prueba()
        self.assertTrue(all(cantidad == 0 for cantidad in resumen.values()))
