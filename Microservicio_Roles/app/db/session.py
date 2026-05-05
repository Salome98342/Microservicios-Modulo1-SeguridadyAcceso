"""
app/db/session.py
=================
Configura el engine de SQLAlchemy y la fábrica de sesiones para
la base de datos PostgreSQL del microservicio ms-roles.

Responsabilidad:
    - Crear el engine de conexión usando la DATABASE_URL del archivo .env.
    - Exponer `SessionLocal`: fábrica de sesiones para uso directo.
    - Exponer `get_db()`: generador/dependencia de FastAPI que abre
      una sesión por request y la cierra al finalizar.

Configuración del pool:
    - pool_pre_ping: verifica la conexión antes de usarla (evita
      errores por conexiones caídas).
    - pool_size: conexiones simultáneas mantenidas en el pool.
    - max_overflow: conexiones adicionales permitidas bajo carga alta.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings


engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)
"""
Engine principal de SQLAlchemy.
Se construye una sola vez al importar el módulo y se reutiliza
durante todo el ciclo de vida de la aplicación.
"""

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
"""
Fábrica de sesiones SQLAlchemy.

    autocommit=False: los cambios requieren llamada explícita a db.commit().
    autoflush=False:  evita flushes automáticos antes de cada consulta,
                      dando control explícito al desarrollador.
"""


def get_db() -> Session:
    """
    Generador de sesión de base de datos para inyección de dependencias en FastAPI.

    Abre una sesión al inicio de cada request HTTP y garantiza su cierre
    al finalizar, independientemente de si ocurrió un error o no (bloque finally).

    Yields:
        Session: Sesión activa de SQLAlchemy lista para ejecutar consultas.

    Uso en un router de FastAPI:
        @router.get("/ejemplo")
        def mi_endpoint(db: Session = Depends(get_db)):
            resultado = db.query(MiModelo).all()
            return resultado

    Nota:
        No se debe llamar a db.close() manualmente dentro de los endpoints;
        este generador se encarga de hacerlo al salir del contexto.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        