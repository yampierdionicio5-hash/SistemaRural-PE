# SistemaRural-PE

Diseño de software multiparadigma para la gestión de establecimientos de salud en zonas rurales del Perú.
Caso aplicado: **Puesto de Salud del Sector / Barrio 1 de Alto Trujillo** (Nivel I-1), Trujillo, La Libertad.

## Datos del curso
- Universidad Privada del Norte, Facultad de Ingeniería
- Curso: Lenguajes de Programación (UAIN1288P), código de clase 25495, ciclo 2026-II
- Docente: Segundo José Castillo Zumarán

## Integrantes
- Arroyo León Dayron Yorbin
- Paredes Castillo Jorge Luis
- Yampier Minchola Dionicio
- Villanueva Briceño Segundo Maximo Rubne
- Otiniano Luján Braulio Caleb

## ¿Qué hace el sistema?
Reemplaza los cuadernos de registro físicos del puesto de salud por un módulo digital que funciona en una
computadora local, sin internet:
- Registro y actualización de pacientes (el DNI es único y se valida).
- Programación, reprogramación y cancelación de citas médicas.
- Registro de atenciones clínicas ligadas a una cita.
- Control de inventario de medicamentos con alertas de stock crítico y de vencimiento.
- Reportes semanales y mensuales (atenciones, morbilidad y consumo de medicamentos).
- Búsqueda de pacientes por DNI o apellidos, y de atenciones por rango de fechas.

## Paradigmas aplicados
| Paradigma | Dónde |
|---|---|
| Orientado a objetos | `sistema_rural/dominio/` (herencia, encapsulamiento, patrón Factory) |
| Funcional | `sistema_rural/servicios/reportes.py` (`map`, `filter`, `reduce`, `lambda`) |
| Orientado a eventos | `sistema_rural/interfaz/` (ventana con Tkinter) |

Patrones de diseño: **Singleton** (`GestorPersistencia`) y **Factory** (`PersonaFactory`).
El diagrama de clases está en `docs/`.

## Cómo ejecutarlo
Requiere solo Python 3.x (Tkinter viene incluido en Windows; en Linux: `sudo apt install python3-tk`).
No hay que instalar librerías.
```
python main.py
```

## Pruebas automatizadas
```
python -m unittest discover -s tests -v
```

## Estructura del proyecto
```
main.py                         punto de entrada
sistema_rural/
  config.py                     constantes y rutas
  excepciones.py                errores propios
  dominio/                      clases del dominio (una por archivo)
  servicios/                    reportes, seguridad, persistencia y coordinación
  interfaz/                     ventana principal
  utilidades/                   validaciones
tests/                          pruebas automatizadas
docs/                           diagrama de clases UML
```

## Protección de datos personales (Ley N.º 29733)
- Los datos personales y clínicos se **cifran** antes de guardarse; el archivo `datos/datos_rural.json`
  no contiene datos en texto plano.
- La clave de cifrado se guarda aparte en `datos/clave.key`. Ambos archivos se crean al ejecutar el programa
  y **no se suben al repositorio** (ver `.gitignore`). Si se pierde la clave, los datos no se pueden recuperar.
- Los registros internos (logs) no incluyen datos personales.
- Todos los datos de demostración son ficticios.
