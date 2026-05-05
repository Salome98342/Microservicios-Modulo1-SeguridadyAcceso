import pytest
from sqlalchemy.orm import Session

from app.services.validacion_service import (
    validar_permiso_de_rol,
    verificar_existencia_rol,
)
from app.services.rol_service import crear_rol
from app.services.permiso_service import crear_permiso
from app.services.asignacion_service import asignar_permiso_a_rol
from app.schemas.rol import RolCreate
from app.schemas.permiso import PermisoCreate


class TestValidacionService:
    """Tests para el servicio de validación"""

    def test_validar_permiso_de_rol_valido(self, db: Session):
        """Test validar permiso válido asignado a rol"""
        # Crear rol, permiso y asignación
        rol = crear_rol(db, RolCreate(nombre="ROL_VALIDO", descripcion="Rol válido"))
        permiso = crear_permiso(db, PermisoCreate(
            codigo="PERM_VALIDO", nombre="Permiso válido", descripcion="Desc",
            modulo="TEST", operacion="READ"
        ))
        asignar_permiso_a_rol(db, rol.id, permiso.id, 1)

        # Validar por ID
        valido = validar_permiso_de_rol(db, str(rol.id), str(permiso.id))
        assert valido is True

        # Validar por nombre/código
        valido = validar_permiso_de_rol(db, rol.nombre, permiso.codigo)
        assert valido is True

    def test_validar_permiso_de_rol_invalido(self, db: Session):
        """Test validar permiso no asignado a rol"""
        # Crear rol y permiso sin asignar
        rol = crear_rol(db, RolCreate(nombre="ROL_INVALIDO", descripcion="Rol inválido"))
        permiso = crear_permiso(db, PermisoCreate(
            codigo="PERM_INVALIDO", nombre="Permiso inválido", descripcion="Desc",
            modulo="TEST", operacion="READ"
        ))

        # Validar
        valido = validar_permiso_de_rol(db, rol.nombre, permiso.codigo)
        assert valido is False

    def test_validar_permiso_de_rol_inexistente(self, db: Session):
        """Test validar con rol o permiso inexistente"""
        # Validar rol inexistente
        valido = validar_permiso_de_rol(db, "ROL_INEXISTENTE", "PERM_VALIDO")
        assert valido is False

        # Validar permiso inexistente
        valido = validar_permiso_de_rol(db, "ROL_VALIDO", "PERM_INEXISTENTE")
        assert valido is False

    def test_validar_permiso_de_rol_inactivo(self, db: Session):
        """Test validar permiso de rol inactivo"""
        # Crear rol inactivo y asignación
        rol = crear_rol(db, RolCreate(nombre="ROL_INACTIVO", descripcion="Rol inactivo"))
        from app.services.rol_service import desactivar_rol
        desactivar_rol(db, rol)

        permiso = crear_permiso(db, PermisoCreate(
            codigo="PERM_INACTIVO", nombre="Permiso inactivo", descripcion="Desc",
            modulo="TEST", operacion="READ"
        ))
        asignar_permiso_a_rol(db, rol.id, permiso.id, 1)

        # Validar - debería ser False porque el rol está inactivo
        valido = validar_permiso_de_rol(db, rol.nombre, permiso.codigo)
        assert valido is False

    def test_verificar_existencia_rol_existente_activo(self, db: Session):
        """Test verificar rol existente y activo"""
        rol = crear_rol(db, RolCreate(nombre="ROL_EXISTENTE", descripcion="Rol existente"))

        existe, activo = verificar_existencia_rol(db, str(rol.id))
        assert existe is True
        assert activo is True

        existe, activo = verificar_existencia_rol(db, rol.nombre)
        assert existe is True
        assert activo is True

    def test_verificar_existencia_rol_existente_inactivo(self, db: Session):
        """Test verificar rol existente pero inactivo"""
        rol = crear_rol(db, RolCreate(nombre="ROL_INACTIVO", descripcion="Rol inactivo"))
        from app.services.rol_service import desactivar_rol
        desactivar_rol(db, rol)

        existe, activo = verificar_existencia_rol(db, rol.nombre)
        assert existe is True
        assert activo is False

    def test_verificar_existencia_rol_inexistente(self, db: Session):
        """Test verificar rol inexistente"""
        existe, activo = verificar_existencia_rol(db, "ROL_INEXISTENTE")
        assert existe is False
        assert activo is False

    def test_verificar_existencia_rol_por_id_inexistente(self, db: Session):
        """Test verificar rol por ID inexistente"""
        existe, activo = verificar_existencia_rol(db, "999")
        assert existe is False
        assert activo is False

    def test_validar_permiso_de_rol_con_id_numerico(self, db: Session):
        """Test validar usando IDs numéricos como strings"""
        rol = crear_rol(db, RolCreate(nombre="ROL_NUM", descripcion="Rol num"))
        permiso = crear_permiso(db, PermisoCreate(
            codigo="PERM_NUM", nombre="Permiso num", descripcion="Desc",
            modulo="TEST", operacion="READ"
        ))
        asignar_permiso_a_rol(db, rol.id, permiso.id, 1)

        # Validar usando strings de IDs
        valido = validar_permiso_de_rol(db, str(rol.id), str(permiso.id))
        assert valido is True

    def test_validar_permiso_de_rol_con_nombres(self, db: Session):
        """Test validar usando nombres/códigos"""
        rol = crear_rol(db, RolCreate(nombre="ROL_NOMBRE", descripcion="Rol nombre"))
        permiso = crear_permiso(db, PermisoCreate(
            codigo="PERM_CODIGO", nombre="Permiso código", descripcion="Desc",
            modulo="TEST", operacion="READ"
        ))
        asignar_permiso_a_rol(db, rol.id, permiso.id, 1)

        # Validar usando nombres
        valido = validar_permiso_de_rol(db, rol.nombre, permiso.codigo)
        assert valido is True