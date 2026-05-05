import pytest
from sqlalchemy.orm import Session

from app.services.rol_service import (
    crear_rol,
    obtener_rol_por_id,
    obtener_rol_por_nombre,
    listar_roles,
    listar_roles_activos,
    actualizar_rol,
    desactivar_rol,
    existe_rol_activo,
)
from app.schemas.rol import RolCreate, RolUpdate
from app.core.exceptions import RecursoNoEncontrado, ConflictoDeNegocio


class TestRolService:
    """Tests para el servicio de roles"""

    def test_crear_rol_exitoso(self, db: Session):
        """Test creación exitosa de un rol"""
        rol_data = RolCreate(
            nombre="ROL_ADMIN",
            descripcion="Rol de administrador"
        )

        rol = crear_rol(db, rol_data)

        assert rol.nombre == "ROL_ADMIN"
        assert rol.descripcion == "Rol de administrador"
        assert rol.estado == "activo"
        assert rol.id is not None

    def test_crear_rol_duplicado(self, db: Session):
        """Test que no se puede crear roles con nombres duplicados"""
        rol_data = RolCreate(
            nombre="ROL_ADMIN",
            descripcion="Rol de administrador"
        )

        # Crear el primer rol
        crear_rol(db, rol_data)

        # Intentar crear el mismo rol debe fallar
        with pytest.raises(ConflictoDeNegocio):
            crear_rol(db, rol_data)

    def test_obtener_rol_por_id_existente(self, db: Session):
        """Test obtener rol por ID cuando existe"""
        rol_data = RolCreate(
            nombre="ROL_TEST",
            descripcion="Rol de prueba"
        )
        rol_creado = crear_rol(db, rol_data)

        rol_obtenido = obtener_rol_por_id(db, rol_creado.id)

        assert rol_obtenido.id == rol_creado.id
        assert rol_obtenido.nombre == "ROL_TEST"

    def test_obtener_rol_por_id_inexistente(self, db: Session):
        """Test obtener rol por ID cuando no existe"""
        with pytest.raises(RecursoNoEncontrado):
            obtener_rol_por_id(db, 999)

    def test_obtener_rol_por_nombre_existente(self, db: Session):
        """Test obtener rol por nombre cuando existe"""
        rol_data = RolCreate(
            nombre="ROL_USUARIO",
            descripcion="Rol de usuario"
        )
        crear_rol(db, rol_data)

        rol_obtenido = obtener_rol_por_nombre(db, "ROL_USUARIO")

        assert rol_obtenido.nombre == "ROL_USUARIO"

    def test_obtener_rol_por_nombre_inexistente(self, db: Session):
        """Test obtener rol por nombre cuando no existe"""
        with pytest.raises(RecursoNoEncontrado):
            obtener_rol_por_nombre(db, "ROL_INEXISTENTE")

    def test_listar_roles_vacio(self, db: Session):
        """Test listar roles cuando no hay ninguno"""
        roles = listar_roles(db)
        assert len(roles) == 0

    def test_listar_roles_con_datos(self, db: Session):
        """Test listar roles con datos"""
        # Crear algunos roles
        crear_rol(db, RolCreate(nombre="ROL_A", descripcion="Rol A"))
        crear_rol(db, RolCreate(nombre="ROL_B", descripcion="Rol B"))

        roles = listar_roles(db)

        assert len(roles) == 2
        nombres = [r.nombre for r in roles]
        assert "ROL_A" in nombres
        assert "ROL_B" in nombres

    def test_listar_roles_activos(self, db: Session):
        """Test listar solo roles activos"""
        # Crear roles activos e inactivos
        rol_activo = crear_rol(db, RolCreate(nombre="ROL_ACTIVO", descripcion="Activo"))
        rol_inactivo = crear_rol(db, RolCreate(nombre="ROL_INACTIVO", descripcion="Inactivo"))
        desactivar_rol(db, rol_inactivo)

        roles_activos = listar_roles_activos(db)

        assert len(roles_activos) == 1
        assert roles_activos[0].nombre == "ROL_ACTIVO"

    def test_actualizar_rol_existente(self, db: Session):
        """Test actualizar un rol existente"""
        # Crear rol
        rol_creado = crear_rol(db, RolCreate(
            nombre="ROL_ORIGINAL",
            descripcion="Descripción original"
        ))

        # Actualizar
        update_data = RolUpdate(
            nombre="ROL_ACTUALIZADO",
            descripcion="Descripción actualizada"
        )

        rol_actualizado = actualizar_rol(db, rol_creado, update_data)

        assert rol_actualizado.nombre == "ROL_ACTUALIZADO"
        assert rol_actualizado.descripcion == "Descripción actualizada"

    def test_actualizar_rol_inexistente(self, db: Session):
        """Test actualizar un rol que no existe"""
        update_data = RolUpdate(nombre="NUEVO_NOMBRE")

        with pytest.raises(AttributeError):  # O el error que corresponda
            actualizar_rol(db, None, update_data)

    def test_desactivar_rol_existente(self, db: Session):
        """Test desactivar un rol existente"""
        rol_creado = crear_rol(db, RolCreate(
            nombre="ROL_A_DESACTIVAR",
            descripcion="Rol a desactivar"
        ))

        rol_desactivado = desactivar_rol(db, rol_creado)

        assert rol_desactivado.estado == "inactivo"

    def test_desactivar_rol_inexistente(self, db: Session):
        """Test desactivar un rol que no existe"""
        # Crear un rol falso
        from app.models.rol import Rol
        rol_falso = Rol(id=999, nombre="FALSO", descripcion="Falso", estado="activo")

        with pytest.raises(Exception):  # Debería fallar
            desactivar_rol(db, rol_falso)

    def test_existe_rol_activo_existente(self, db: Session):
        """Test verificar si existe un rol activo"""
        rol_creado = crear_rol(db, RolCreate(
            nombre="ROL_ACTIVO_TEST",
            descripcion="Rol activo para test"
        ))

        existe = existe_rol_activo(db, rol_creado.id)
        assert existe is True

    def test_existe_rol_activo_inactivo(self, db: Session):
        """Test verificar rol inactivo"""
        rol_creado = crear_rol(db, RolCreate(
            nombre="ROL_INACTIVO_TEST",
            descripcion="Rol inactivo para test"
        ))
        desactivar_rol(db, rol_creado)

        existe = existe_rol_activo(db, rol_creado.id)
        assert existe is False

    def test_existe_rol_activo_inexistente(self, db: Session):
        """Test verificar rol que no existe"""
        existe = existe_rol_activo(db, 999)
        assert existe is False