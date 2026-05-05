from typing import Optional

import repository.usuario_repository  as usuario_repo
import repository.historial_repository as historial_repo
from database import get_connection

ESTADOS_VALIDOS = {"activo", "inactivo", "suspendido"}


def cambiar_estado(
    usuario_id:             int,
    estado_nuevo:           str,
    motivo:                 str,
    usuario_modificador_id: int,
) -> tuple[Optional[dict], Optional[str]]:
    """
    Cambia el estado y registra el historial en una sola transacción atómica.
    USR-RF-015. Retorna (usuario_actualizado, error).
    """
    if estado_nuevo not in ESTADOS_VALIDOS:
        return None, f"Estado inválido. Valores permitidos: {', '.join(ESTADOS_VALIDOS)}"
    if not motivo or not motivo.strip():
        return None, "Debe proporcionar un motivo para el cambio de estado"

    usuario = usuario_repo.obtener_por_id(usuario_id)
    if not usuario:
        return None, "404:Usuario no encontrado"
    if usuario["estado"] == estado_nuevo:
        return None, "El usuario ya se encuentra en el estado especificado"

    estado_anterior = usuario["estado"]

    # Transacción atómica: UPDATE de estado + INSERT de historial
    conn = get_connection()
    try:
        usuario_actualizado = usuario_repo.cambiar_estado_transaccional(
            conn, usuario_id, estado_nuevo
        )
        historial_repo.registrar_cambio_transaccional(
            conn, usuario_id, estado_anterior, estado_nuevo,
            motivo, usuario_modificador_id
        )
        conn.commit()
        return usuario_actualizado, None
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def listar_historial(usuario_id: int) -> list[dict]:
    """USR-RF-016."""
    if not usuario_repo.obtener_por_id(usuario_id):
        return []
    return historial_repo.listar_por_usuario(usuario_id)

