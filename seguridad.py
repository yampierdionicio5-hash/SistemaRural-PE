import base64
import hashlib
import hmac
import secrets
from pathlib import Path

from sistema_rural.excepciones import ErrorAlmacenamiento

TAM_CLAVE = 32
TAM_NONCE = 16
TAM_FIRMA = 32


class ServicioSeguridad:
    """Cifra los datos personales antes de guardarlos (Ley N.º 29733).

    Usa solo la librería estándar: un flujo de bytes derivado con HMAC-SHA256
    (distinto en cada dato gracias a un nonce aleatorio) y una firma HMAC para
    detectar si el dato fue alterado. Está aislado en esta clase para poder
    cambiarlo por otro algoritmo sin tocar el resto del sistema.
    """

    def __init__(self, ruta_clave):
        self._ruta_clave = Path(ruta_clave)
        try:
            clave = self._cargar_o_crear_clave()
        except OSError:
            raise ErrorAlmacenamiento("No se pudo leer o crear la clave de cifrado.")
        if len(clave) != TAM_CLAVE:
            raise ErrorAlmacenamiento("La clave de cifrado está dañada.")
        self._clave_cifrado = hashlib.sha256(b"cifrado" + clave).digest()
        self._clave_firma = hashlib.sha256(b"firma" + clave).digest()

    @staticmethod
    def enmascarar_dni(dni):
        """Solo para registros internos (logs): evita escribir el DNI completo."""
        return dni[:2] + "****" + dni[-2:]

    def _cargar_o_crear_clave(self):
        if self._ruta_clave.exists():
            return self._ruta_clave.read_bytes()
        clave = secrets.token_bytes(TAM_CLAVE)
        self._ruta_clave.write_bytes(clave)
        return clave

    def _flujo(self, nonce, longitud):
        bloques = bytearray()
        contador = 0
        while len(bloques) < longitud:
            bloques += hmac.new(
                self._clave_cifrado, nonce + contador.to_bytes(4, "big"), hashlib.sha256
            ).digest()
            contador += 1
        return bytes(bloques[:longitud])

    def _firmar(self, datos):
        return hmac.new(self._clave_firma, datos, hashlib.sha256).digest()

    def cifrar(self, texto):
        """Devuelve el dato cifrado y firmado (Base64) para guardarlo en el JSON."""
        datos = str(texto).encode("utf-8")
        nonce = secrets.token_bytes(TAM_NONCE)
        cifrado = bytes(a ^ b for a, b in zip(datos, self._flujo(nonce, len(datos))))
        firma = self._firmar(nonce + cifrado)
        return base64.urlsafe_b64encode(nonce + firma + cifrado).decode("ascii")

    def descifrar(self, token):
        """Verifica la firma y devuelve el texto original; falla si el dato fue alterado."""
        error = ErrorAlmacenamiento(
            "No se pudo descifrar un dato: la clave no corresponde o el archivo fue alterado."
        )
        try:
            crudo = base64.urlsafe_b64decode(token.encode("ascii"))
        except (ValueError, UnicodeError):
            raise error
        if len(crudo) < TAM_NONCE + TAM_FIRMA:
            raise error
        nonce = crudo[:TAM_NONCE]
        firma = crudo[TAM_NONCE:TAM_NONCE + TAM_FIRMA]
        cifrado = crudo[TAM_NONCE + TAM_FIRMA:]
        if not hmac.compare_digest(firma, self._firmar(nonce + cifrado)):
            raise error
        datos = bytes(a ^ b for a, b in zip(cifrado, self._flujo(nonce, len(cifrado))))
        try:
            return datos.decode("utf-8")
        except UnicodeError:
            raise error
