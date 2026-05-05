import base64
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from app.config import settings


# ── AES-256 ───────────────────────────────────────────────────────────────────

def _get_aes_key() -> bytes:
    """
    La clave debe ser exactamente 32 bytes (256 bits).
    Se lee desde settings y se codifica a bytes.
    """
    clave = settings.aes_secret_key.encode("utf-8")
    if len(clave) != 32:
        raise ValueError(
            f"AES_SECRET_KEY debe tener exactamente 32 caracteres. "
            f"Actualmente tiene {len(clave)}."
        )
    return clave


def cifrar_aes256(texto_plano: str) -> str:
    """
    Cifra un texto con AES-256 en modo CBC.
    Retorna base64(IV + texto_cifrado) para almacenamiento seguro.
    """
    clave = _get_aes_key()
    iv    = os.urandom(16)                          # vector de inicialización aleatorio

    cipher    = Cipher(algorithms.AES(clave), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # Padding PKCS7 manual para que el texto sea múltiplo de 16 bytes
    texto_bytes  = texto_plano.encode("utf-8")
    padding_len  = 16 - (len(texto_bytes) % 16)
    texto_padded = texto_bytes + bytes([padding_len] * padding_len)

    texto_cifrado = encryptor.update(texto_padded) + encryptor.finalize()

    # Guardar IV + cifrado juntos, codificados en base64
    return base64.b64encode(iv + texto_cifrado).decode("utf-8")


def descifrar_aes256(texto_cifrado_b64: str) -> str:
    """
    Descifra un texto cifrado con cifrar_aes256().
    Retorna el texto plano original.
    """
    clave = _get_aes_key()
    datos = base64.b64decode(texto_cifrado_b64.encode("utf-8"))

    iv            = datos[:16]
    texto_cifrado = datos[16:]

    cipher    = Cipher(algorithms.AES(clave), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    texto_padded = decryptor.update(texto_cifrado) + decryptor.finalize()

    # Quitar padding PKCS7
    padding_len = texto_padded[-1]
    return texto_padded[:-padding_len].decode("utf-8")


# ── Validación de token de aplicación (RT-002) ────────────────────────────────

def validar_token_aplicacion(token_cifrado_recibido: str, token_cifrado_bd: str) -> bool:
    """
    Descifra ambos tokens y compara en texto plano.
    Retorna True si coinciden y son válidos.
    """
    try:
        token_recibido = descifrar_aes256(token_cifrado_recibido)
        token_bd       = descifrar_aes256(token_cifrado_bd)
        return token_recibido == token_bd
    except Exception:
        return False


def generar_token_aplicacion() -> tuple[str, str]:
    """
    Genera un token de aplicación nuevo.
    Retorna (token_plano, token_cifrado).
    El token_plano se entrega al servicio propietario.
    El token_cifrado se almacena en base de datos.
    """
    import secrets
    token_plano   = secrets.token_urlsafe(32)
    token_cifrado = cifrar_aes256(token_plano)
    return token_plano, token_cifrado