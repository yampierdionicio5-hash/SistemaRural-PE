# SistemaRural-PE

Módulo de gestión para el Puesto de Salud del Barrio 1 – Alto Trujillo.
Curso: Lenguajes de Programación (UAIN1288P).

## Cómo ejecutarlo
No requiere instalar nada: solo Python 3.x (Tkinter viene incluido en Windows).
```
python main.py
```
En Linux puede hacer falta `sudo apt install python3-tk`.

## Pruebas automatizadas
```
python -m unittest discover -s tests -v
```
(también corren con `pytest` si está instalado)

## Estructura
```
main.py                         punto de entrada
sistema_rural/
  config.py                     constantes y rutas
  excepciones.py                errores propios
  dominio/                      POO: una clase por archivo (igual al diagrama UML)
    persona.py  paciente.py  profesional_salud.py  persona_factory.py
    cita_medica.py  atencion_clinica.py  medicamento.py  inventario.py
  servicios/
    reportes.py                 MotorReportes (programación funcional)
    seguridad.py                ServicioSeguridad (cifrado de datos personales)
    persistencia.py             GestorPersistencia (Singleton, JSON)
    sistema_rural.py            SistemaRural (coordina dominio + persistencia)
  interfaz/
    ventana_principal.py        VentanaPrincipal (Tkinter, eventos)
  utilidades/
    validaciones.py
tests/                          pruebas automatizadas
```

## ¿Dónde y cómo se guardan los datos?
- Carpeta `datos/` junto al proyecto (se crea sola; la ruta se calcula desde `config.py`,
  así que no depende de desde dónde se ejecute).
- `datos/datos_rural.json`: un solo archivo con las colecciones `pacientes`, `citas`,
  `atenciones`, `medicamentos` y `salidas`.
- `datos/clave.key`: clave de cifrado, generada la primera vez.
- Los datos personales y clínicos (DNI, nombres, apellidos, fecha de nacimiento, dirección,
  motivo, diagnóstico, tratamiento) se cifran antes de escribirse. En el JSON solo hay texto
  ilegible. Los medicamentos no son datos personales y quedan en claro.
- Cada operación exitosa en la interfaz llama a `SistemaRural.guardar()`; al abrir el
  programa, `SistemaRural.cargar()` lee el JSON y descifra los campos.
- Se escribe en un archivo temporal y luego se reemplaza el original (`os.replace`) para no
  dejar el JSON a medias si se corta la luz.
- Si se pierde `clave.key`, los datos cifrados no se pueden recuperar: se respaldan juntos.
  Ninguno de los dos va a Git (ver `.gitignore`).
- En pantalla y en los reportes se muestran los datos completos al personal autorizado; la
  protección se aplica en el almacenamiento (cifrado) y en los registros internos (logs), donde
  no se escriben datos personales. `ServicioSeguridad.enmascarar_dni` se usa solo para logs.

## Cumplimiento de la rúbrica EF (implementación del módulo)
| Exigencia | Dónde está |
|---|---|
| 2 o más paradigmas | POO en `dominio/`, funcional en `servicios/reportes.py`, eventos en `interfaz/` |
| Encapsulamiento completo | Atributos privados (`_dni`, `_stock`...) con propiedades y setters validados en `dominio/` |
| 2 o más funciones de orden superior | `filter`, `map`, `reduce`, `sorted(key=lambda)` en `reportes.py`, `inventario.py` y la interfaz |
| Manejo de errores y excepciones | `excepciones.py`; la interfaz captura `ErrorRural` y muestra el mensaje |
| Datos personales sin texto plano | `servicios/seguridad.py` + `persistencia.py` (JSON cifrado); `__repr__` y logs sin datos; prueba que verifica el JSON |
| Git con 10 o más commits en español | Ver `GUIA_GIT.md` |
| Pruebas automatizadas | `tests/` (53 pruebas) |

## Ver todo
- Pacientes: tabla con todos los datos; doble clic o «Ver ficha completa» muestra datos, citas e historial.
- Atenciones: «Mostrar todas» quita el filtro por fechas.
- Reportes: semanal y mensual con atenciones (paciente, profesional, diagnóstico, tratamiento), morbilidad, consumo y pacientes.

## Datos de demostración
Los dos profesionales de salud (CMP-10001 y CMP-10002) son ficticios.


## Registros de prueba y limpieza
En la primera ejecución, si todavía no existe `datos/datos_rural.json`, el sistema
carga registros ficticios para mostrar los módulos (pacientes, citas, atención e inventario).
La carga inicial ocurre una sola vez: si el JSON existe vacío después de limpiar, no se
volverán a insertar automáticamente.

Después de la demostración, para retirar únicamente los registros ficticios identificados,
cierra la aplicación y ejecuta desde la carpeta raíz:

