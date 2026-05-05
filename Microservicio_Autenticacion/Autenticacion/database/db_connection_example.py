"""
Ejemplo de conexión a la base de datos PostgreSQL
Microservicio de Autenticación
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import logging

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Clase para manejar la conexión a PostgreSQL"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
    
    def connect(self, database_url: str = None):
        """
        Establece conexión con la base de datos
        
        Args:
            database_url: URL de conexión (si no se proporciona, usa variable de entorno)
        """
        if database_url is None:
            database_url = os.getenv(
                "DATABASE_URL",
                "postgresql://auth:auth@localhost:5432/auth_db"
            )
        
        try:
            self.engine = create_engine(
                database_url,
                echo=os.getenv("SQL_ECHO", "false").lower() == "true",
                poolclass=NullPool if os.getenv("TESTING") else None,
                pool_pre_ping=True,  # Verifica conexiones antes de usarlas
                pool_recycle=3600,  # Recicla conexiones después de 1 hora
            )
            
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # Prueba la conexión
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                logger.info("Conexión a PostgreSQL exitosa")
                return True
                
        except Exception as e:
            logger.error(f"Error al conectar a PostgreSQL: {e}")
            return False
    
    def get_session(self):
        """Obtiene una nueva sesión de BD"""
        if self.SessionLocal is None:
            raise RuntimeError("Database no está conectada. Llamar a connect() primero.")
        return self.SessionLocal()
    
    def close(self):
        """Cierra la conexión con la BD"""
        if self.engine:
            self.engine.dispose()
            logger.info("Conexión a PostgreSQL cerrada")


# Instancia global
db = DatabaseConnection()


# ============================================
# Funciones de ejemplo para cada tabla
# ============================================

def create_session_user(
    session_id: str,
    user_id: str,
    token: str,
    ip_origin: str,
    user_agent: str,
    status: str = "active"
):
    """
    Crea una nueva sesión de usuario
    
    Ejemplo:
        create_session_user(
            session_id="sess_123",
            user_id="user_456",
            token="token_xyz",
            ip_origin="192.168.1.1",
            user_agent="Mozilla/5.0...",
            status="active"
        )
    """
    from datetime import datetime
    
    session = db.get_session()
    try:
        query = text("""
            INSERT INTO sessions_user (
                id, user_id, token, ip_origin, user_agent,
                created_at, last_activity_at, status,
                record_created_at, record_updated_at
            ) VALUES (
                :id, :user_id, :token, :ip_origin, :user_agent,
                :created_at, :last_activity_at, :status,
                :record_created_at, :record_updated_at
            )
        """)
        
        now = datetime.now().isoformat()
        session.execute(query, {
            "id": session_id,
            "user_id": user_id,
            "token": token,
            "ip_origin": ip_origin,
            "user_agent": user_agent,
            "created_at": now,
            "last_activity_at": now,
            "status": status,
            "record_created_at": now,
            "record_updated_at": now,
        })
        session.commit()
        logger.info(f"Sesión creada: {session_id}")
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error creando sesión: {e}")
        raise
    finally:
        session.close()


def get_session_by_token(token: str):
    """
    Obtiene una sesión por su token
    
    Ejemplo:
        session_data = get_session_by_token("token_xyz")
    """
    session = db.get_session()
    try:
        query = text("""
            SELECT * FROM sessions_user
            WHERE token = :token
            LIMIT 1
        """)
        
        result = session.execute(query, {"token": token})
        return result.fetchone()
        
    finally:
        session.close()


def check_tables_exist():
    """
    Verifica que todas las tablas hayan sido creadas correctamente
    
    Returns:
        dict: {table_name: exists_bool, ...}
    """
    session = db.get_session()
    try:
        query = text("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'
        """)
        
        result = session.execute(query)
        tables = [row[0] for row in result]
        
        expected_tables = {
            'sessions_user',
            'app_tokens',
            'access_history',
            'login_attempt_control',
            'invalidated_tokens'
        }
        
        return {table: table in tables for table in expected_tables}
        
    finally:
        session.close()


def get_database_stats():
    """
    Obtiene estadísticas de la base de datos
    
    Returns:
        dict: Información sobre tamaño y registros
    """
    session = db.get_session()
    try:
        # Tamaño total
        size_query = text("SELECT pg_size_pretty(pg_database_size('auth_db')) as size")
        size_result = session.execute(size_query).fetchone()
        
        # Conteo de registros por tabla
        count_query = text("""
            SELECT
                (SELECT COUNT(*) FROM sessions_user) as sessions_count,
                (SELECT COUNT(*) FROM app_tokens) as tokens_count,
                (SELECT COUNT(*) FROM access_history) as history_count,
                (SELECT COUNT(*) FROM login_attempt_control) as attempts_count,
                (SELECT COUNT(*) FROM invalidated_tokens) as invalidated_count
        """)
        
        counts_result = session.execute(count_query).fetchone()
        
        return {
            "database_size": size_result[0] if size_result else "Unknown",
            "sessions_count": counts_result[0] if counts_result else 0,
            "tokens_count": counts_result[1] if counts_result else 0,
            "access_history_count": counts_result[2] if counts_result else 0,
            "login_attempts_count": counts_result[3] if counts_result else 0,
            "invalidated_tokens_count": counts_result[4] if counts_result else 0,
        }
        
    finally:
        session.close()


# ============================================
# Inicialización
# ============================================

if __name__ == "__main__":
    import sys
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Conectar a la BD
    if db.connect():
        print("✓ Conexión exitosa")
        
        # Verificar tablas
        tables = check_tables_exist()
        print("\nTablas:")
        for table, exists in tables.items():
            status = "✓" if exists else "✗"
            print(f"  {status} {table}")
        
        # Mostrar estadísticas
        print("\nEstadísticas:")
        stats = get_database_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Cerrar conexión
        db.close()
        
    else:
        print("✗ Error al conectar")
        sys.exit(1)
