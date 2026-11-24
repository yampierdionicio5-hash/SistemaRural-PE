from datetime import date, timedelta

from sistema_rural.dominio.atencion_clinica import AtencionClinica
from sistema_rural.dominio.cita_medica import CitaMedica
from sistema_rural.dominio.inventario import Inventario, Salida
from sistema_rural.dominio.medicamento import Medicamento
from sistema_rural.dominio.persona_factory import PersonaFactory
from sistema_rural.excepciones import DatoInvalidoError, DuplicadoError
from sistema_rural.servicios.reportes import MotorReportes
from sistema_rural.utilidades.validaciones import parsear_fecha

CAMPOS_PACIENTE = ("dni", "nombres", "apellidos", "fecha_nacimiento", "sexo", "direccion")
CAMPOS_CITA = ("dni_paciente",)
CAMPOS_ATENCION = ("motivo_consulta", "diagnostico", "tratamiento")


class SistemaRural:
    """Coordina las entidades del dominio y la persistencia."""

    def __init__(self, gestor):
        self._gestor = gestor
        self._pacientes = {}
        self._profesionales = {}
        self._citas = {}
        self._atenciones = []
        self.inventario = Inventario()

    @property
    def pacientes(self):
        return list(self._pacientes.values())

    @property
    def profesionales(self):
        return list(self._profesionales.values())

    @property
    def citas(self):
        return list(self._citas.values())

    @property
    def atenciones(self):
        return list(self._atenciones)

    def registrar_profesional(self, **datos):
        profesional = PersonaFactory.crear("profesional", **datos)
        self._profesionales[profesional.nro_colegiatura] = profesional
        return profesional

    def registrar_paciente(self, **datos):
        paciente = PersonaFactory.crear("paciente", **datos)
        if paciente.dni in self._pacientes:
            raise DuplicadoError("Ya existe un paciente registrado con ese DNI.")
        self._pacientes[paciente.dni] = paciente
        return paciente

    def obtener_paciente(self, dni):
        paciente = self._pacientes.get(dni.strip())
        if paciente is None:
            raise DatoInvalidoError("No se encontró un paciente con ese DNI.")
        return paciente

    def eliminar_paciente(self, dni):
        """Elimina un paciente solo si no tiene citas ni historial clínico."""
        paciente = self.obtener_paciente(dni)
        if any(c.paciente.dni == paciente.dni for c in self._citas.values()):
            raise DatoInvalidoError(
                "No se puede eliminar este paciente porque tiene citas registradas "
                "(incluidas las canceladas). Se conserva para proteger su historial."
            )
        if any(a.paciente.dni == paciente.dni for a in self._atenciones):
            raise DatoInvalidoError(
                "No se puede eliminar este paciente porque tiene atenciones en su historial clínico."
            )
        del self._pacientes[paciente.dni]
        return paciente

    def actualizar_paciente(self, dni, nombres="", apellidos="", direccion=""):
        paciente = self.obtener_paciente(dni)
        if nombres:
            paciente.nombres = nombres
        if apellidos:
            paciente.apellidos = apellidos
        if direccion:
            paciente.direccion = direccion
        return paciente

    def buscar_pacientes(self, dni="", apellido=""):
        return MotorReportes.buscar_pacientes(self.pacientes, dni, apellido)

    def programar_cita(self, dni, nro_colegiatura, fecha, especialidad=None):
        paciente = self.obtener_paciente(dni)
        profesional = self._profesionales.get(nro_colegiatura.strip())
        if profesional is None:
            raise DatoInvalidoError("No se encontró al profesional de salud.")
        id_cita = max(self._citas, default=0) + 1
        # Si no se indica, la cita toma la especialidad del profesional elegido.
        especialidad = especialidad or profesional.especialidad
        cita = CitaMedica(id_cita, paciente, profesional, fecha, especialidad)
        cita.programar()
        self._citas[id_cita] = cita
        return cita

    def obtener_cita(self, id_cita):
        try:
            return self._citas[int(id_cita)]
        except (KeyError, ValueError):
            raise DatoInvalidoError("No existe una cita con ese ID.")

    def registrar_atencion(self, id_cita, motivo, diagnostico, tratamiento):
        cita = self.obtener_cita(id_cita)
        atencion = AtencionClinica(cita, motivo, diagnostico, tratamiento)
        atencion.registrar()
        self._atenciones.append(atencion)
        return atencion

    def buscar_atenciones(self, desde="", hasta=""):
        inicio = parsear_fecha(desde) if desde else None
        fin = parsear_fecha(hasta) if hasta else None
        return MotorReportes.atenciones_en_rango(self._atenciones, inicio, fin)

    def generar_reporte(self, dias):
        """Arma el texto del reporte semanal (7) o mensual (30) con datos de pacientes."""
        desde = date.today() - timedelta(days=dias)
        atenciones = MotorReportes.atenciones_recientes(self._atenciones, dias)
        salidas = MotorReportes.salidas_recientes(self.inventario.salidas, dias)
        morbilidad = sorted(
            MotorReportes.morbilidad_por_diagnostico(atenciones).items(),
            key=lambda par: par[1], reverse=True,
        )
        nombres = {m.codigo: m.nombre for m in self.inventario.medicamentos}
        consumo = MotorReportes.consumo_por_medicamento(salidas)

        lineas = [f"REPORTE DE LOS ÚLTIMOS {dias} DÍAS (desde {desde.isoformat()})", ""]
        lineas.append(f"1. ATENCIONES REALIZADAS ({len(atenciones)})")
        for d in MotorReportes.detalle_atenciones(atenciones):
            lineas.append(f"  {d['fecha']} | DNI {d['dni']} | {d['paciente']}")
            lineas.append(f"     Atendió: {d['profesional']} ({d['especialidad']})")
            lineas.append(f"     Motivo: {d['motivo']} | Diagnóstico: {d['diagnostico']} | Tratamiento: {d['tratamiento']}")
        if not atenciones:
            lineas.append("  (sin atenciones en el período)")
        lineas += ["", "2. MORBILIDAD POR DIAGNÓSTICO"]
        lineas += [f"  - {diagnostico}: {total}" for diagnostico, total in morbilidad] or ["  (sin datos)"]
        lineas += ["", f"3. CONSUMO DE MEDICAMENTOS (total: {MotorReportes.consumo_total(salidas)} unidades)"]
        lineas += [f"  - {nombres.get(codigo, codigo)}: {cantidad}" for codigo, cantidad in consumo.items()] or ["  (sin salidas)"]
        pacientes = MotorReportes.resumen_pacientes(self.pacientes)
        lineas += ["", f"4. PACIENTES REGISTRADOS ({len(pacientes)})"]
        lineas += [
            f"  {p['dni']} | {p['nombre']} | {p['sexo']} | {p['edad']} años | {p['direccion']}"
            for p in pacientes
        ] or ["  (sin pacientes)"]
        return "\n".join(lineas)

    def ficha_paciente(self, dni):
        """Datos completos del paciente, sus citas y su historial de atenciones."""
        p = self.obtener_paciente(dni)
        citas = sorted(filter(lambda c: c.paciente.dni == p.dni, self._citas.values()), key=lambda c: c.fecha)
        atenciones = list(filter(lambda a: a.paciente.dni == p.dni, self._atenciones))
        lineas = [
            "DATOS DEL PACIENTE",
            f"  DNI: {p.dni}",
            f"  Nombres y apellidos: {p.nombre_completo()}",
            f"  Fecha de nacimiento: {p.fecha_nacimiento.isoformat()} ({p.edad()} años)",
            f"  Sexo: {p.sexo}",
            f"  Dirección: {p.direccion}",
            "", f"CITAS ({len(citas)})",
        ]
        lineas += [
            f"  #{c.id_cita} | {c.fecha.isoformat()} | {c.profesional.nombre_completo()} ({c.especialidad}) | {c.estado}"
            for c in citas
        ] or ["  (sin citas)"]
        lineas += ["", f"HISTORIAL DE ATENCIONES ({len(atenciones)})"]
        for d in MotorReportes.detalle_atenciones(atenciones):
            lineas.append(f"  {d['fecha']} | {d['especialidad']} | Atendió: {d['profesional']}")
            lineas.append(f"     Motivo: {d['motivo']}")
            lineas.append(f"     Diagnóstico: {d['diagnostico']}")
            lineas.append(f"     Tratamiento: {d['tratamiento']}")
        if not atenciones:
            lineas.append("  (sin atenciones)")
        return "\n".join(lineas)

    def eliminar_datos_prueba(self):
        """Elimina únicamente los registros de demostración identificados por sus códigos.

        Conserva los registros ajenos a la demostración y no elimina el archivo JSON
        ni la clave de seguridad. Devuelve un resumen de lo eliminado.
        """
        pacientes_demo = {
            "70000001": ("María", "Quispe Soto"),
            "70000002": ("José", "Ramos León"),
            "70000003": ("Rosa", "Vega Díaz"),
        }
        nombres_medicamentos_demo = {
            "DEM-001": "Paracetamol 500 mg (prueba)",
            "DEM-002": "Amoxicilina 500 mg (prueba)",
            "DEM-003": "Sales de rehidratación oral (prueba)",
            "DEM-004": "Alcohol medicinal (prueba)",
        }
        # Verifica también los nombres: no basta con coincidir en DNI/código.
        dnis_demo = {
            dni for dni, paciente in self._pacientes.items()
            if dni in pacientes_demo
            and (paciente.nombres, paciente.apellidos) == pacientes_demo[dni]
        }
        codigos_demo = {
            codigo for codigo, nombre in nombres_medicamentos_demo.items()
            if any(m.codigo == codigo and m.nombre == nombre
                   for m in self.inventario.medicamentos)
        }

        pacientes_antes = len(self._pacientes)
        citas_antes = len(self._citas)
        atenciones_antes = len(self._atenciones)
        medicamentos_antes = len(self.inventario.medicamentos)
        salidas_antes = len(self.inventario.salidas)

        ids_citas_demo = {
            id_cita for id_cita, cita in self._citas.items()
            if cita.paciente.dni in dnis_demo
        }
        self._atenciones = [
            atencion for atencion in self._atenciones
            if atencion.paciente.dni not in dnis_demo
        ]
        self._citas = {
            id_cita: cita for id_cita, cita in self._citas.items()
            if id_cita not in ids_citas_demo
        }
        self._pacientes = {
            dni: paciente for dni, paciente in self._pacientes.items()
            if dni not in dnis_demo
        }

        medicamentos = [
            medicamento for medicamento in self.inventario.medicamentos
            if medicamento.codigo not in codigos_demo
        ]
        salidas = [
            salida for salida in self.inventario.salidas
            if salida.codigo not in codigos_demo
        ]
        self.inventario.cargar(medicamentos, salidas)

        return {
            "pacientes": pacientes_antes - len(self._pacientes),
            "citas": citas_antes - len(self._citas),
            "atenciones": atenciones_antes - len(self._atenciones),
            "medicamentos": medicamentos_antes - len(self.inventario.medicamentos),
            "salidas": salidas_antes - len(self.inventario.salidas),
        }

    def guardar(self):
        g = self._gestor
        g.guardar("pacientes", [p.a_diccionario() for p in self.pacientes], CAMPOS_PACIENTE)
        g.guardar("citas", [c.a_diccionario() for c in self.citas], CAMPOS_CITA)
        g.guardar("atenciones", [a.a_diccionario() for a in self._atenciones], CAMPOS_ATENCION)
        g.guardar("medicamentos", [m.a_diccionario() for m in self.inventario.medicamentos])
        g.guardar("salidas", self.inventario.salidas_a_diccionarios())

    def cargar(self):
        g = self._gestor
        for datos in g.cargar("pacientes", CAMPOS_PACIENTE):
            self.registrar_paciente(**datos)

        for datos in g.cargar("citas", CAMPOS_CITA):
            paciente = self._pacientes.get(datos["dni_paciente"])
            profesional = self._profesionales.get(datos["nro_colegiatura"])
            if paciente and profesional:
                id_cita = int(datos["id_cita"])
                self._citas[id_cita] = CitaMedica(
                    id_cita, paciente, profesional,
                    datos["fecha"], datos["especialidad"], datos["estado"],
                )

        for datos in g.cargar("atenciones", CAMPOS_ATENCION):
            cita = self._citas.get(int(datos["id_cita"]))
            if cita:
                self._atenciones.append(
                    AtencionClinica(cita, datos["motivo_consulta"], datos["diagnostico"], datos["tratamiento"])
                )

        medicamentos = [Medicamento(**datos) for datos in g.cargar("medicamentos")]
        salidas = [
            Salida(d["codigo"], int(d["cantidad"]), parsear_fecha(d["fecha"]))
            for d in g.cargar("salidas")
        ]
        self.inventario.cargar(medicamentos, salidas)


