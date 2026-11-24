from collections import namedtuple
from datetime import date

from sistema_rural.config import DIAS_POR_VENCER, UMBRAL_STOCK_CRITICO
from sistema_rural.excepciones import DatoInvalidoError, DuplicadoError
from sistema_rural.servicios.reportes import MotorReportes

Salida = namedtuple("Salida", ["codigo", "cantidad", "fecha"])


class Inventario:
    """Agrupa los medicamentos y registra ingresos, salidas y alertas (RF-03)."""
    def __init__(self):
        self._medicamentos = []
        self._salidas = []

    @property
    def medicamentos(self):
        return tuple(self._medicamentos)

    @property
    def salidas(self):
        return tuple(self._salidas)

    def agregar_medicamento(self, medicamento):
        if any(m.codigo == medicamento.codigo for m in self._medicamentos):
            raise DuplicadoError(f"Ya existe un medicamento con el código {medicamento.codigo}.")
        self._medicamentos.append(medicamento)

    def _buscar(self, codigo):
        codigo = codigo.strip()
        medicamento = next((m for m in self._medicamentos if m.codigo == codigo), None)
        if medicamento is None:
            raise DatoInvalidoError(f"No existe un medicamento con el código {codigo}.")
        return medicamento

    def dar_de_baja(self, codigo):
        """Retira del catálogo un medicamento sin stock y conserva sus movimientos."""
        medicamento = self._buscar(codigo)
        if medicamento.stock != 0:
            raise DatoInvalidoError(
                f"No se puede dar de baja {medicamento.nombre}: todavía tiene "
                f"{medicamento.stock} unidades en stock. Registre las salidas correspondientes."
            )
        self._medicamentos.remove(medicamento)
        return medicamento

    def registrar_ingreso(self, codigo, cantidad):
        self._buscar(codigo).aumentar_stock(cantidad)

    def registrar_salida(self, codigo, cantidad):
        medicamento = self._buscar(codigo)
        medicamento.disminuir_stock(cantidad)
        self._salidas.append(Salida(medicamento.codigo, int(cantidad), date.today()))

    def generar_alertas(self, umbral=UMBRAL_STOCK_CRITICO, dias=DIAS_POR_VENCER):
        criticos = map(
            lambda m: f"STOCK CRÍTICO: {m.nombre} ({m.stock} unidades)",
            MotorReportes.filtrar_stock_critico(self._medicamentos, umbral),
        )
        por_vencer = map(
            lambda m: f"POR VENCER: {m.nombre} (vence el {m.fecha_vencimiento.isoformat()})",
            MotorReportes.filtrar_por_vencer(self._medicamentos, dias),
        )
        return list(criticos) + list(por_vencer)

    def cargar(self, medicamentos, salidas):
        self._medicamentos = list(medicamentos)
        self._salidas = list(salidas)

    def salidas_a_diccionarios(self):
        return [
            {"codigo": s.codigo, "cantidad": s.cantidad, "fecha": s.fecha.isoformat()}
            for s in self._salidas
        ]
