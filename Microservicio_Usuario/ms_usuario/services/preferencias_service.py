from typing import Optional

import repository.preferencias_repository as repo
import repository.usuario_repository      as usuario_repo

DEFAULTS = {
    "notif_email":                True,
    "notif_sms":                  False,
    "notif_push":                 True,
    "canal_preferido":            "email",
    "horario_no_molestar_inicio": None,
    "horario_no_molestar_fin":    None,
}


def obtener_preferencias(usuario_id: int) -> tuple[Optional[dict], Optional[str]]:
    """USR-RF-018. Retorna defaults si no hay configuración personalizada."""
    if not usuario_repo.obtener_por_id(usuario_id):
        return None, "404:Usuario no encontrado"
    pref = repo.obtener_por_usuario_id(usuario_id)
    if not pref:
        return {"usuario_id": usuario_id, **DEFAULTS}, None
    return dict(pref), None


def crear_o_actualizar_preferencias(
    usuario_id: int, datos: dict
) -> tuple[Optional[dict], Optional[str]]:
    """USR-RF-019."""
    if not usuario_repo.obtener_por_id(usuario_id):
        return None, "404:Usuario no encontrado"
    pref = repo.crear_o_actualizar(usuario_id, datos)
    return pref, None

