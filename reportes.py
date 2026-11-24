from datetime import date, timedelta
from functools import reduce

from sistema_rural.config import DIAS_POR_VENCER, UMBRAL_STOCK_CRITICO


class MotorReportes:
    """Parte funcional del sistema: solo funciones que no modifican los datos."""

    @staticmethod
    def filtrar_stock_critico(medicamentos, umbral=UMBRAL_STOCK_CRITICO):
        """Medicamentos con stock menor al umbral (RF-03)."""
        return list(filter(lambda m: m.es_stock_critico(umbral), medicamentos))

    @staticmethod
    def filtrar_por_vencer(medicamentos, dias=DIAS_POR_VENCER):
        return list(filter(lambda m: m.esta_por_vencer(dias), medicamentos))

    @staticmethod
    def morbilidad_por_diagnostico(atenciones):
        """Cuenta cuántas atenciones hubo por cada diagnóstico (RF-05)."""
        return reduce(
            lambda acum, a: {**acum, a.diagnostico: acum.get(a.diagnostico, 0) + 1},
            atenciones,
            {},
        )

    @staticmethod
    def consumo_total(salidas):
        """Suma las unidades de todas las salidas de medicamentos (RF-05)."""
        return reduce(lambda total, s: total + s.cantidad, salidas, 0)

    @staticmethod
    def atenciones_en_rango(atenciones, desde=None, hasta=None):
        return list(
            filter(
                lambda a: (desde is None or a.fecha >= desde) and (hasta is None or a.fecha <= hasta),
                atenciones,
            )
        )

    @staticmethod
    def atenciones_recientes(atenciones, dias):
        return MotorReportes.atenciones_en_rango(atenciones, desde=date.today() - timedelta(days=dias))

    @staticmethod
    def salidas_recientes(salidas, dias):
        limite = date.today() - timedelta(days=dias)
        return list(filter(lambda s: s.fecha >= limite, salidas))

    @staticmethod
    def buscar_pacientes(pacientes, dni="", apellido=""):
        dni = dni.strip()
        apellido = apellido.strip().lower()
        return list(
            filter(lambda p: p.dni.startswith(dni) and apellido in p.apellidos.lower(), pacientes)
        )

    @staticmethod
    def consumo_por_medicamento(salidas):
        return reduce(
            lambda acum, s: {**acum, s.codigo: acum.get(s.codigo, 0) + s.cantidad},
            salidas,
            {},
        )

    @staticmethod
    def resumen_pacientes(pacientes):
        return list(
            map(
                lambda p: {
                    "dni": p.dni,
                    "nombre": p.nombre_completo(),
                    "sexo": p.sexo,
                    "edad": p.edad(),
                    "direccion": p.direccion,
                },
                pacientes,
            )
        )

    @staticmethod
    def detalle_atenciones(atenciones):
        return list(
            map(
                lambda a: {
                    "fecha": a.fecha.isoformat(),
                    "dni": a.paciente.dni,
                    "paciente": a.paciente.nombre_completo(),
                    "profesional": a.profesional.nombre_completo(),
                    "especialidad": a.cita.especialidad,
                    "motivo": a.motivo_consulta,
                    "diagnostico": a.diagnostico,
                    "tratamiento": a.tratamiento,
                },
                atenciones,
            )
        )
