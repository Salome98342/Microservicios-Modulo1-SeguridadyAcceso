import time
import random
import string
from typing import Optional


def generar_request_id() -> str:
    """
    Genera un Request ID con el formato: USR-{timestamp_unix}-{8_chars_alfanuméricos}
    Ejemplo: USR-1709856234-a3f8b2c1
    """
    timestamp = int(time.time())
    aleatorio = "".join(
        random.choices(string.ascii_lowercase + string.digits, k=8)
    )
    return f"USR-{timestamp}-{aleatorio}"


def obtener_o_generar(x_request_id: Optional[str]) -> str:
    """
    Si la petición trae un Request ID (de otro microservicio), lo reutiliza.
    Si no, genera uno nuevo. Implementa USR-RF-003.
    """
    if x_request_id and x_request_id.strip():
        return x_request_id.strip()
    return generar_request_id()