```
python limpiar_datos_demo.py
```

El script solicita escribir `ELIMINAR DEMO` antes de continuar. Elimina los pacientes de
prueba identificados por DNI 70000001–70000003, sus citas y atenciones, y los medicamentos
DEM-001 a DEM-004 con sus movimientos. Conserva otros registros y **no elimina**
`datos/datos_rural.json` ni `datos/clave.key`. Haz una copia de seguridad antes de limpiar.

## Eliminaciones desde la interfaz
- **Pacientes:** selecciona una fila y pulsa «Eliminar paciente». Solo se permite si no
  tiene citas ni atenciones asociadas; esto evita perder referencias de su historial.
- **Citas:** utiliza «Cancelar» y el ID de la cita. Se conserva el registro con estado
  CANCELADA en vez de borrarlo.
- **Atenciones:** no se ofrece eliminación desde la interfaz para proteger el historial clínico.
- **Inventario:** selecciona un medicamento y pulsa «Dar de baja medicamento». Solo se
  permite cuando el stock es cero; los movimientos históricos se conservan.

Cada operación confirmada se guarda en el mismo archivo JSON.


## Pruebas y cobertura

Ejecutar las pruebas:

```bash
python -m unittest discover -s tests -v
```

Medir cobertura (instalar primero `pip install -r requirements-dev.txt`):

```bash
coverage run --branch -m unittest discover -s tests -v
coverage report -m
```

La ejecución de referencia incluida en `evidencia/` obtuvo 53 pruebas aprobadas y 94.5% de cobertura de sentencias del paquete `sistema_rural` (655 sentencias medidas). La cobertura mide ejecución de código durante las pruebas; no representa garantía de ausencia de errores.

El diagrama UML actualizado se encuentra en `docs/`. El informe revisado se entrega junto al ZIP.


## Pruebas y cobertura

Ejecutar las pruebas:

```bash
python -m unittest discover -s tests -v
```

Medir cobertura (instalar primero `pip install -r requirements-dev.txt`):

```bash
coverage run --branch -m unittest discover -s tests -v
coverage report -m
```

La ejecución de referencia incluida en `evidencia/` obtuvo 53 pruebas aprobadas y 94.5% de cobertura de sentencias del paquete `sistema_rural` (655 sentencias medidas). La cobertura mide ejecución de código durante las pruebas; no representa garantía de ausencia de errores.

El diagrama UML actualizado se encuentra en `docs/`. El informe revisado se entrega junto al ZIP.


## Pruebas y cobertura

Ejecutar las pruebas:

```bash
python -m unittest discover -s tests -v
```

Medir cobertura (instalar primero `pip install -r requirements-dev.txt`):

```bash
coverage run --branch -m unittest discover -s tests -v
coverage report --include="sistema_rural/*" -m
```

La ejecución de referencia incluida en `evidencia/` obtuvo 53 pruebas aprobadas y 94.5% de cobertura de sentencias del paquete `sistema_rural` (655 sentencias medidas). La cobertura mide ejecución de código durante las pruebas; no representa garantía de ausencia de errores.

El diagrama UML actualizado se encuentra en `docs/`. El informe revisado se entrega junto al ZIP.


## Pruebas y cobertura

Ejecutar las pruebas:

```bash
python -m unittest discover -s tests -v
```

Medir cobertura (instalar primero `pip install -r requirements-dev.txt`):

```bash
coverage run --branch -m unittest discover -s tests -v
coverage report --include="sistema_rural/*" -m
```

La ejecución de referencia incluida en `evidencia/` obtuvo 53 pruebas aprobadas y 94.5% de cobertura de sentencias del paquete `sistema_rural` (655 sentencias medidas). La cobertura mide ejecución de código durante las pruebas; no representa garantía de ausencia de errores.

El diagrama UML actualizado se encuentra en `docs/`. El informe revisado se entrega junto al ZIP.


Repositorio público del equipo: https://github.com/yampierdionicio5-hash/SistemaRural-PE

## Pruebas y cobertura

Ejecutar las pruebas:

```bash
python -m unittest discover -s tests -v
```

Medir cobertura (instalar primero `pip install -r requirements-dev.txt`):

```bash
coverage run --branch -m unittest discover -s tests -v
coverage report --include="sistema_rural/*" -m
```

La ejecución de referencia incluida en `evidencia/` obtuvo 53 pruebas aprobadas y 94.5% de cobertura de sentencias del paquete `sistema_rural` (655 sentencias medidas). La cobertura mide ejecución de código durante las pruebas; no representa garantía de ausencia de errores.

El diagrama UML actualizado se encuentra en `docs/`. El informe revisado se entrega junto al ZIP.
