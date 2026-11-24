import logging
import tkinter as tk
from tkinter import messagebox, ttk

from sistema_rural.dominio.medicamento import Medicamento
from sistema_rural.excepciones import ErrorRural

logger = logging.getLogger(__name__)


class VentanaPrincipal(tk.Tk):
    """Interfaz gráfica: cada botón está enlazado a un handler on_*."""

    def __init__(self, sistema):
        super().__init__()
        self.title("SistemaRural-PE - Puesto de Salud Barrio 1, Alto Trujillo")
        self.geometry("1080x700")
        self._sistema = sistema
        self._profesionales = {p.obtener_resumen(): p for p in sistema.profesionales}
        self._construir_pestanas()
        self._refrescar_todo()

    # ---------- utilidades de la interfaz ----------

    @staticmethod
    def _formulario(marco, campos):
        entradas = {}
        for fila, (clave, etiqueta) in enumerate(campos):
            ttk.Label(marco, text=etiqueta).grid(row=fila, column=0, sticky="w", padx=4, pady=2)
            entrada = ttk.Entry(marco, width=34)
            entrada.grid(row=fila, column=1, padx=4, pady=2)
            entradas[clave] = entrada
        return entradas

    @staticmethod
    def _valores(entradas):
        return {clave: entrada.get().strip() for clave, entrada in entradas.items()}

    @staticmethod
    def _limpiar(entradas):
        for entrada in entradas.values():
            entrada.delete(0, tk.END)

    @staticmethod
    def _tabla(marco, columnas, alto=8):
        tabla = ttk.Treeview(marco, columns=[c[0] for c in columnas], show="headings", height=alto)
        for clave, titulo, ancho in columnas:
            tabla.heading(clave, text=titulo)
            tabla.column(clave, width=ancho, anchor="w")
        barra = ttk.Scrollbar(marco, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y", pady=4)
        tabla.pack(fill="both", expand=True, padx=(4, 0), pady=4)
        return tabla

    @staticmethod
    def _llenar(tabla, filas, iids=None):
        tabla.delete(*tabla.get_children())
        for posicion, fila in enumerate(filas):
            # El iid guarda el valor original (por ejemplo el DNI) sin que Tk lo convierta a número.
            tabla.insert("", tk.END, iid=iids[posicion] if iids else None, values=fila)

    @staticmethod
    def _botones(marco, acciones):
        barra = ttk.Frame(marco)
        barra.pack(anchor="w", pady=4)
        for texto, comando in acciones:
            ttk.Button(barra, text=texto, command=comando).pack(side="left", padx=4)

    def _mostrar_texto(self, titulo, texto):
        ventana = tk.Toplevel(self)
        ventana.title(titulo)
        ventana.geometry("720x520")
        caja = tk.Text(ventana, wrap="word")
        caja.insert(tk.END, texto)
        caja.config(state="disabled")
        caja.pack(fill="both", expand=True, padx=6, pady=6)

    def _ejecutar(self, accion, exito=None):
        """Ejecuta una acción, guarda los datos y muestra el resultado al usuario."""
        try:
            accion()
            self._sistema.guardar()
        except ErrorRural as error:
            messagebox.showerror("No se pudo completar la operación", str(error))
            return False
        except Exception:
            logger.exception("Error inesperado")
            messagebox.showerror("Error", "Ocurrió un error inesperado. Revise el registro del sistema.")
            return False
        self._refrescar_todo()
        if exito:
            messagebox.showinfo("Listo", exito)
        return True

    # ---------- construcción de pestañas ----------

    def _construir_pestanas(self):
        pestanas = ttk.Notebook(self)
        pestanas.pack(fill="both", expand=True, padx=6, pady=6)
        self._pestana_pacientes(pestanas)
        self._pestana_citas(pestanas)
        self._pestana_atenciones(pestanas)
        self._pestana_inventario(pestanas)
        self._pestana_reportes(pestanas)

    def _pestana_pacientes(self, pestanas):
        marco = ttk.Frame(pestanas)
        pestanas.add(marco, text="Pacientes")
        formulario = ttk.Frame(marco)
        formulario.pack(anchor="w")
        self._f_paciente = self._formulario(formulario, [
            ("dni", "DNI"), ("nombres", "Nombres"), ("apellidos", "Apellidos"),
            ("fecha_nacimiento", "Nacimiento (AAAA-MM-DD)"), ("sexo", "Sexo (M/F)"),
            ("direccion", "Dirección"),
        ])
        self._botones(marco, [
            ("Registrar", self.on_registrar_paciente),
            ("Actualizar", self.on_actualizar_paciente),
            ("Buscar (DNI / apellidos)", self.on_buscar),
            ("Mostrar todos", self._refrescar_pacientes),
            ("Ver ficha completa", self.on_ver_ficha),
            ("Eliminar paciente", self.on_eliminar_paciente),
        ])
        contenedor = ttk.Frame(marco)
        contenedor.pack(fill="both", expand=True)
        self._tabla_pacientes = self._tabla(contenedor, [
            ("dni", "DNI", 90), ("nombres", "Nombres", 140), ("apellidos", "Apellidos", 160),
            ("nacimiento", "Nacimiento", 95), ("sexo", "Sexo", 45), ("edad", "Edad", 45),
            ("direccion", "Dirección", 300),
        ])
        self._tabla_pacientes.bind("<Double-1>", lambda evento: self.on_ver_ficha())

    def _pestana_citas(self, pestanas):
        marco = ttk.Frame(pestanas)
        pestanas.add(marco, text="Citas")
        formulario = ttk.Frame(marco)
        formulario.pack(anchor="w")
        self._f_cita = self._formulario(formulario, [
            ("dni", "DNI del paciente"), ("fecha", "Fecha (AAAA-MM-DD)"),
            ("id_cita", "ID de cita (para reprogramar o cancelar)"),
        ])
        ttk.Label(formulario, text="Profesional").grid(row=3, column=0, sticky="w", padx=4, pady=2)
        self._combo_profesional = ttk.Combobox(
            formulario, width=45, state="readonly", values=list(self._profesionales),
        )
        self._combo_profesional.grid(row=3, column=1, padx=4, pady=2)
        self._combo_profesional.bind("<<ComboboxSelected>>", lambda evento: self._mostrar_especialidad())
        ttk.Label(formulario, text="Especialidad").grid(row=4, column=0, sticky="w", padx=4, pady=2)
        self._etiqueta_especialidad = ttk.Label(formulario, text="(se completa al elegir al profesional)")
        self._etiqueta_especialidad.grid(row=4, column=1, sticky="w", padx=4, pady=2)
        self._botones(marco, [
            ("Programar", self.on_programar_cita),
            ("Reprogramar", self.on_reprogramar_cita),
            ("Cancelar", self.on_cancelar_cita),
        ])
        contenedor = ttk.Frame(marco)
        contenedor.pack(fill="both", expand=True)
        self._tabla_citas = self._tabla(contenedor, [
            ("id", "ID", 40), ("fecha", "Fecha", 90), ("dni", "DNI", 90), ("paciente", "Paciente", 200),
            ("profesional", "Profesional", 200), ("especialidad", "Especialidad", 140), ("estado", "Estado", 100),
        ])

    def _pestana_atenciones(self, pestanas):
        marco = ttk.Frame(pestanas)
        pestanas.add(marco, text="Atenciones")
        formulario = ttk.Frame(marco)
        formulario.pack(anchor="w")
        self._f_atencion = self._formulario(formulario, [
            ("id_cita", "ID de cita"), ("motivo", "Motivo de consulta"),
            ("diagnostico", "Diagnóstico"), ("tratamiento", "Tratamiento"),
        ])
        self._botones(marco, [("Registrar atención", self.on_registrar_atencion)])
        filtro = ttk.Frame(marco)
        filtro.pack(anchor="w", pady=(8, 0))
        self._f_rango = self._formulario(filtro, [("desde", "Desde (AAAA-MM-DD)"), ("hasta", "Hasta (AAAA-MM-DD)")])
        self._botones(marco, [
            ("Buscar atenciones por fecha", self.on_buscar_atenciones),
            ("Mostrar todas", self._refrescar_atenciones),
        ])
        contenedor = ttk.Frame(marco)
        contenedor.pack(fill="both", expand=True)
        self._tabla_atenciones = self._tabla(contenedor, [
            ("fecha", "Fecha", 85), ("dni", "DNI", 85), ("paciente", "Paciente", 150),
            ("profesional", "Profesional", 130), ("motivo", "Motivo", 150),
            ("diagnostico", "Diagnóstico", 140), ("tratamiento", "Tratamiento", 160),
        ], alto=6)

    def _pestana_inventario(self, pestanas):
        marco = ttk.Frame(pestanas)
        pestanas.add(marco, text="Inventario")
        formulario = ttk.Frame(marco)
        formulario.pack(anchor="w")
        self._f_med = self._formulario(formulario, [
            ("codigo", "Código"), ("nombre", "Nombre"), ("cantidad", "Cantidad"),
            ("vence", "Vence (AAAA-MM-DD)"),
        ])
        self._botones(marco, [
            ("Nuevo medicamento", self.on_nuevo_medicamento),
            ("Registrar ingreso", self.on_ingreso),
            ("Registrar salida", self.on_salida),
            ("Dar de baja medicamento", self.on_baja_medicamento),
        ])
        contenedor = ttk.Frame(marco)
        contenedor.pack(fill="both", expand=True)
        self._tabla_inventario = self._tabla(contenedor, [
            ("codigo", "Código", 90), ("nombre", "Nombre", 250), ("stock", "Stock", 80), ("vence", "Vencimiento", 120),
        ], alto=7)
        self._alertas = ttk.Label(marco, text="", foreground="red", justify="left")
        self._alertas.pack(anchor="w", padx=4)

    def _pestana_reportes(self, pestanas):
        marco = ttk.Frame(pestanas)
        pestanas.add(marco, text="Reportes")
        self._botones(marco, [
            ("Reporte semanal", lambda: self.on_generar_reporte(7)),
            ("Reporte mensual", lambda: self.on_generar_reporte(30)),
        ])
        self._texto_reporte = tk.Text(marco, height=22, state="disabled")
        self._texto_reporte.pack(fill="both", expand=True, padx=4, pady=4)

    # ---------- refresco de tablas ----------

    def _mostrar_especialidad(self):
        profesional = self._profesionales.get(self._combo_profesional.get())
        if profesional:
            self._etiqueta_especialidad.config(text=profesional.especialidad)

    def _refrescar_pacientes(self, pacientes=None):
        pacientes = self._sistema.pacientes if pacientes is None else pacientes
        self._llenar(
            self._tabla_pacientes,
            [(p.dni, p.nombres, p.apellidos, p.fecha_nacimiento.isoformat(), p.sexo, p.edad(), p.direccion)
             for p in pacientes],
            iids=[p.dni for p in pacientes],
        )

    def _refrescar_atenciones(self, atenciones=None):
        atenciones = self._sistema.atenciones if atenciones is None else atenciones
        self._llenar(self._tabla_atenciones, [
            (a.fecha.isoformat(), a.paciente.dni, a.paciente.nombre_completo(),
             a.profesional.nombre_completo(), a.motivo_consulta, a.diagnostico, a.tratamiento)
            for a in atenciones
        ])

    def _refrescar_todo(self):
        self._refrescar_pacientes()
        self._refrescar_atenciones()
        self._llenar(self._tabla_citas, [
            (c.id_cita, c.fecha.isoformat(), c.paciente.dni, c.paciente.nombre_completo(),
             c.profesional.nombre_completo(), c.especialidad, c.estado)
            for c in self._sistema.citas
        ])
        medicamentos = self._sistema.inventario.medicamentos
        self._llenar(
            self._tabla_inventario,
            [(m.codigo, m.nombre, m.stock, m.fecha_vencimiento.isoformat())
             for m in medicamentos],
            iids=[m.codigo for m in medicamentos],
        )
        self._alertas.config(text="\n".join(self._sistema.inventario.generar_alertas()))

    # ---------- handlers de eventos ----------

    def on_eliminar_paciente(self):
        seleccion = self._tabla_pacientes.selection()
        if not seleccion:
            messagebox.showinfo("Eliminar paciente", "Seleccione un paciente de la tabla.")
            return
        dni = seleccion[0]
        try:
            paciente = self._sistema.obtener_paciente(dni)
        except ErrorRural as error:
            messagebox.showerror("No se pudo completar la operación", str(error))
            return
        confirmado = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Desea eliminar al paciente {paciente.nombre_completo()} (DNI {dni})?\n\n"
            "Solo se puede eliminar si no tiene citas ni atenciones registradas.",
        )
        if confirmado:
            self._ejecutar(lambda: self._sistema.eliminar_paciente(dni),
                           "Paciente eliminado correctamente.")

    def on_registrar_paciente(self):
        """Evento: registra al paciente con los datos del formulario (RF-01)."""
        def accion():
            self._sistema.registrar_paciente(**self._valores(self._f_paciente))
            self._limpiar(self._f_paciente)
        self._ejecutar(accion, "Paciente registrado correctamente.")

    def on_actualizar_paciente(self):
        def accion():
            v = self._valores(self._f_paciente)
            self._sistema.actualizar_paciente(v["dni"], v["nombres"], v["apellidos"], v["direccion"])
            self._limpiar(self._f_paciente)
        self._ejecutar(accion, "Datos del paciente actualizados.")

    def on_buscar(self):
        v = self._valores(self._f_paciente)
        self._refrescar_pacientes(self._sistema.buscar_pacientes(v["dni"], v["apellidos"]))

    def on_ver_ficha(self):
        seleccion = self._tabla_pacientes.selection()
        if not seleccion:
            messagebox.showinfo("Ficha del paciente", "Seleccione un paciente de la tabla.")
            return
        try:
            texto = self._sistema.ficha_paciente(seleccion[0])
        except ErrorRural as error:
            messagebox.showerror("No se pudo completar la operación", str(error))
            return
        self._mostrar_texto("Ficha completa del paciente", texto)

    def on_programar_cita(self):
        resultado = {}

        def accion():
            profesional = self._profesionales.get(self._combo_profesional.get())
            if profesional is None:
                raise ErrorRural("Seleccione un profesional de salud.")
            v = self._valores(self._f_cita)
            cita = self._sistema.programar_cita(v["dni"], profesional.nro_colegiatura, v["fecha"])
            self._limpiar(self._f_cita)
            resultado["id"] = cita.id_cita
        if self._ejecutar(accion):
            messagebox.showinfo("Listo", f"Cita programada. ID de la cita: {resultado['id']}")

    def on_reprogramar_cita(self):
        def accion():
            v = self._valores(self._f_cita)
            self._sistema.obtener_cita(v["id_cita"]).reprogramar(v["fecha"])
        self._ejecutar(accion, "Cita reprogramada.")

    def on_cancelar_cita(self):
        def accion():
            self._sistema.obtener_cita(self._valores(self._f_cita)["id_cita"]).cancelar()
        self._ejecutar(accion, "Cita cancelada.")

    def on_registrar_atencion(self):
        def accion():
            v = self._valores(self._f_atencion)
            self._sistema.registrar_atencion(v["id_cita"], v["motivo"], v["diagnostico"], v["tratamiento"])
            self._limpiar(self._f_atencion)
        self._ejecutar(accion, "Atención clínica registrada.")

    def on_buscar_atenciones(self):
        try:
            v = self._valores(self._f_rango)
            self._refrescar_atenciones(self._sistema.buscar_atenciones(v["desde"], v["hasta"]))
        except ErrorRural as error:
            messagebox.showerror("No se pudo completar la operación", str(error))

    def on_nuevo_medicamento(self):
        def accion():
            v = self._valores(self._f_med)
            self._sistema.inventario.agregar_medicamento(
                Medicamento(v["codigo"], v["nombre"], v["cantidad"], v["vence"])
            )
            self._limpiar(self._f_med)
        self._ejecutar(accion, "Medicamento registrado.")

    def on_ingreso(self):
        def accion():
            v = self._valores(self._f_med)
            self._sistema.inventario.registrar_ingreso(v["codigo"], v["cantidad"])
        self._ejecutar(accion, "Ingreso registrado.")

    def on_salida(self):
        def accion():
            v = self._valores(self._f_med)
            self._sistema.inventario.registrar_salida(v["codigo"], v["cantidad"])
        self._ejecutar(accion, "Salida registrada.")

    def on_baja_medicamento(self):
        seleccion = self._tabla_inventario.selection()
        if not seleccion:
            messagebox.showinfo("Dar de baja medicamento", "Seleccione un medicamento de la tabla.")
            return
        codigo = seleccion[0]
        medicamento = next((m for m in self._sistema.inventario.medicamentos
                            if m.codigo == codigo), None)
        if medicamento is None:
            messagebox.showerror("No encontrado", "No se encontró el medicamento seleccionado.")
            return
        confirmado = messagebox.askyesno(
            "Confirmar baja",
            f"¿Desea dar de baja {medicamento.nombre} ({codigo})?\n\n"
            "Solo se permite cuando el stock es cero. El historial de movimientos se conservará.",
        )
        if confirmado:
            self._ejecutar(lambda: self._sistema.inventario.dar_de_baja(codigo),
                           "Medicamento dado de baja. El historial se conservó.")

    def on_generar_reporte(self, dias):
        texto = self._sistema.generar_reporte(dias)
        self._texto_reporte.config(state="normal")
        self._texto_reporte.delete("1.0", tk.END)
        self._texto_reporte.insert(tk.END, texto)
        self._texto_reporte.config(state="disabled")
