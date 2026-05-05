from database import get_connection, get_cursor
from typing import Optional


def listar_activos() -> list[dict]:
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute(
                "SELECT id, codigo, nombre, descripcion "
                "FROM usr_tipos_documento WHERE activo = true ORDER BY nombre ASC"
            )
            return [dict(f) for f in cur.fetchall()]
    finally:
        conn.close()


def obtener_por_id(tipo_id: int) -> Optional[dict]:
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute(
                "SELECT id, codigo, nombre, descripcion, activo "
                "FROM usr_tipos_documento WHERE id = %s",
                (tipo_id,)
            )
            fila = cur.fetchone()
            return dict(fila) if fila else None
    finally:
        conn.close()

