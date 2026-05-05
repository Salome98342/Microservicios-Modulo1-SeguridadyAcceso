from database import get_connection, get_cursor
from typing import Optional


def registrar_cambio_transaccional(
    conn,
    usuario_id:             int,
    estado_anterior:        str,
    estado_nuevo:           str,
    motivo:                 str,
    usuario_modificador_id: int,
) -> dict:
    """
    Inserta en usr_historial_estados dentro de una transacción externa.
    La conexión es administrada por el llamador.
    """
    with get_cursor(conn) as cur:
        cur.execute(
            """
            INSERT INTO usr_historial_estados
                (usuario_id, estado_anterior, estado_nuevo, motivo, usuario_modificador_id)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING *
            """,
            (usuario_id, estado_anterior, estado_nuevo, motivo, usuario_modificador_id)
        )
        return dict(cur.fetchone())


def listar_por_usuario(usuario_id: int) -> list[dict]:
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute(
                """
                SELECT * FROM usr_historial_estados
                WHERE usuario_id = %s
                ORDER BY created_at DESC
                """,
                (usuario_id,)
            )
            return [dict(f) for f in cur.fetchall()]
    finally:
        conn.close()

