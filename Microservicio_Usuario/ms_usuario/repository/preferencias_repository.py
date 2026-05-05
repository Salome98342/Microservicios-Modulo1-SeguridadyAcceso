from database import get_connection, get_cursor
from typing import Optional


def obtener_por_usuario_id(usuario_id: int) -> Optional[dict]:
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute(
                "SELECT * FROM usr_preferencias_notificacion WHERE usuario_id = %s",
                (usuario_id,)
            )
            fila = cur.fetchone()
            return dict(fila) if fila else None
    finally:
        conn.close()


def crear_o_actualizar(usuario_id: int, datos: dict) -> dict:
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute(
                "SELECT id FROM usr_preferencias_notificacion WHERE usuario_id = %s",
                (usuario_id,)
            )
            existente = cur.fetchone()

            if existente:
                set_clause = ", ".join(f"{k} = %s" for k in datos)
                cur.execute(
                    f"""
                    UPDATE usr_preferencias_notificacion SET {set_clause}
                    WHERE usuario_id = %s RETURNING *
                    """,
                    list(datos.values()) + [usuario_id]
                )
            else:
                columnas     = ", ".join(["usuario_id"] + list(datos.keys()))
                placeholders = ", ".join(["%s"] * (1 + len(datos)))
                cur.execute(
                    f"""
                    INSERT INTO usr_preferencias_notificacion ({columnas})
                    VALUES ({placeholders}) RETURNING *
                    """,
                    [usuario_id] + list(datos.values())
                )

            pref = cur.fetchone()
        conn.commit()
        return dict(pref)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