def cargar_profesionales_demo(sistema):
    """Profesionales ficticios para la demostración (no son datos reales)."""
    sistema.registrar_profesional(
        dni="40111222", nombres="Ana", apellidos="Torres Vega",
        fecha_nacimiento="1985-04-12", sexo="F",
        nro_colegiatura="CMP-10001", especialidad="Medicina General",
    )
    sistema.registrar_profesional(
        dni="40333444", nombres="Luis", apellidos="Mendoza Rojas",
        fecha_nacimiento="1982-09-30", sexo="M",
        nro_colegiatura="CMP-10002", especialidad="Obstetricia",
    )


def cargar_datos_prueba(sistema):
    """Carga registros ficticios para probar los módulos en una instalación vacía.

    No reemplaza ni mezcla información existente. Los datos se guardan al llamar
    a sistema.guardar() desde el punto de entrada de la aplicación.
    """
    if (sistema.pacientes or sistema.citas or sistema.atenciones
            or sistema.inventario.medicamentos or sistema.inventario.salidas):
        return False

    pacientes = [
        dict(dni="70000001", nombres="María", apellidos="Quispe Soto",
             fecha_nacimiento="1992-03-14", sexo="F", direccion="Sector A - Alto Trujillo"),
        dict(dni="70000002", nombres="José", apellidos="Ramos León",
             fecha_nacimiento="1980-07-22", sexo="M", direccion="Sector B - Alto Trujillo"),
        dict(dni="70000003", nombres="Rosa", apellidos="Vega Díaz",
             fecha_nacimiento="2001-11-05", sexo="F", direccion="Sector C - Alto Trujillo"),
    ]
    for datos in pacientes:
        sistema.registrar_paciente(**datos)

    hoy = date.today()
    citas = [
        sistema.programar_cita("70000001", "CMP-10001", hoy.isoformat()),
        sistema.programar_cita("70000002", "CMP-10002", (hoy + timedelta(days=2)).isoformat()),
        sistema.programar_cita("70000003", "CMP-10001", (hoy + timedelta(days=5)).isoformat()),
    ]
    sistema.registrar_atencion(
        citas[0].id_cita, "Consulta de prueba", "Diagnóstico ficticio",
        "Registro demostrativo; no constituye indicación médica",
    )

    medicamentos = [
        Medicamento("DEM-001", "Paracetamol 500 mg (prueba)", 45,
                    (hoy + timedelta(days=300)).isoformat()),
        Medicamento("DEM-002", "Amoxicilina 500 mg (prueba)", 0,
                    (hoy + timedelta(days=240)).isoformat()),
        Medicamento("DEM-003", "Sales de rehidratación oral (prueba)", 28,
                    (hoy + timedelta(days=20)).isoformat()),
        Medicamento("DEM-004", "Alcohol medicinal (prueba)", 60,
                    (hoy + timedelta(days=500)).isoformat()),
    ]
    for medicamento in medicamentos:
        sistema.inventario.agregar_medicamento(medicamento)
    sistema.inventario.registrar_salida("DEM-001", 5)
    sistema.inventario.registrar_ingreso("DEM-002", 6)
    return True
