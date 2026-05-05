import pytest
from sqlalchemy.orm import Session

from app.services.permiso_service import (
    crear_permiso,
    obtener_permiso_por_id,
    obtener_permiso_por_codigo,
    listar_permisos,
    listar_permisos_por_modulo,
    actualizar_permiso,
    eliminar_permiso,
)
from app.schemas.permiso import PermisoCreate, PermisoUpdate
from app.core.exceptions import RecursoNoEncontrado, ConflictoDeNegocio


class TestPermisoService:
    """Tests para el servicio de permisos"""

    def test_crear_permiso_exitoso(self, db: Session):
        """Test creación exitosa de un permiso"""
        permiso_data = PermisoCreate(
            codigo="PERM_READ",
            nombre="Permiso de lectura",
            descripcion="Permite leer recursos",
            modulo="GENERAL",
            operacion="READ"
        )

        permiso = crear_permiso(db, permiso_data)

        assert permiso.codigo == "PERM_READ"
        assert permiso.nombre == "Permiso de lectura"
        assert permiso.modulo == "GENERAL"
        assert permiso.operacion == "READ"
        assert permiso.id is not None

    def test_crear_permiso_codigo_duplicado(self, db: Session):
        """Test que no se puede crear permisos con códigos duplicados"""
        permiso_data = PermisoCreate(
            codigo="PERM_DUPLICADO",
            nombre="Permiso duplicado",
            descripcion="Descripción",
            modulo="TEST",
            operacion="CREATE"
        )

        # Crear el primer permiso
        crear_permiso(db, permiso_data)

        # Intentar crear el mismo código debe fallar
        with pytest.raises(ConflictoDeNegocio):
            crear_permiso(db, permiso_data)

    def test_obtener_permiso_por_id_existente(self, db: Session):
        """Test obtener permiso por ID cuando existe"""
        permiso_data = PermisoCreate(
            codigo="PERM_TEST_ID",
            nombre="Permiso test ID",
            descripcion="Para test",
            modulo="TEST",
            operacion="READ"
        )
        permiso_creado = crear_permiso(db, permiso_data)

        permiso_obtenido = obtener_permiso_por_id(db, permiso_creado.id)

        assert permiso_obtenido.id == permiso_creado.id
        assert permiso_obtenido.codigo == "PERM_TEST_ID"

    def test_obtener_permiso_por_id_inexistente(self, db: Session):
        """Test obtener permiso por ID cuando no existe"""
        with pytest.raises(RecursoNoEncontrado):
            obtener_permiso_por_id(db, 999)

    def test_obtener_permiso_por_codigo_existente(self, db: Session):
        """Test obtener permiso por código cuando existe"""
        permiso_data = PermisoCreate(
            codigo="PERM_TEST_CODIGO",
            nombre="Permiso test código",
            descripcion="Para test",
            modulo="TEST",
            operacion="UPDATE"
        )
        crear_permiso(db, permiso_data)

        permiso_obtenido = obtener_permiso_por_codigo(db, "PERM_TEST_CODIGO")

        assert permiso_obtenido.codigo == "PERM_TEST_CODIGO"

    def test_obtener_permiso_por_codigo_inexistente(self, db: Session):
        """Test obtener permiso por código cuando no existe"""
        with pytest.raises(RecursoNoEncontrado):
            obtener_permiso_por_codigo(db, "PERM_INEXISTENTE")

    def test_listar_permisos_vacio(self, db: Session):
        """Test listar permisos cuando no hay ninguno"""
        permisos = listar_permisos(db)
        assert len(permisos) == 0

    def test_listar_permisos_con_datos(self, db: Session):
        """Test listar permisos con datos"""
        # Crear algunos permisos
        crear_permiso(db, PermisoCreate(
            codigo="PERM_A", nombre="Permiso A", descripcion="Desc A",
            modulo="MOD_A", operacion="READ"
        ))
        crear_permiso(db, PermisoCreate(
            codigo="PERM_B", nombre="Permiso B", descripcion="Desc B",
            modulo="MOD_B", operacion="CREATE"
        ))

        permisos = listar_permisos(db)

        assert len(permisos) == 2
        codigos = [p.codigo for p in permisos]
        assert "PERM_A" in codigos
        assert "PERM_B" in codigos

    def test_listar_permisos_por_modulo(self, db: Session):
        """Test listar permisos agrupados por módulo"""
        # Crear permisos en diferentes módulos
        crear_permiso(db, PermisoCreate(
            codigo="PERM_MOD1_A", nombre="Permiso A", descripcion="Desc",
            modulo="MODULO_1", operacion="READ"
        ))
        crear_permiso(db, PermisoCreate(
            codigo="PERM_MOD1_B", nombre="Permiso B", descripcion="Desc",
            modulo="MODULO_1", operacion="CREATE"
        ))
        crear_permiso(db, PermisoCreate(
            codigo="PERM_MOD2_A", nombre="Permiso C", descripcion="Desc",
            modulo="MODULO_2", operacion="UPDATE"
        ))

        permisos_por_modulo = listar_permisos_por_modulo(db)

        # Verificar que MODULO_1 tenga 2 permisos
        assert "MODULO_1" in permisos_por_modulo
        assert len(permisos_por_modulo["MODULO_1"]) == 2

        # Verificar que MODULO_2 tenga 1 permiso
        assert "MODULO_2" in permisos_por_modulo
        assert len(permisos_por_modulo["MODULO_2"]) == 1

    def test_actualizar_permiso_existente(self, db: Session):
        """Test actualizar un permiso existente"""
        # Crear permiso
        permiso_creado = crear_permiso(db, PermisoCreate(
            codigo="PERM_ORIGINAL",
            nombre="Nombre original",
            descripcion="Descripción original",
            modulo="MOD_ORIGINAL",
            operacion="READ"
        ))

        # Actualizar
        update_data = PermisoUpdate(
            nombre="Nombre actualizado",
            descripcion="Descripción actualizada",
            modulo="MOD_ACTUALIZADO",
            operacion="UPDATE"
        )

        permiso_actualizado = actualizar_permiso(db, permiso_creado, update_data)

        assert permiso_actualizado.nombre == "Nombre actualizado"
        assert permiso_actualizado.descripcion == "Descripción actualizada"
        assert permiso_actualizado.modulo == "MOD_ACTUALIZADO"
        assert permiso_actualizado.operacion == "UPDATE"

    def test_eliminar_permiso_sin_asignaciones(self, db: Session):
        """Test eliminar un permiso que no está asignado a ningún rol"""
        permiso_creado = crear_permiso(db, PermisoCreate(
            codigo="PERM_A_ELIMINAR",
            nombre="Permiso a eliminar",
            descripcion="Para eliminar",
            modulo="TEST",
            operacion="DELETE"
        ))

        # Debería eliminarse sin problemas
        eliminar_permiso(db, permiso_creado)

        # Verificar que ya no existe
        with pytest.raises(RecursoNoEncontrado):
            obtener_permiso_por_id(db, permiso_creado.id)

    def test_eliminar_permiso_con_asignaciones(self, db: Session):
        """Test que no se puede eliminar un permiso asignado a roles"""
        from app.services.asignacion_service import asignar_permisos_a_rol
        from app.services.rol_service import crear_rol

        # Crear rol y permiso
        rol = crear_rol(db, RolCreate(nombre="ROL_TEST", descripcion="Rol test"))
        permiso = crear_permiso(db, PermisoCreate(
            codigo="PERM_ASIGNADO",
            nombre="Permiso asignado",
            descripcion="No se puede eliminar",
            modulo="TEST",
            operacion="READ"
        ))

        # Asignar permiso al rol
        asignar_permisos_a_rol(db, rol.id, [permiso.id], 1)

        # Intentar eliminar debe fallar
        with pytest.raises(ConflictoDeNegocio):
            eliminar_permiso(db, permiso)