import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.config import settings


# ── Base de datos de pruebas ───────────────────────────────────────────────────

# Usar SQLite en memoria para pruebas rápidas
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)

# Crear todas las tablas
Base.metadata.create_all(bind=engine)

# Session factory para pruebas
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def db() -> Session:
    """
    Fixture que proporciona una sesión de base de datos limpia para cada test.
    Se encarga de crear y limpiar las tablas automáticamente.
    """
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)

    # Crear sesión
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        # Limpiar datos después de cada test
        db.rollback()
        db.close()

        # Opcional: dropear y recrear tablas para aislamiento completo
        # Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_with_seed(db: Session):
    """
    Fixture que proporciona una sesión con datos semilla cargados.
    Útil para tests que necesitan datos iniciales.
    """
    from app.services.seed_service import cargar_datos_semilla

    # Cargar datos semilla
    resultado = cargar_datos_semilla(db)
    db.commit()

    yield db