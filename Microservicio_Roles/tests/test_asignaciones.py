import pytest
from sqlalchemy.orm import Session

from app.services.asignacion_service import (
    asignar_permisos_a_rol,
    remover_permiso_de_rol,
    obtener_permisos_de_rol,
    obtener_roles_de_permiso,
    asignar_rol_a_usuario,
    remover_rol_de_usuario,
    listar_roles_de_usuario,
    obtener_usuarios_de_rol,
    asignar_permiso_a_rol,
)
from app.services.rol_service import crear_rol
from app.services.permiso_service import crear_permiso
from app.schemas.rol import RolCreate
from app.schemas.permiso import PermisoCreate
from app.core.exceptions import RecursoNoEncontrado, ConflictoDeNegocio


class TestAsignacionService:
    """Tests para el servicio de asignaciones"""

    def test_asignar_permisos_a_rol_exitoso(self, db: Session):
        """Test asignar múltiples permisos a un rol"""
        # Crear rol y permisos
        rol = crear_rol(db, RolCreate(nombre="ROL_TEST", descripcion="Rol test"))
        permiso1 = crear_permiso(db, PermisoCreate(
            codigo="PERM_1", nombre="Permiso 1", descripcion="Desc",
            modulo="TEST", operacion="READ"
        ))
        permiso2 = crear_permiso(db, PermisoCreate(
            codigo="PERM_2", nombre="Permiso 2", descripcion="Desc",
            modulo="TEST", operacion="CREATE"
        ))

        # Asignar permisos
        asignaciones = asignar_permisos_a_rol(db, rol.id, [permiso1.id, permiso2.id], 1)

        assert len(asignaciones) == 2
        assert asignaciones[0].rol_id == rol.id
        assert asignaciones[1].rol_id == rol.id

    def test_asignar_permiso_a_rol_exitoso(self, db: Session):
        """Test asignar un solo permiso a un rol"""
        # Crear rol y permiso
        rol = crear_rol(db, RolCreate(nombre="ROL_SINGLE", descripcion="Rol single"))
        permiso = crear_permiso(db, PermisoCreate(
            codigo="PERM_SINGLE", nombre="Permiso single", descripcion="Desc",
            modulo="TEST", operacion="READ"
        ))

        # Asignar permiso
        asignacion = asignar_permiso_a_rol(db, rol.id, permiso.id, 1)

        assert asignacion.rol_id == rol.id
        assert asignacion.permiso_id == permiso.id

    def test_asignar_permiso_a_rol_inexistente(self, db: Session):
        """Test asignar permiso a rol que no existe"""
        permiso = crear_permiso(db, PermisoCreate(
            codigo="PERM_TEST", nombre="Permiso test", descripcion="Desc",
            modulo="TEST", operacion="READ"
        ))

        with pytest.raises(RecursoNoEncontrado):
            asignar_permiso_a_rol(db, 999, permiso.id, 1)

    def test_remover_permiso_de_rol_existente(self, db: Session):
        """Test remover permiso de rol existente"""
        # Crear y asignar
        rol = crear_rol(db, RolCreate(nombre="ROL_REMOVE", descripcion="Rol remove"))
        permiso = crear_permiso(db, PermisoCreate(
            codigo="PERM_REMOVE", nombre="Permiso remove", descripcion="Desc",
            modulo="TEST", operacion="READ"
        ))
        asignar_permiso_a_rol(db, rol.id, permiso.id, 1)

        # Remover
        remover_permiso_de_rol(db, rol.id, permiso.id)

        # Verificar que ya no está asignado
        permisos = obtener_permisos_de_rol(db, rol.id)
        assert len(permisos) == 0

    def test_remover_permiso_de_rol_no_asignado(self, db: Session):
        """Test remover permiso que no está asignado"""
        rol = crear_rol(db, RolCreate(nombre="ROL_NO_ASSIGN", descripcion="Rol no assign"))
        permiso = crear_permiso(db, PermisoCreate(
            codigo="PERM_NO_ASSIGN", nombre="Permiso no assign", descripcion="Desc",
            modulo="TEST", operacion="READ"
        ))

        with pytest.raises(RecursoNoEncontrado):
            remover_permiso_de_rol(db, rol.id, permiso.id)

    def test_obtener_permisos_de_rol_con_asignaciones(self, db: Session):
        """Test obtener permisos asignados a un rol"""
        # Crear rol y permisos
        rol = crear_rol(db, RolCreate(nombre="ROL_PERMS", descripcion="Rol perms"))
        permiso1 = crear_permiso(db, PermisoCreate(
            codigo="PERM_ROL_1", nombre="Permiso rol 1", descripcion="Desc",
            modulo="TEST", operacion="READ"
        ))
        permiso2 = crear_permiso(db, PermisoCreate(
            codigo="PERM_ROL_2", nombre="Permiso rol 2", descripcion="Desc",
            modulo="TEST", operacion="CREATE"
        ))

        # Asignar
        asignar_permisos_a_rol(db, rol.id, [permiso1.id, permiso2.id], 1)

        # Obtener
        permisos = obtener_permisos_de_rol(db, rol.id)

        assert len(permisos) == 2
        codigos = [p.codigo for p in permisos]
        assert "PERM_ROL_1" in codigos
        assert "PERM_ROL_2" in codigos

    def test_obtener_permisos_de_rol_sin_asignaciones(self, db: Session):
        """Test obtener permisos de rol sin asignaciones"""
        rol = crear_rol(db, RolCreate(nombre="ROL_EMPTY", descripcion="Rol empty"))

        permisos = obtener_permisos_de_rol(db, rol.id)

        assert len(permisos) == 0

    def test_obtener_roles_de_permiso_con_asignaciones(self, db: Session):
        """Test obtener roles que tienen un permiso"""
        # Crear roles y permiso
        rol1 = crear_rol(db, RolCreate(nombre="ROL_PERM_1", descripcion="Rol perm 1"))
        rol2 = crear_rol(db, RolCreate(nombre="ROL_PERM_2", descripcion="Rol perm 2"))
        permiso = crear_permiso(db, PermisoCreate(
            codigo="PERM_SHARED", nombre="Permiso shared", descripcion="Desc",
            modulo="TEST", operacion="READ"
        ))

        # Asignar permiso a ambos roles
        asignar_permiso_a_rol(db, rol1.id, permiso.id, 1)
        asignar_permiso_a_rol(db, rol2.id, permiso.id, 1)

        # Obtener roles
        roles = obtener_roles_de_permiso(db, permiso.id)

        assert len(roles) == 2
        nombres = [r.nombre for r in roles]
        assert "ROL_PERM_1" in nombres
        assert "ROL_PERM_2" in nombres

    def test_asignar_rol_a_usuario_exitoso(self, db: Session):
        """Test asignar rol a usuario exitosamente"""
        rol = crear_rol(db, RolCreate(nombre="ROL_USER", descripcion="Rol user"))

        asignacion = asignar_rol_a_usuario(db, "usuario123", rol.id, 1)

        assert asignacion.usuario_id == "usuario123"
        assert asignacion.rol_id == rol.id
        assert asignacion.estado == "activo"

    def test_asignar_rol_inactivo_a_usuario(self, db: Session):
        """Test que no se puede asignar rol inactivo"""
        rol = crear_rol(db, RolCreate(nombre="ROL_INACTIVO", descripcion="Rol inactivo"))
        from app.services.rol_service import desactivar_rol
        desactivar_rol(db, rol)

        with pytest.raises(ConflictoDeNegocio):
            asignar_rol_a_usuario(db, "usuario123", rol.id, 1)

    def test_asignar_rol_inexistente_a_usuario(self, db: Session):
        """Test asignar rol que no existe"""
        with pytest.raises(RecursoNoEncontrado):
            asignar_rol_a_usuario(db, "usuario123", 999, 1)

    def test_remover_rol_de_usuario_existente(self, db: Session):
        """Test remover rol de usuario existente"""
        rol = crear_rol(db, RolCreate(nombre="ROL_REMOVE_USER", descripcion="Rol remove user"))
        asignar_rol_a_usuario(db, "usuario456", rol.id, 1)

        asignacion = remover_rol_de_usuario(db, "usuario456", rol.id)

        assert asignacion.estado == "inactivo"

    def test_remover_rol_de_usuario_no_asignado(self, db: Session):
        """Test remover rol que no está asignado al usuario"""
        rol = crear_rol(db, RolCreate(nombre="ROL_NOT_ASSIGNED", descripcion="Rol not assigned"))

        with pytest.raises(RecursoNoEncontrado):
            remover_rol_de_usuario(db, "usuario789", rol.id)

    def test_listar_roles_de_usuario_con_asignaciones(self, db: Session):
        """Test listar roles asignados a un usuario"""
        rol1 = crear_rol(db, RolCreate(nombre="ROL_USER_1", descripcion="Rol user 1"))
        rol2 = crear_rol(db, RolCreate(nombre="ROL_USER_2", descripcion="Rol user 2"))

        asignar_rol_a_usuario(db, "usuario_test", rol1.id, 1)
        asignar_rol_a_usuario(db, "usuario_test", rol2.id, 1)

        asignaciones = listar_roles_de_usuario(db, "usuario_test")

        assert len(asignaciones) == 2
        rol_ids = [a.rol_id for a in asignaciones]
        assert rol1.id in rol_ids
        assert rol2.id in rol_ids

    def test_obtener_usuarios_de_rol_con_asignaciones(self, db: Session):
        """Test obtener usuarios asignados a un rol"""
        rol = crear_rol(db, RolCreate(nombre="ROL_USERS", descripcion="Rol users"))

        asignar_rol_a_usuario(db, "user1", rol.id, 1)
        asignar_rol_a_usuario(db, "user2", rol.id, 1)

        asignaciones = obtener_usuarios_de_rol(db, rol.id)

        assert len(asignaciones) == 2
        user_ids = [a.usuario_id for a in asignaciones]
        assert "user1" in user_ids
        assert "user2" in user_ids