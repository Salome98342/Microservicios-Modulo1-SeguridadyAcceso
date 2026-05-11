from database import get_connection, get_cursor
from typing import Optional
import math


def obtener_por_id(usuario_id: int) -> Optional[dict]:
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute(
                "SELECT id, username, email, estado, rol_id, created_at, updated_at "
                "FROM usr_usuarios WHERE id = %s",
                (usuario_id,)
            )
            fila = cur.fetchone()
            return dict(fila) if fila else None
    finally:
        conn.close()


def obtener_por_id_con_hash(usuario_id: int) -> Optional[dict]:
    """Incluye password_hash. Solo para validación interna."""
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute("SELECT * FROM usr_usuarios WHERE id = %s", (usuario_id,))
            fila = cur.fetchone()
            return dict(fila) if fila else None
    finally:
        conn.close()


def obtener_por_email(email: str) -> Optional[dict]:
    """Sin password_hash. Para endpoints públicos."""
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute(
                "SELECT id, username, email, estado, rol_id, created_at, updated_at "
                "FROM usr_usuarios WHERE email = %s",
                (email,)
            )
            fila = cur.fetchone()
            return dict(fila) if fila else None
    finally:
        conn.close()


def obtener_por_email_con_hash(email: str) -> Optional[dict]:
    """Incluye password_hash. Exclusivo para ms-autenticacion."""
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute("SELECT * FROM usr_usuarios WHERE email = %s", (email,))
            fila = cur.fetchone()
            return dict(fila) if fila else None
    finally:
        conn.close()


def obtener_por_username_con_hash(username: str) -> Optional[dict]:
    """Incluye password_hash. Exclusivo para validación interna de credenciales."""
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute("SELECT * FROM usr_usuarios WHERE username = %s", (username,))
            fila = cur.fetchone()
            return dict(fila) if fila else None
    finally:
        conn.close()


def existe_username(username: str, excluir_id: Optional[int] = None) -> bool:
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            if excluir_id:
                cur.execute(
                    "SELECT 1 FROM usr_usuarios WHERE username = %s AND id <> %s",
                    (username, excluir_id)
                )
            else:
                cur.execute(
                    "SELECT 1 FROM usr_usuarios WHERE username = %s",
                    (username,)
                )
            return cur.fetchone() is not None
    finally:
        conn.close()


def existe_email(email: str, excluir_id: Optional[int] = None) -> bool:
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            if excluir_id:
                cur.execute(
                    "SELECT 1 FROM usr_usuarios WHERE email = %s AND id <> %s",
                    (email, excluir_id)
                )
            else:
                cur.execute(
                    "SELECT 1 FROM usr_usuarios WHERE email = %s",
                    (email,)
                )
            return cur.fetchone() is not None
    finally:
        conn.close()


def crear(username: str, email: str, password_hash: str, rol_id: int) -> dict:
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute(
                """
                INSERT INTO usr_usuarios (username, email, password_hash, estado, rol_id)
                VALUES (%s, %s, %s, 'activo', %s)
                RETURNING id, username, email, estado, rol_id, created_at, updated_at
                """,
                (username, email, password_hash, rol_id)
            )
            usuario = cur.fetchone()
        conn.commit()
        return dict(usuario)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def actualizar(usuario_id: int, campos: dict) -> Optional[dict]:
    """Actualización parcial: solo los campos presentes en el dict."""
    if not campos:
        return None
    set_clause = ", ".join(f"{k} = %s" for k in campos)
    valores    = list(campos.values()) + [usuario_id]
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute(
                f"""
                UPDATE usr_usuarios SET {set_clause}
                WHERE id = %s
                RETURNING id, username, email, estado, rol_id, created_at, updated_at
                """,
                valores
            )
            usuario = cur.fetchone()
        conn.commit()
        return dict(usuario) if usuario else None
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def actualizar_password(usuario_id: int, nuevo_hash: str) -> bool:
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute(
                "UPDATE usr_usuarios SET password_hash = %s WHERE id = %s",
                (nuevo_hash, usuario_id)
            )
            actualizado = cur.rowcount > 0
        conn.commit()
        return actualizado
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def cambiar_estado_transaccional(conn, usuario_id: int, nuevo_estado: str) -> Optional[dict]:
    """
    Actualiza el estado dentro de una transacción externa.
    La conexión es administrada por el llamador.
    """
    with get_cursor(conn) as cur:
        cur.execute(
            """
            UPDATE usr_usuarios SET estado = %s
            WHERE id = %s
            RETURNING id, username, email, estado, rol_id, created_at, updated_at
            """,
            (nuevo_estado, usuario_id)
        )
        fila = cur.fetchone()
        return dict(fila) if fila else None


