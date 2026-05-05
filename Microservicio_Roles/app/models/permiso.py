"""
app/models/permiso.py
=====================
Modelo ORM SQLAlchemy que representa la tabla `rol_permisos` en la base
de datos `db_roles` del microservicio ms-roles [ROL].

Tabla:
    rol_permisos

Responsabilidad:
    Catálogo centralizado de todos los permisos del sistema ERP universitario.
    Cada permiso representa una funcionalidad específica de un microservicio
    y posee un código único en todo el sistema (ej: 'PED_CREATE', 'CAL_READ').

    El responsable de ms-roles debe coordinar con los 18 microservicios
    restantes para registrar aquí todos los códigos de permiso del sistema.

Restricciones de negocio:
    - `codigo` es único en todo el sistema ERP (no solo en ms-roles).
    - `codigo` es INMUTABLE una vez creado; cambiarlo requeriría
      actualización sincronizada en los 18 microservicios que lo referencian.
    - `metodo_operacion` solo admite: 'consulta' | 'creacion' |
      'actualizacion' | 'eliminacion'.

Convención de nomenclatura del código:
    {PREFIJO_SERVICIO}_{ACCION}
    Ejemplos: ROL_CREATE, PED_DELETE, CAL_READ, USR_UPDATE

Referencias al documento maestro:
    ROL-RF-006 (Registrar permiso)
    ROL-RF-007 (Consultar permiso por ID)
    ROL-RF-008 (Listar permisos)
    ROL-RF-009 (Listar permisos por módulo)
    ROL-RF-010 (Actualizar permiso)
    ROL-RF-011 (Eliminar permiso)
"""

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin


class Permiso(Base, TimestampMixin):
    """
    Representa un permiso del catálogo global del sistema ERP universitario.

    Cada instancia corresponde a una funcionalidad específica de un
    microservicio que requiere control de acceso. Los permisos se asignan
    a roles mediante la tabla de asociación `rol_asignaciones_rol_permiso`.

    Attributes:
        id                     (int): Identificador interno autoincremental.
        codigo                 (str): Código único del permiso en todo el sistema.
                                      Convención: {PREFIJO}_{ACCION}.
                                      Inmutable tras su creación.
        nombre                 (str): Nombre legible del permiso.
                                      Ejemplo: 'Crear pedido'.
        descripcion            (str): Descripción detallada de la funcionalidad
                                      que protege este permiso. Puede ser nulo.
        modulo                 (str): Módulo funcional al que pertenece.
                                      Ejemplo: 'Logística y Proveedores'.
        microservicio_origen   (str): Microservicio propietario del permiso.
                                      Ejemplo: 'ms-pedidos'.
        funcionalidad_asociada (str): Descripción de la funcionalidad específica.
        metodo_operacion       (str): Tipo de operación. Valores permitidos:
                                      'consulta' | 'creacion' |
                                      'actualizacion' | 'eliminacion'.
        created_at  (datetime):       Heredado de TimestampMixin.
        updated_at  (datetime):       Heredado de TimestampMixin.
    """

    __tablename__ = "rol_permisos"

    id                     = Column(Integer,      primary_key=True, autoincrement=True)
    codigo                 = Column(String(60),   nullable=False, unique=True)
    nombre                 = Column(String(150),  nullable=False)
    descripcion            = Column(Text,         nullable=True)
    modulo                 = Column(String(80),   nullable=False)
    microservicio_origen   = Column(String(60),   nullable=False)
    funcionalidad_asociada = Column(String(150),  nullable=False)
    metodo_operacion       = Column(String(20),   nullable=False)

    # ── Relaciones ────────────────────────────────────────────────────────────

    asignaciones_roles = relationship(
        "AsignacionRolPermiso",
        back_populates="permiso",
        doc="Lista de roles a los que está asignado este permiso."
    )

    @property
    def operacion(self) -> str:
        """Devuelve el código de operación público asociado al permiso."""
        if self.metodo_operacion == "consulta":
            return "READ"
        if self.metodo_operacion == "creacion":
            return "CREATE"
        if self.metodo_operacion == "actualizacion":
            return "UPDATE"
        if self.metodo_operacion == "eliminacion":
            return "DELETE"
        return self.metodo_operacion.upper()

    def __repr__(self) -> str:
        """Representación legible del objeto para depuración."""
        return f"<Permiso id={self.id} codigo={self.codigo}>"