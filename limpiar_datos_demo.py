"""Limpia los registros de demostración sin eliminar el archivo JSON ni la clave.

Ejecutar desde la carpeta raíz del proyecto: python limpiar_datos_demo.py
"""
from sistema_rural.servicios.persistencia import GestorPersistencia
from sistema_rural.servicios.sistema_rural import (
    SistemaRural, cargar_profesionales_demo,
)


def main():
    confirmacion = input(
        "Esto eliminará los registros ficticios identificados del sistema.\n"
        "Escriba ELIMINAR DEMO para continuar: "
    ).strip()
    if confirmacion != "ELIMINAR DEMO":
        print("Operación cancelada. No se modificaron los datos.")
        return

    gestor = GestorPersistencia.obtener_instancia()
    sistema = SistemaRural(gestor)
    cargar_profesionales_demo(sistema)
    sistema.cargar()
    resumen = sistema.eliminar_datos_prueba()
    sistema.guardar()
    print("Limpieza finalizada. Se conservaron datos_rural.json y clave.key.")
    for nombre, cantidad in resumen.items():
        print(f"- {nombre}: {cantidad} eliminado(s)")
    print("Al volver a abrir el programa no se volverán a cargar los datos demo.")


if __name__ == "__main__":
    main()
