import json
import logging
import os
from pathlib import Path

from sistema_rural.config import CARPETA_DATOS, NOMBRE_ARCHIVO_CLAVE, NOMBRE_ARCHIVO_DATOS
from sistema_rural.excepciones import ErrorAlmacenamiento
from sistema_rural.servicios.seguridad import ServicioSeguridad

logger = logging.getLogger(__name__)


class GestorPersistencia:
    """Singleton: una única instancia controla el acceso al archivo JSON."""

    _instancia = None

    def __init__(self, carpeta=None):
        if GestorPersistencia._instancia is not None:
            raise RuntimeError("Use GestorPersistencia.obtener_instancia().")
        carpeta = Path(carpeta) if carpeta else CARPETA_DATOS
        try:
            carpeta.mkdir(parents=True, exist_ok=True)
        except OSError:
            raise ErrorAlmacenamiento("No se pudo crear la carpeta de datos.")
        self._ruta = carpeta / NOMBRE_ARCHIVO_DATOS
        self._seguridad = ServicioSeguridad(carpeta / NOMBRE_ARCHIVO_CLAVE)

    @classmethod
    def obtener_instancia(cls, carpeta=None):
        if cls._instancia is None:
            cls._instancia = cls(carpeta)
        return cls._instancia

    @classmethod
    def reiniciar(cls):
        cls._instancia = None

    @property
    def ruta(self):
        return self._ruta

    def _leer(self):
        if not self._ruta.exists():
            return {}
        try:
            with open(self._ruta, "r", encoding="utf-8") as archivo:
                return json.load(archivo)
        except (OSError, json.JSONDecodeError):
            raise ErrorAlmacenamiento("No se pudo leer el archivo de datos (¿está dañado?).")

    def _escribir(self, datos):
        # Se escribe en un archivo temporal y luego se reemplaza el original,
        # así un corte de luz a mitad de la escritura no deja el JSON a medias.
        temporal = self._ruta.with_suffix(".tmp")
        try:
            with open(temporal, "w", encoding="utf-8") as archivo:
                json.dump(datos, archivo, ensure_ascii=False, indent=2)
            os.replace(temporal, self._ruta)
        except OSError:
            raise ErrorAlmacenamiento("No se pudo escribir el archivo de datos.")

    def guardar(self, coleccion, registros, campos_sensibles=()):
        """Cifra los campos sensibles y guarda la colección en el JSON."""
        datos = self._leer()
        datos[coleccion] = [
            {
                campo: self._seguridad.cifrar(valor) if campo in campos_sensibles else valor
                for campo, valor in registro.items()
            }
            for registro in registros
        ]
        self._escribir(datos)
        logger.info("Colección '%s' guardada (%d registros).", coleccion, len(registros))

    def cargar(self, coleccion, campos_sensibles=()):
        """Lee la colección del JSON y descifra los campos sensibles."""
        registros = self._leer().get(coleccion, [])
        return [
            {
                campo: self._seguridad.descifrar(valor) if campo in campos_sensibles else valor
                for campo, valor in registro.items()
            }
            for registro in registros
        ]
