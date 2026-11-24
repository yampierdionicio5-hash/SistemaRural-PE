from datetime import date, timedelta

from sistema_rural.config import DIAS_POR_VENCER, UMBRAL_STOCK_CRITICO
from sistema_rural.excepciones import StockInsuficienteError
from sistema_rural.utilidades.validaciones import parsear_fecha, texto_obligatorio, validar_cantidad


class Medicamento:
    """Medicamento del inventario con su stock y su fecha de vencimiento (RF-03)."""
    def __init__(self, codigo, nombre, stock, fecha_vencimiento):
        self._codigo = texto_obligatorio(codigo, "código")
        self._nombre = texto_obligatorio(nombre, "nombre")
        self._stock = validar_cantidad(stock, permitir_cero=True)
        self._fecha_vencimiento = parsear_fecha(fecha_vencimiento)

    @property
    def codigo(self):
        return self._codigo

    @property
    def nombre(self):
        return self._nombre

    @property
    def stock(self):
        return self._stock

    @property
    def fecha_vencimiento(self):
        return self._fecha_vencimiento

    def aumentar_stock(self, cantidad):
        self._stock += validar_cantidad(cantidad)

    def disminuir_stock(self, cantidad):
        cantidad = validar_cantidad(cantidad)
        if cantidad > self._stock:
            raise StockInsuficienteError(
                f"Stock insuficiente de {self._nombre}: hay {self._stock} unidades."
            )
        self._stock -= cantidad

    def es_stock_critico(self, umbral=UMBRAL_STOCK_CRITICO):
        return self._stock < umbral

    def esta_por_vencer(self, dias=DIAS_POR_VENCER):
        return self._fecha_vencimiento <= date.today() + timedelta(days=dias)

    def a_diccionario(self):
        return {
            "codigo": self._codigo,
            "nombre": self._nombre,
            "stock": self._stock,
            "fecha_vencimiento": self._fecha_vencimiento.isoformat(),
        }
