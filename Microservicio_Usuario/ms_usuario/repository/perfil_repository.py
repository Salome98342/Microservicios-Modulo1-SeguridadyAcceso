from database import get_connection, get_cursor
from typing import Optional


def obtener_por_usuario_id(usuario_id: int) -> Optional[dict]:
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute(
                """
                SELECT p.*, t.codigo AS tipo_documento_codigo,
                            t.nombre AS tipo_documento_nombre
                FROM usr_perfiles p
                JOIN usr_tipos_documento t ON t.id = p.tipo_documento_id
                WHERE p.usuario_id = %s
                """,
                (usuario_id,)
            )
            fila = cur.fetchone()
            return dict(fila) if fila else None
    finally:
        conn.close()


def existe_numero_documento(
    numero_documento: str, excluir_usuario_id: Optional[int] = None
) -> bool:
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            if excluir_usuario_id:
                cur.execute(
                    "SELECT 1 FROM usr_perfiles "
                    "WHERE numero_documento = %s AND usuario_id <> %s",
                    (numero_documento, excluir_usuario_id)
                )
            else:
                cur.execute(
                    "SELECT 1 FROM usr_perfiles WHERE numero_documento = %s",
                    (numero_documento,)
                )
            return cur.fetchone() is not None
    finally:
        conn.close()


def crear_o_actualizar(usuario_id: int, datos: dict) -> dict:
    """Upsert: crea el perfil si no existe; lo actualiza si existe."""
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute(
                "SELECT id FROM usr_perfiles WHERE usuario_id = %s",
                (usuario_id,)
            )
            existente = cur.fetchone()

            if existente:
                set_clause = ", ".join(f"{k} = %s" for k in datos)
                valores    = list(datos.values()) + [usuario_id]
                cur.execute(
                    f"""
                    UPDATE usr_perfiles SET {set_clause}
                    WHERE usuario_id = %s RETURNING *
                    """,
                    valores
                )
            else:
                columnas     = ", ".join(["usuario_id"] + list(datos.keys()))
                placeholders = ", ".join(["%s"] * (1 + len(datos)))
                cur.execute(
                    f"""
                    INSERT INTO usr_perfiles ({columnas})
                    VALUES ({placeholders}) RETURNING *
                    """,
                    [usuario_id] + list(datos.values())
                )

            perfil = cur.fetchone()
        conn.commit()
        return dict(perfil)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

