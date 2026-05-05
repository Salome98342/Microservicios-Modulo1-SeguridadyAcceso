from typing import Optional

import repository.perfil_repository         as repo
import repository.usuario_repository        as usuario_repo
import repository.tipo_documento_repository as tipo_repo


def obtener_perfil(usuario_id: int) -> tuple[Optional[dict], Optional[str]]:
    """USR-RF-013."""
    if not usuario_repo.obtener_por_id(usuario_id):
        return None, "404:Usuario no encontrado"
    perfil = repo.obtener_por_usuario_id(usuario_id)
    if not perfil:
        return None, "404:Perfil no encontrado para el usuario especificado"
    return perfil, None


def crear_o_actualizar_perfil(
    usuario_id: int, datos: dict
) -> tuple[Optional[dict], Optional[str], bool]:
    """USR-RF-014. Retorna (perfil, error, fue_creado)."""
    if not usuario_repo.obtener_por_id(usuario_id):
        return None, "404:Usuario no encontrado", False

    tipo = tipo_repo.obtener_por_id(datos["tipo_documento_id"])
    if not tipo or not tipo["activo"]:
        return None, "Tipo de documento inválido", False

    if repo.existe_numero_documento(
        datos["numero_documento"], excluir_usuario_id=usuario_id
    ):
        return None, "El número de documento ya está registrado", False

    existia = repo.obtener_por_usuario_id(usuario_id) is not None
    perfil  = repo.crear_o_actualizar(usuario_id, datos)
    return perfil, None, not existia

