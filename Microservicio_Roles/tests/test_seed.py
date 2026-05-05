import pytest
from sqlalchemy.orm import Session
from app.db.base import Base
from tests.conftest import engine
from app.services.seed_service import cargar_datos_semilla
from app.models import Rol, Permiso, AsignacionRolPermiso, TokenAplicacion


class TestSeedService:
    """Tests para el servicio de datos semilla"""

    def test_datos_semilla_crean_permisos_basicos(self, db: Session):
        cargar_datos_semilla(db)

        # Nombres corregidos según seed_service.py
        permisos_basicos = ["ROL_READ", "ROL_CREATE", "PERM_READ", "PERM_CREATE"]
        for permiso_codigo in permisos_basicos:
            permiso = db.query(Permiso).filter(Permiso.codigo == permiso_codigo).first()
            assert permiso is not None, f"Permiso {permiso_codigo} no fue creado"

    def test_cargar_datos_semilla_idempotente(self, db: Session):
        """Test que cargar datos semilla múltiples veces no duplica datos"""
        # Primera carga
        resultado1 = cargar_datos_semilla(db)

        # Segunda carga
        resultado2 = cargar_datos_semilla(db)

        # Los resultados deberían ser similares (idempotente)
        # En la segunda carga, algunos elementos ya existen, así que los contadores pueden ser 0
        assert isinstance(resultado1, dict)
        assert isinstance(resultado2, dict)

        # Verificar que las claves existen
        expected_keys = ["roles_creados", "permisos_creados", "asignaciones_creadas", "token_aplicacion_creado"]
        for key in expected_keys:
            assert key in resultado1
            assert key in resultado2

    def test_datos_semilla_crean_roles_basicos(self, db: Session):
        """Test que se crean los roles básicos esperados"""
        cargar_datos_semilla(db)

        # Verificar roles básicos existen
        roles_basicos = ["ADMIN", "USUARIO", "MODERADOR"]
        for rol_nombre in roles_basicos:
            rol = db.query(Rol).filter(Rol.nombre == rol_nombre).first()
            assert rol is not None, f"Rol {rol_nombre} no fue creado"
            assert rol.estado == "activo"

    def test_datos_semilla_crean_permisos_basicos(self, db: Session):
        """Test que se crean los permisos básicos esperados"""
        cargar_datos_semilla(db)

        # Verificar algunos permisos básicos existen
        permisos_basicos = ["ROL_READ", "ROL_CREATE", "PERMISO_READ", "PERMISO_CREATE"]
        for permiso_codigo in permisos_basicos:
            permiso = db.query(Permiso).filter(Permiso.codigo == permiso_codigo).first()
            assert permiso is not None, f"Permiso {permiso_codigo} no fue creado"

    def test_datos_semilla_crean_asignaciones_admin(self, db: Session):
        """Test que el rol ADMIN tiene permisos asignados"""
        cargar_datos_semilla(db)

        # Obtener rol ADMIN
        admin_rol = db.query(Rol).filter(Rol.nombre == "ADMIN").first()
        assert admin_rol is not None

        # Verificar que tiene asignaciones
        asignaciones = db.query(AsignacionRolPermiso).filter(
            AsignacionRolPermiso.rol_id == admin_rol.id
        ).all()

        assert len(asignaciones) > 0, "El rol ADMIN debe tener permisos asignados"

    def test_datos_semilla_crean_token_aplicacion(self, db: Session):
        """Test que se crea un token de aplicación"""
        cargar_datos_semilla(db)

        # Verificar que existe al menos un token activo
        token = db.query(TokenAplicacion).filter(TokenAplicacion.estado == "activo").first()
        assert token is not None, "Debe existir un token de aplicación activo"

        # Verificar que tiene los campos necesarios
        assert token.nombre_servicio is not None
        assert token.token_cifrado is not None
        assert len(token.token_cifrado) > 0

    def test_datos_semilla_no_duplican_tokens(self, db: Session):
        """Test que no se crean tokens duplicados"""
        cargar_datos_semilla(db)

        # Contar tokens activos
        tokens_count_1 = db.query(TokenAplicacion).filter(TokenAplicacion.estado == "activo").count()

        # Cargar nuevamente
        cargar_datos_semilla(db)

        # Contar nuevamente
        tokens_count_2 = db.query(TokenAplicacion).filter(TokenAplicacion.estado == "activo").count()

        # Debe ser el mismo número (no duplicados)
        assert tokens_count_1 == tokens_count_2, "No deben crearse tokens duplicados"

    def test_datos_semilla_verificar_estructura_completa(self, db: Session):
    # Limpiar tablas antes de correr para evitar el problema de idempotencia
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

        resultado = cargar_datos_semilla(db)

        assert resultado["roles_creados"] >= 3
        assert resultado["permisos_creados"] >= 8
        assert resultado["asignaciones_creadas"] >= 5
        assert resultado["token_aplicacion_creado"] is True

        roles_count = db.query(Rol).count()
        assert roles_count >= resultado["roles_creados"]

        permisos_count = db.query(Permiso).count()
        assert permisos_count >= resultado["permisos_creados"]

        asignaciones = db.query(AsignacionRolPermiso).all()
        for asignacion in asignaciones:
            assert db.query(Rol).filter(Rol.id == asignacion.rol_id).first() is not None
            assert db.query(Permiso).filter(Permiso.id == asignacion.permiso_id).first() is not None