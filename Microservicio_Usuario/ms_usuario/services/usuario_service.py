import math
import re
from typing import Optional

import repository.usuario_repository as repo
from utils.crypto import descifrar_aes256, hashear_bcrypt, verificar_bcrypt
from utils.inter_service import validar_rol_externo
from config import ITEMS_POR_PAGINA_MAX, DEBUG_MODE

ESTADOS_VALIDOS = {"activo", "inactivo", "suspendido"}


def obtener_por_id(usuario_id: int) -> Optional[dict]:
    return repo.obtener_por_id(usuario_id)


def obtener_por_email_publico(email: str) -> Optional[dict]:
    return repo.obtener_por_email(email)


def obtener_por_email_con_hash(email: str) -> Optional[dict]:
    """Solo para ms-autenticacion."""
    return repo.obtener_por_email_con_hash(email)


def crear_usuario(
    username: str, 
    email: str, 
    password_encrypted: Optional[str] = None,
    password_plana: Optional[str] = None,
    rol_id: int = None
) -> tuple[Optional[dict], Optional[str]]:
    """USR-RF-006. Retorna (usuario, error).
    
    En modo DEBUG_MODE: acepta password_plana (texto plano)
    En producción: requiere password_encrypted (AES-256 Base64)
    """
    if repo.existe_username(username):
        return None, "El nombre de usuario ya está registrado"
    if repo.existe_email(email):
        return None, "El correo electrónico ya está registrado"

    rol_valido, error_rol = validar_rol_externo(rol_id)
    if not rol_valido:
        return None, error_rol or "El rol especificado no es válido"

    # Determinar fuente de contraseña
    if DEBUG_MODE and password_plana:
        # Modo DEBUG: usar contraseña en texto plano
        password_plano = password_plana
    elif password_encrypted:
        # Modo normal: descifrar contraseña AES-256
        try:
            password_plano = descifrar_aes256(password_encrypted)
        except Exception as e:
            return None, f"Error al procesar la contraseña: {str(e)}"
    else:
        return None, "Se requiere 'password_encrypted' o 'password_plana' (DEBUG_MODE)"

    password_hash = hashear_bcrypt(password_plano)
    usuario = repo.crear(username, email, password_hash, rol_id)
    return usuario, None


def actualizar_usuario(
    usuario_id: int,
    username:   Optional[str],
    email:      Optional[str],
    rol_id:     Optional[int],
) -> tuple[Optional[dict], Optional[str]]:
    """USR-RF-010."""
    if not any([username, email, rol_id]):
        return None, "Debe proporcionar al menos un campo a actualizar"

    if not repo.obtener_por_id(usuario_id):
        return None, "404:Usuario no encontrado"

    campos = {}

    if username:
        if repo.existe_username(username, excluir_id=usuario_id):
            return None, "El nombre de usuario ya está registrado"
        campos["username"] = username

    if email:
        if repo.existe_email(email, excluir_id=usuario_id):
            return None, "El correo electrónico ya está registrado"
        campos["email"] = email

    if rol_id:
        valido, error = validar_rol_externo(rol_id)
        if not valido:
            return None, error or "El rol especificado no es válido"
        campos["rol_id"] = rol_id

    usuario = repo.actualizar(usuario_id, campos)
    return usuario, None


def cambiar_password(
    usuario_id:                int,
    password_actual_encrypted: str,
    password_nueva_encrypted:  str,
) -> tuple[bool, Optional[str]]:
    """USR-RF-022."""
    usuario = repo.obtener_por_id_con_hash(usuario_id)
    if not usuario:
        return False, "404:Usuario no encontrado"

    try:
        actual_plano = descifrar_aes256(password_actual_encrypted)
        nueva_plano  = descifrar_aes256(password_nueva_encrypted)
    except Exception:
        return False, "Error al procesar las contraseñas"

    if not verificar_bcrypt(actual_plano, usuario["password_hash"]):
        return False, "401:Contraseña actual incorrecta"

    if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$", nueva_plano):
        return False, (
            "La nueva contraseña no cumple con las políticas de seguridad: "
            "mínimo 8 caracteres, al menos 1 mayúscula, 1 minúscula, 1 número"
        )

    repo.actualizar_password(usuario_id, hashear_bcrypt(nueva_plano))
    return True, None


def busqueda_avanzada(
    nombre, numero_documento, email, estado, ciudad, pagina, items_por_pagina
) -> dict:
    if items_por_pagina > ITEMS_POR_PAGINA_MAX:
        items_por_pagina = ITEMS_POR_PAGINA_MAX
    filas, total = repo.busqueda_avanzada(
        nombre, numero_documento, email, estado, ciudad, pagina, items_por_pagina
    )
    return {
        "resultados":       filas,
        "total_registros":  total,
        "total_paginas":    math.ceil(total / items_por_pagina) if total else 0,
        "pagina_actual":    pagina,
        "items_por_pagina": items_por_pagina,
    }


def validar_existencia(usuario_id: int) -> dict:
    """USR-RF-021. Para ms-programas."""
    fila = repo.validar_existencia(usuario_id)
    if not fila:
        return {"existe": False}
    return {
        "existe":   True,
        "estado":   fila["estado"],
        "user_id":  fila["id"],
        "username": fila["username"],
    }


def obtener_estadisticas() -> dict:
    """USR-RF-024."""
    return repo.estadisticas_por_estado()


def listar_por_rol(rol_id, estado, pagina, items_por_pagina) -> dict:
    filas, total = repo.listar_por_rol(rol_id, estado, pagina, items_por_pagina)
    return {
        "resultados":       filas,
        "total_registros":  total,
        "total_paginas":    math.ceil(total / items_por_pagina) if total else 0,
        "pagina_actual":    pagina,
        "items_por_pagina": items_por_pagina,
    }