def busqueda_avanzada(
    nombre:           Optional[str],
    numero_documento: Optional[str],
    email:            Optional[str],
    estado:           Optional[str],
    ciudad:           Optional[str],
    pagina:           int,
    items_por_pagina: int,
) -> tuple[list[dict], int]:
    """Retorna (lista_usuarios, total_registros). JOIN con usr_perfiles para filtros de perfil."""
    condiciones: list[str] = []
    valores:     list      = []

    if nombre:
        condiciones.append(
            "(p.primer_nombre ILIKE %s OR p.primer_apellido ILIKE %s)"
        )
        valores += [f"%{nombre}%", f"%{nombre}%"]
    if numero_documento:
        condiciones.append("p.numero_documento = %s")
        valores.append(numero_documento)
    if email:
        condiciones.append("u.email ILIKE %s")
        valores.append(f"%{email}%")
    if estado:
        condiciones.append("u.estado = %s")
        valores.append(estado)
    if ciudad:
        condiciones.append("p.ciudad ILIKE %s")
        valores.append(f"%{ciudad}%")

    where = ("WHERE " + " AND ".join(condiciones)) if condiciones else ""
    base  = f"FROM usr_usuarios u LEFT JOIN usr_perfiles p ON p.usuario_id = u.id {where}"
    offset = (pagina - 1) * items_por_pagina

    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute(f"SELECT COUNT(*) AS total {base}", valores)
            total = cur.fetchone()["total"]

            cur.execute(
                f"""
                SELECT u.id, u.username, u.email, u.estado, u.rol_id,
                       u.created_at, u.updated_at
                {base}
                ORDER BY u.created_at DESC
                LIMIT %s OFFSET %s
                """,
                valores + [items_por_pagina, offset]
            )
            filas = cur.fetchall()

        return [dict(f) for f in filas], total
    finally:
        conn.close()


def validar_existencia(usuario_id: int) -> Optional[dict]:
    """Endpoint ligero para ms-programas — solo id, estado, username."""
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute(
                "SELECT id, username, estado FROM usr_usuarios WHERE id = %s",
                (usuario_id,)
            )
            fila = cur.fetchone()
            return dict(fila) if fila else None
    finally:
        conn.close()


def estadisticas_por_estado() -> dict:
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute(
                "SELECT estado, COUNT(*) AS cantidad FROM usr_usuarios GROUP BY estado"
            )
            filas = cur.fetchall()
        resultado = {"activo": 0, "inactivo": 0, "suspendido": 0}
        for f in filas:
            resultado[f["estado"]] = int(f["cantidad"])
        total = sum(resultado.values())
        return {"total": total, "por_estado": resultado}
    finally:
        conn.close()


def listar_por_rol(
    rol_id: int,
    estado: Optional[str],
    pagina: int,
    items_por_pagina: int,
) -> tuple[list[dict], int]:
    condiciones = ["rol_id = %s"]
    valores: list = [rol_id]

    if estado and estado != "todos":
        condiciones.append("estado = %s")
        valores.append(estado)

    where  = "WHERE " + " AND ".join(condiciones)
    offset = (pagina - 1) * items_por_pagina

    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute(
                f"SELECT COUNT(*) AS total FROM usr_usuarios {where}",
                valores
            )
            total = cur.fetchone()["total"]

            cur.execute(
                f"""
                SELECT id, username, email, estado, rol_id, created_at, updated_at
                FROM usr_usuarios {where}
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
                """,
                valores + [items_por_pagina, offset]
            )
            filas = cur.fetchall()

        return [dict(f) for f in filas], total
    finally:
        conn.close()

