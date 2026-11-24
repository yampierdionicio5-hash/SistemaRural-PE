import logging
import sys
import tkinter as tk
from tkinter import messagebox

from sistema_rural.excepciones import ErrorRural
from sistema_rural.interfaz.ventana_principal import VentanaPrincipal
from sistema_rural.servicios.persistencia import GestorPersistencia
from sistema_rural.servicios.sistema_rural import (
    SistemaRural, cargar_profesionales_demo, cargar_datos_prueba,
)


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    try:
        gestor = GestorPersistencia.obtener_instancia()
        sistema = SistemaRural(gestor)
        cargar_profesionales_demo(sistema)
        archivo_nuevo = not gestor.ruta.exists()
        sistema.cargar()
        # La demostración se carga una sola vez, en la primera ejecución.
        # Si el JSON existe vacío tras la limpieza, no se vuelven a crear demos.
        if archivo_nuevo and cargar_datos_prueba(sistema):
            sistema.guardar()
    except ErrorRural as error:
        raiz = tk.Tk()
        raiz.withdraw()
        messagebox.showerror("No se pudieron cargar los datos", str(error))
        sys.exit(1)
    VentanaPrincipal(sistema).mainloop()


if __name__ == "__main__":
    main()
