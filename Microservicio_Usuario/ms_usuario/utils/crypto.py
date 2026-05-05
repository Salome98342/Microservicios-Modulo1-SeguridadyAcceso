"""
Cifrado AES-256 y hashing bcrypt.
Según los documentos, las contraseñas se transmiten cifradas con AES-256
en Base64 desde el cliente; el servidor las descifra y genera hash bcrypt.
Los tokens de aplicación siguen la misma política.
"""
import base64
import bcrypt
from config import AES_SECRET_KEY, BCRYPT_ROUNDS


def _obtener_clave_bytes() -> bytes:
    """
    La clave AES-256 se almacena como 64 caracteres hexadecimales en .env
    (32 bytes). Esta función la convierte a bytes.
    """
    return bytes.fromhex(AES_SECRET_KEY)


def descifrar_aes256(texto_cifrado_b64: str) -> str:
    """
    Descifra un texto cifrado con AES-256 recibido en Base64.
    Formato esperado: IV (16 bytes) + datos cifrados, todo codificado en Base64.
    """
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import unpad

    datos   = base64.b64decode(texto_cifrado_b64)
    iv      = datos[:16]
    cifrado = datos[16:]
    cipher  = AES.new(_obtener_clave_bytes(), AES.MODE_CBC, iv)
    plano   = unpad(cipher.decrypt(cifrado), AES.block_size)
    return plano.decode("utf-8")


def cifrar_aes256(texto_plano: str) -> str:
    """
    Cifra texto plano con AES-256-CBC.
    Retorna IV + datos cifrados codificado en Base64.
    """
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad
    from Crypto.Random import get_random_bytes

    iv      = get_random_bytes(16)
    cipher  = AES.new(_obtener_clave_bytes(), AES.MODE_CBC, iv)
    cifrado = cipher.encrypt(pad(texto_plano.encode("utf-8"), AES.block_size))
    return base64.b64encode(iv + cifrado).decode("utf-8")


def hashear_bcrypt(password_plano: str) -> str:
    """Hash bcrypt con factor de costo mínimo 12 (según USR-RF-006 y Sección 6.4)."""
    return bcrypt.hashpw(
        password_plano.encode("utf-8"),
        bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    ).decode("utf-8")


def verificar_bcrypt(password_plano: str, hash_almacenado: str) -> bool:
    return bcrypt.checkpw(
        password_plano.encode("utf-8"),
        hash_almacenado.encode("utf-8")
    )

