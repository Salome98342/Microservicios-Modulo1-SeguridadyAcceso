"""
Envío asíncrono (fire-and-forget) de logs de auditoría a ms-auditoria [AUD].
Si falla, escribe en archivo de respaldo local.
Implementa USR-RF-004 y la regla transversal 6.6.
"""
import json
import threading
import datetime
import os
from typing import Optional
from urllib import request as urllib_request
from urllib.error import URLError

from config import AUD_SERVICE_URL, AUD_APP_TOKEN, TIMEOUT_AUD

BACKUP_DIR  = "/var/log/ms-usuarios/audit-backup"


def _guardar_respaldo(log: dict) -> None:
    """Escribe el log en un archivo JSONL local si ms-auditoria no está disponible."""
    try:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        fecha   = datetime.date.today().isoformat()
        archivo = os.path.join(BACKUP_DIR, f"audit-{fecha}.jsonl")
        with open(archivo, "a", encoding="utf-8") as f:
            f.write(json.dumps(log, default=str) + "\n")
    except Exception as e:
        print(f"[AUDIT BACKUP ERROR] {e}")


def _enviar_log(log: dict) -> None:
    """Envía el log JSON a ms-auditoria. En caso de error, lo guarda en respaldo."""
    try:
        payload = json.dumps(log, default=str).encode("utf-8")
        req = urllib_request.Request(
            url=f"{AUD_SERVICE_URL}/api/v1/audit/logs",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "X-App-Token":  f"AES256:{AUD_APP_TOKEN}",
                "X-Request-ID": log.get("request_id", ""),
            },
            method="POST",
        )
        urllib_request.urlopen(req, timeout=TIMEOUT_AUD)
    except Exception:
        _guardar_respaldo(log)


def registrar_log_async(
    request_id:    str,
    funcionalidad: str,
    metodo:        str,
    endpoint:      str,
    codigo:        int,
    usuario_id:    Optional[int],
    detalle:       str,
) -> None:
    """
    Construye el log JSON y lo envía en un thread separado (no bloquea).
    Implementa USR-RF-004.
    """
    log = {
        "timestamp":        datetime.datetime.utcnow().isoformat() + "Z",
        "request_id":       request_id,
        "microservicio":    "ms-usuarios",
        "funcionalidad":    funcionalidad,
        "metodo":           metodo,
        "endpoint":         endpoint,
        "codigo_respuesta": codigo,
        "usuario_id":       usuario_id,
        "detalle":          detalle,
    }
    hilo = threading.Thread(target=_enviar_log, args=(log,), daemon=True)
    hilo.start()

