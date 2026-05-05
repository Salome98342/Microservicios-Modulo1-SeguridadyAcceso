"""
app/models/token_aplicacion.py
================================
Modelo ORM SQLAlchemy que representa la tabla
`rol_tokens_aplicacion` en la base de datos `db_roles`.

Tabla:
    rol_tokens_aplicacion

Responsabilidad:
    Almacena los tokens de aplicación cifrados con AES-256 que identifican
    a ms-roles ante los demás microservicios del sistema, y los tokens de
    los demás servicios que ms-roles debe validar al recibir peticiones
    inter-servicio (ROL-RT-002).

Política de tokens de aplicación (del documento maestro § 6.3):
    - Los tokens se almacenan SIEMPRE cifrados con AES-256.
    - Nunca deben aparecer en texto plano en logs, respuestas ni configs.
    - No tienen fecha de expiración.
    - Solo se actualizan manualmente por un administrador.
    - El campo `estado` permite desactivarlos sin eliminarlos.

Tokens semilla precargados (ROL-RF-018):
    - 'ms-roles':          token propio del servicio.
    - 'ms-autenticacion':  token para la relación de confianza mutua
                           (bootstrap de seguridad).

Referencias externas (sin FK real):
    actualizado_por_usuario_id → ms-usuarios [USR] (administrador)

Referencias al documento maestro:
    ROL-RT-002 (Validación de token de aplicación entre servicios)
    ROL-RF-018 (Carga inicial de datos semilla)
"""

from sqlalchemy import Column, Integer, String, Text
from app.db.base import Base, TimestampMixin


class TokenAplicacion(Base, TimestampMixin):
    """
    Token de aplicación cifrado AES-256 para comunicación inter-servicio.

    Cada registro representa la credencial de un microservicio del sistema.
    ms-roles valida el token recibido en la cabecera `Authorization` de
    las peticiones inter-servicio consultando esta tabla (ROL-RT-002).

    Attributes:
        id                         (int): Identificador interno autoincremental.
        nombre_servicio            (str): Nombre único del microservicio al que
                                          identifica el token.
                                          Ejemplo: 'ms-roles', 'ms-autenticacion'.
        token_cifrado              (str): Valor del token almacenado con cifrado
                                          AES-256. NUNCA en texto plano.
        descripcion                (str): Descripción del propósito del token.
                                          Puede ser nulo.
        estado                     (str): Estado del token.
                                          Valores: 'activo' (defecto) | 'inactivo'.
        actualizado_por_usuario_id (int): Referencia externa al administrador que
                                          realizó la última actualización manual
                                          del token (ms-usuarios [USR]).
                                          Puede ser nulo (bootstrap inicial).
        created_at  (datetime):           Heredado de TimestampMixin.
        updated_at  (datetime):           Heredado de TimestampMixin.
    """

    __tablename__ = "rol_tokens_aplicacion"

    id                         = Column(Integer,     primary_key=True, autoincrement=True)
    nombre_servicio            = Column(String(60),  nullable=False, unique=True)
    token_cifrado              = Column(Text,         nullable=False)
    descripcion                = Column(Text,         nullable=True)
    estado                     = Column(String(10),   nullable=False, default="activo")
    actualizado_por_usuario_id = Column(Integer,      nullable=True)