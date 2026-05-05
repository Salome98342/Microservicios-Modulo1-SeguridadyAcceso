# Guía de Desarrollo: ms-usuarios [USR]
## Guía Completa de Implementación

| Campo | Detalle |
|-------|---------|
| **Microservicio** | ms-usuarios [USR] |
| **Módulo** | Módulo 1 — Seguridad y Acceso |
| **Lenguaje** | Python |
| **Framework** | FastAPI |
| **Base de datos** | PostgreSQL |
| **Cifrado contraseñas** | bcrypt (cost ≥ 12) |
| **Cifrado datos** | AES-256 |
| **Documentación** | Swagger UI (`/docs`) |

---

## Tabla de Contenido

1. [Estructura del proyecto](#1-estructura-del-proyecto)
2. [Variables de entorno](#2-variables-de-entorno)
3. [Configuración — config.py](#3-configuración--configpy)
4. [Conexión a base de datos — database.py](#4-conexión-a-base-de-datos--databasepy)
5. [Modelos Pydantic — models/](#5-modelos-pydantic--models)
6. [Repositorio — repository/](#6-repositorio--repository)
7. [Servicios — services/](#7-servicios--services)
8. [Utilidades — utils/](#8-utilidades--utils)
9. [Rutas — routes/](#9-rutas--routes)
10. [Punto de entrada — main.py](#10-punto-de-entrada--mainpy)
11. [Flujo completo de una petición](#11-flujo-completo-de-una-petición)
12. [Tabla de endpoints y permisos](#12-tabla-de-endpoints-y-permisos)

---

## 1. Estructura del proyecto

```
ms-usuarios/
├── main.py
├── config.py
├── database.py
├── .env
├── requirements.txt
│
├── models/
│   ├── __init__.py
│   ├── usuario.py
│   ├── perfil.py
│   ├── historial_estado.py
│   ├── preferencias_notificacion.py
│   ├── tipo_documento.py
│   └── response.py
│
├── repository/
│   ├── __init__.py
│   ├── usuario_repository.py
│   ├── perfil_repository.py
│   ├── historial_repository.py
│   ├── preferencias_repository.py
│   └── tipo_documento_repository.py
│
├── services/
│   ├── __init__.py
│   ├── usuario_service.py
│   ├── perfil_service.py
│   ├── historial_service.py
│   ├── preferencias_service.py
│   └── tipo_documento_service.py
│
├── routes/
│   ├── __init__.py
│   ├── usuarios.py
│   ├── perfiles.py
│   ├── historial.py
│   ├── preferencias.py
│   └── tipos_documento.py
│
└── utils/
    ├── __init__.py
    ├── request_id.py
    ├── crypto.py
    ├── audit.py
    └── inter_service.py
```

### Regla de capas

```
routes/  →  services/  →  repository/  →  PostgreSQL
               ↓
            utils/  →  Microservicios externos (AUTH, ROL, NOT, AUD)
```

- `routes/` solo conoce `services/` y `utils/`. Nunca toca el repositorio directamente.
- `services/` contiene la lógica de negocio. No importa FastAPI ni lanza `HTTPException`. Retorna tuplas `(resultado, error)`.
- `repository/` ejecuta SQL puro. No contiene lógica de negocio.
- `utils/` agrupa funciones transversales (Request ID, cifrado, auditoría, comunicación inter-servicio).

---

## 2. Variables de entorno

Crear el archivo `.env` en la raíz del proyecto. **Nunca subir a control de versiones.**

```env
# ── Base de datos ─────────────────────────────────────────────
DB_HOST=localhost
DB_PORT=5432
DB_NAME=db_usuarios
DB_USER=postgres
DB_PASSWORD=password_seguro

# ── Cifrado AES-256 ───────────────────────────────────────────
# Clave de 32 bytes en hexadecimal (64 caracteres).
# Generar con: python -c "import secrets; print(secrets.token_hex(32))"
AES_SECRET_KEY=0000000000000000000000000000000000000000000000000000000000000000

# ── bcrypt ────────────────────────────────────────────────────
BCRYPT_ROUNDS=12

# ── Token propio de ms-usuarios ───────────────────────────────
USR_APP_TOKEN=token_de_ms_usuarios

# ── Tokens de microservicios externos ─────────────────────────
AUTH_APP_TOKEN=token_de_ms_autenticacion
ROL_APP_TOKEN=token_de_ms_roles
NOT_APP_TOKEN=token_de_ms_notificaciones
AUD_APP_TOKEN=token_de_ms_auditoria

# ── URLs de microservicios ────────────────────────────────────
AUTH_SERVICE_URL=http://ms-autenticacion:8001
ROL_SERVICE_URL=http://ms-roles:8002
NOT_SERVICE_URL=http://ms-notificaciones:8003
AUD_SERVICE_URL=http://ms-auditoria:8004

# ── Timeouts en segundos ──────────────────────────────────────
TIMEOUT_AUTH=3
TIMEOUT_ROL=3
TIMEOUT_NOT=1
TIMEOUT_AUD=0.5
```

---

## 3. Configuración — config.py

```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# ── Aplicación ────────────────────────────────────────────────
APP_TITULO      = "ms-usuarios [USR]"
APP_DESCRIPCION = "Microservicio de gestión de usuarios — Módulo 1: Seguridad y Acceso"
APP_VERSION     = "1.0.0"
APP_PREFIX      = "/api/v1"

# ── Base de datos ─────────────────────────────────────────────
DB_HOST     = os.getenv("DB_HOST",     "localhost")
DB_PORT     = os.getenv("DB_PORT",     "5432")
DB_NAME     = os.getenv("DB_NAME",     "db_usuarios")
DB_USER     = os.getenv("DB_USER",     "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# ── Cifrado ───────────────────────────────────────────────────
# Clave AES-256: 32 bytes almacenados como 64 hex chars
AES_SECRET_KEY = os.getenv("AES_SECRET_KEY", "")
BCRYPT_ROUNDS  = int(os.getenv("BCRYPT_ROUNDS", "12"))

# ── Tokens de aplicación ──────────────────────────────────────
USR_APP_TOKEN  = os.getenv("USR_APP_TOKEN",  "")
AUTH_APP_TOKEN = os.getenv("AUTH_APP_TOKEN", "")
ROL_APP_TOKEN  = os.getenv("ROL_APP_TOKEN",  "")
NOT_APP_TOKEN  = os.getenv("NOT_APP_TOKEN",  "")
AUD_APP_TOKEN  = os.getenv("AUD_APP_TOKEN",  "")

# ── URLs de servicios ─────────────────────────────────────────
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://ms-autenticacion:8001")
ROL_SERVICE_URL  = os.getenv("ROL_SERVICE_URL",  "http://ms-roles:8002")
NOT_SERVICE_URL  = os.getenv("NOT_SERVICE_URL",  "http://ms-notificaciones:8003")
AUD_SERVICE_URL  = os.getenv("AUD_SERVICE_URL",  "http://ms-auditoria:8004")

# ── Timeouts ──────────────────────────────────────────────────
TIMEOUT_AUTH = float(os.getenv("TIMEOUT_AUTH", "3"))
TIMEOUT_ROL  = float(os.getenv("TIMEOUT_ROL",  "3"))
TIMEOUT_NOT  = float(os.getenv("TIMEOUT_NOT",  "1"))
TIMEOUT_AUD  = float(os.getenv("TIMEOUT_AUD",  "0.5"))

# ── Paginación ────────────────────────────────────────────────
PAGINA_DEFAULT           = 1
ITEMS_POR_PAGINA_DEFAULT = 10
ITEMS_POR_PAGINA_MAX     = 100
```

---

## 4. Conexión a base de datos — database.py

Los documentos especifican **PostgreSQL** como motor y **Python** como lenguaje. La conexión se hace con el driver estándar para Python + PostgreSQL.

```python
# database.py
import psycopg2
import psycopg2.extras
from config import DATABASE_URL


def get_connection():
    """Abre y retorna una conexión a db_usuarios con autocommit=False."""
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = False
    return conn


def get_cursor(conn):
    """Cursor que retorna filas como diccionarios (RealDictCursor)."""
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
```

**Dependencia a instalar:**

```
psycopg2-binary
```

---

## 5. Modelos Pydantic — models/

### models/response.py — Estructura estándar (USR-RF-005)

Todas las respuestas siguen esta estructura:
`{ request_id, success, data, message, timestamp }`

```python
# models/response.py
from pydantic import BaseModel
from typing import Any, Optional
from datetime import datetime, timezone


class RespuestaEstandar(BaseModel):
    """
    Estructura uniforme para todas las respuestas del microservicio.
    Implementa USR-RF-005.
    """
    request_id: str
    success:    bool
    data:       Optional[Any] = None
    message:    str
    timestamp:  str

    @classmethod
    def ok(cls, request_id: str, data: Any, message: str) -> "RespuestaEstandar":
        return cls(
            request_id=request_id,
            success=True,
            data=data,
            message=message,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    @classmethod
    def error(cls, request_id: str, message: str) -> "RespuestaEstandar":
        return cls(
            request_id=request_id,
            success=False,
            data=None,
            message=message,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
```

### models/usuario.py

```python
# models/usuario.py
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime


class UsuarioCrear(BaseModel):
    """Datos para crear un usuario (USR-RF-006)."""
    username:           str
    email:              EmailStr
    password_encrypted: str   # Contraseña cifrada AES-256 + Base64 desde el cliente
    rol_id:             int

    @field_validator("username")
    @classmethod
    def username_valido(cls, v: str) -> str:
        if len(v.strip()) < 3:
            raise ValueError("El username debe tener al menos 3 caracteres")
        return v.strip()


class UsuarioActualizar(BaseModel):
    """Campos actualizables (USR-RF-010). Todos opcionales."""
    username: Optional[str]      = None
    email:    Optional[EmailStr] = None
    rol_id:   Optional[int]      = None

    @field_validator("username")
    @classmethod
    def username_valido(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v.strip()) < 3:
            raise ValueError("El username debe tener al menos 3 caracteres")
        return v.strip() if v else v


class CambiarPassword(BaseModel):
    """Cambio de contraseña autenticado (USR-RF-022)."""
    password_actual_encrypted: str
    password_nueva_encrypted:  str


class CambiarEstadoBody(BaseModel):
    """Cuerpo para cambio de estado o desactivación."""
    estado_nuevo: Optional[str] = None
    motivo:       str


class UsuarioRespuesta(BaseModel):
    """Datos de usuario expuestos al cliente. Sin password_hash."""
    id:         int
    username:   str
    email:      str
    estado:     str
    rol_id:     int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UsuarioConHash(UsuarioRespuesta):
    """
    Incluye password_hash.
    SOLO para uso interno de ms-autenticacion [AUTH].
    Nunca retornar en endpoints públicos.
    """
    password_hash: str


class ResultadoPaginado(BaseModel):
    resultados:       list[UsuarioRespuesta]
    total_registros:  int
    total_paginas:    int
    pagina_actual:    int
    items_por_pagina: int
```

### models/perfil.py

```python
# models/perfil.py
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import date, datetime
from enum import Enum


class GeneroEnum(str, Enum):
    masculino         = "masculino"
    femenino          = "femenino"
    otro              = "otro"
    prefiero_no_decir = "prefiero_no_decir"


class PerfilCrearActualizar(BaseModel):
    """Crear o actualizar perfil extendido (USR-RF-014)."""
    tipo_documento_id:            int
    numero_documento:             str
    primer_nombre:                str
    segundo_nombre:               Optional[str] = None
    primer_apellido:              str
    segundo_apellido:             Optional[str] = None
    fecha_nacimiento:             date
    genero:                       GeneroEnum
    direccion_residencia:         str
    ciudad:                       str
    departamento:                 str
    telefono_fijo:                Optional[str] = None
    telefono_movil:               str
    contacto_emergencia_nombre:   str
    contacto_emergencia_telefono: str
    biografia:                    Optional[str] = None

    @field_validator("fecha_nacimiento")
    @classmethod
    def validar_edad_minima(cls, v: date) -> date:
        from datetime import date as d
        hoy  = d.today()
        edad = hoy.year - v.year - ((hoy.month, hoy.day) < (v.month, v.day))
        if edad < 14:
            raise ValueError("Fecha de nacimiento inválida o usuario menor de 14 años")
        return v


class PerfilRespuesta(BaseModel):
    id:                           int
    usuario_id:                   int
    tipo_documento_id:            int
    tipo_documento_codigo:        Optional[str] = None
    tipo_documento_nombre:        Optional[str] = None
    numero_documento:             str
    primer_nombre:                str
    segundo_nombre:               Optional[str]
    primer_apellido:              str
    segundo_apellido:             Optional[str]
    fecha_nacimiento:             date
    genero:                       str
    direccion_residencia:         str
    ciudad:                       str
    departamento:                 str
    telefono_fijo:                Optional[str]
    telefono_movil:               str
    contacto_emergencia_nombre:   str
    contacto_emergencia_telefono: str
    biografia:                    Optional[str]
    created_at:                   datetime
    updated_at:                   datetime

    model_config = {"from_attributes": True}
```

### models/historial_estado.py

```python
# models/historial_estado.py
from pydantic import BaseModel
from datetime import datetime


class HistorialRespuesta(BaseModel):
    id:                     int
    usuario_id:             int
    estado_anterior:        str
    estado_nuevo:           str
    motivo:                 str
    usuario_modificador_id: int
    created_at:             datetime

    model_config = {"from_attributes": True}
```

### models/preferencias_notificacion.py

```python
# models/preferencias_notificacion.py
from pydantic import BaseModel, model_validator
from typing import Optional
from datetime import time, datetime


class PreferenciasActualizar(BaseModel):
    """Actualizar preferencias de notificación (USR-RF-019)."""
    notif_email:                Optional[bool] = None
    notif_sms:                  Optional[bool] = None
    notif_push:                 Optional[bool] = None
    canal_preferido:            Optional[str]  = None
    horario_no_molestar_inicio: Optional[time] = None
    horario_no_molestar_fin:    Optional[time] = None

    @model_validator(mode="after")
    def validar_horarios(self) -> "PreferenciasActualizar":
        inicio = self.horario_no_molestar_inicio
        fin    = self.horario_no_molestar_fin
        if (inicio is None) != (fin is None):
            raise ValueError("Debe proporcionar ambos horarios de no molestar o ninguno")
        if inicio and fin and inicio >= fin:
            raise ValueError("El horario de inicio debe ser anterior al horario de fin")
        return self


class PreferenciasRespuesta(BaseModel):
    id:                         int
    usuario_id:                 int
    notif_email:                bool
    notif_sms:                  bool
    notif_push:                 bool
    canal_preferido:            str
    horario_no_molestar_inicio: Optional[time]
    horario_no_molestar_fin:    Optional[time]
    created_at:                 datetime
    updated_at:                 datetime

    model_config = {"from_attributes": True}
```

### models/tipo_documento.py

```python
# models/tipo_documento.py
from pydantic import BaseModel
from typing import Optional


class TipoDocumentoRespuesta(BaseModel):
    id:          int
    codigo:      str
    nombre:      str
    descripcion: Optional[str]

    model_config = {"from_attributes": True}
```

---

## 6. Repositorio — repository/

Acceso a base de datos con SQL puro. Sin lógica de negocio. Todas las funciones abren y cierran su conexión, excepto las que participan en transacciones externas.

### repository/usuario_repository.py

```python
# repository/usuario_repository.py
from database import get_connection, get_cursor
from typing import Optional
import math


def obtener_por_id(usuario_id: int) -> Optional[dict]:
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute(
                "SELECT id, username, email, estado, rol_id, created_at, updated_at "
                "FROM usr_usuarios WHERE id = %s",
                (usuario_id,)
            )
            fila = cur.fetchone()
            return dict(fila) if fila else None
    finally:
        conn.close()


def obtener_por_id_con_hash(usuario_id: int) -> Optional[dict]:
    """Incluye password_hash. Solo para validación interna."""
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute("SELECT * FROM usr_usuarios WHERE id = %s", (usuario_id,))
            fila = cur.fetchone()
            return dict(fila) if fila else None
    finally:
        conn.close()


def obtener_por_email(email: str) -> Optional[dict]:
    """Sin password_hash. Para endpoints públicos."""
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute(
                "SELECT id, username, email, estado, rol_id, created_at, updated_at "
                "FROM usr_usuarios WHERE email = %s",
                (email,)
            )
            fila = cur.fetchone()
            return dict(fila) if fila else None
    finally:
        conn.close()


def obtener_por_email_con_hash(email: str) -> Optional[dict]:
    """Incluye password_hash. Exclusivo para ms-autenticacion."""
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute("SELECT * FROM usr_usuarios WHERE email = %s", (email,))
            fila = cur.fetchone()
            return dict(fila) if fila else None
    finally:
        conn.close()


def existe_username(username: str, excluir_id: Optional[int] = None) -> bool:
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            if excluir_id:
                cur.execute(
                    "SELECT 1 FROM usr_usuarios WHERE username = %s AND id <> %s",
                    (username, excluir_id)
                )
            else:
                cur.execute(
                    "SELECT 1 FROM usr_usuarios WHERE username = %s",
                    (username,)
                )
            return cur.fetchone() is not None
    finally:
        conn.close()


def existe_email(email: str, excluir_id: Optional[int] = None) -> bool:
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            if excluir_id:
                cur.execute(
                    "SELECT 1 FROM usr_usuarios WHERE email = %s AND id <> %s",
                    (email, excluir_id)
                )
            else:
                cur.execute(
                    "SELECT 1 FROM usr_usuarios WHERE email = %s",
                    (email,)
                )
            return cur.fetchone() is not None
    finally:
        conn.close()


def crear(username: str, email: str, password_hash: str, rol_id: int) -> dict:
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute(
                """
                INSERT INTO usr_usuarios (username, email, password_hash, estado, rol_id)
                VALUES (%s, %s, %s, 'activo', %s)
                RETURNING id, username, email, estado, rol_id, created_at, updated_at
                """,
                (username, email, password_hash, rol_id)
            )
            usuario = cur.fetchone()
        conn.commit()
        return dict(usuario)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def actualizar(usuario_id: int, campos: dict) -> Optional[dict]:
    """Actualización parcial: solo los campos presentes en el dict."""
    if not campos:
        return None
    set_clause = ", ".join(f"{k} = %s" for k in campos)
    valores    = list(campos.values()) + [usuario_id]
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute(
                f"""
                UPDATE usr_usuarios SET {set_clause}
                WHERE id = %s
                RETURNING id, username, email, estado, rol_id, created_at, updated_at
                """,
                valores
            )
            usuario = cur.fetchone()
        conn.commit()
        return dict(usuario) if usuario else None
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def actualizar_password(usuario_id: int, nuevo_hash: str) -> bool:
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute(
                "UPDATE usr_usuarios SET password_hash = %s WHERE id = %s",
                (nuevo_hash, usuario_id)
            )
            actualizado = cur.rowcount > 0
        conn.commit()
        return actualizado
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def cambiar_estado_transaccional(conn, usuario_id: int, nuevo_estado: str) -> Optional[dict]:
    """
    Actualiza el estado dentro de una transacción externa.
    La conexión es administrada por el llamador.
    """
    with get_cursor(conn) as cur:
        cur.execute(
            """
            UPDATE usr_usuarios SET estado = %s
            WHERE id = %s
            RETURNING id, username, email, estado, rol_id, created_at, updated_at
            """,
            (nuevo_estado, usuario_id)
        )
        fila = cur.fetchone()
        return dict(fila) if fila else None


def busqueda_avanzada(
    nombre:           Optional[str],
    numero_documento: Optional[str],
    email:            Optional[str],
    estado:           Optional[str],
    ciudad:           Optional[str],
    pagina:           int,
    items_por_pagina: int,
) -> tuple[list[dict], int]:
    """Retorna (lista_usuarios, total_registros). JOIN con usr_perfiles para filtros de perfil."""
    condiciones: list[str] = []
    valores:     list      = []

    if nombre:
        condiciones.append(
            "(p.primer_nombre ILIKE %s OR p.primer_apellido ILIKE %s)"
        )
        valores += [f"%{nombre}%", f"%{nombre}%"]
    if numero_documento:
        condiciones.append("p.numero_documento = %s")
        valores.append(numero_documento)
    if email:
        condiciones.append("u.email ILIKE %s")
        valores.append(f"%{email}%")
    if estado:
        condiciones.append("u.estado = %s")
        valores.append(estado)
    if ciudad:
        condiciones.append("p.ciudad ILIKE %s")
        valores.append(f"%{ciudad}%")

    where = ("WHERE " + " AND ".join(condiciones)) if condiciones else ""
    base  = f"FROM usr_usuarios u LEFT JOIN usr_perfiles p ON p.usuario_id = u.id {where}"
    offset = (pagina - 1) * items_por_pagina

    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute(f"SELECT COUNT(*) AS total {base}", valores)
            total = cur.fetchone()["total"]

            cur.execute(
                f"""
                SELECT u.id, u.username, u.email, u.estado, u.rol_id,
                       u.created_at, u.updated_at
                {base}
                ORDER BY u.created_at DESC
                LIMIT %s OFFSET %s
                """,
                valores + [items_por_pagina, offset]
            )
            filas = cur.fetchall()

        return [dict(f) for f in filas], total
    finally:
        conn.close()


def validar_existencia(usuario_id: int) -> Optional[dict]:
    """Endpoint ligero para ms-programas — solo id, estado, username."""
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute(
                "SELECT id, username, estado FROM usr_usuarios WHERE id = %s",
                (usuario_id,)
            )
            fila = cur.fetchone()
            return dict(fila) if fila else None
    finally:
        conn.close()


def estadisticas_por_estado() -> dict:
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute(
                "SELECT estado, COUNT(*) AS cantidad FROM usr_usuarios GROUP BY estado"
            )
            filas = cur.fetchall()
        resultado = {"activo": 0, "inactivo": 0, "suspendido": 0}
        for f in filas:
            resultado[f["estado"]] = int(f["cantidad"])
        total = sum(resultado.values())
        return {"total": total, "por_estado": resultado}
    finally:
        conn.close()


def listar_por_rol(
    rol_id: int,
    estado: Optional[str],
    pagina: int,
    items_por_pagina: int,
) -> tuple[list[dict], int]:
    condiciones = ["rol_id = %s"]
    valores: list = [rol_id]

    if estado and estado != "todos":
        condiciones.append("estado = %s")
        valores.append(estado)

    where  = "WHERE " + " AND ".join(condiciones)
    offset = (pagina - 1) * items_por_pagina

    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute(
                f"SELECT COUNT(*) AS total FROM usr_usuarios {where}",
                valores
            )
            total = cur.fetchone()["total"]

            cur.execute(
                f"""
                SELECT id, username, email, estado, rol_id, created_at, updated_at
                FROM usr_usuarios {where}
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
                """,
                valores + [items_por_pagina, offset]
            )
            filas = cur.fetchall()

        return [dict(f) for f in filas], total
    finally:
        conn.close()
```

### repository/historial_repository.py

```python
# repository/historial_repository.py
from database import get_connection, get_cursor
from typing import Optional


def registrar_cambio_transaccional(
    conn,
    usuario_id:             int,
    estado_anterior:        str,
    estado_nuevo:           str,
    motivo:                 str,
    usuario_modificador_id: int,
) -> dict:
    """
    Inserta en usr_historial_estados dentro de una transacción externa.
    La conexión es administrada por el llamador.
    """
    with get_cursor(conn) as cur:
        cur.execute(
            """
            INSERT INTO usr_historial_estados
                (usuario_id, estado_anterior, estado_nuevo, motivo, usuario_modificador_id)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING *
            """,
            (usuario_id, estado_anterior, estado_nuevo, motivo, usuario_modificador_id)
        )
        return dict(cur.fetchone())


def listar_por_usuario(usuario_id: int) -> list[dict]:
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute(
                """
                SELECT * FROM usr_historial_estados
                WHERE usuario_id = %s
                ORDER BY created_at DESC
                """,
                (usuario_id,)
            )
            return [dict(f) for f in cur.fetchall()]
    finally:
        conn.close()
```

### repository/perfil_repository.py

```python
# repository/perfil_repository.py
from database import get_connection, get_cursor
from typing import Optional


def obtener_por_usuario_id(usuario_id: int) -> Optional[dict]:
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute(
                """
                SELECT p.*, t.codigo AS tipo_documento_codigo,
                            t.nombre AS tipo_documento_nombre
                FROM usr_perfiles p
                JOIN usr_tipos_documento t ON t.id = p.tipo_documento_id
                WHERE p.usuario_id = %s
                """,
                (usuario_id,)
            )
            fila = cur.fetchone()
            return dict(fila) if fila else None
    finally:
        conn.close()


def existe_numero_documento(
    numero_documento: str, excluir_usuario_id: Optional[int] = None
) -> bool:
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            if excluir_usuario_id:
                cur.execute(
                    "SELECT 1 FROM usr_perfiles "
                    "WHERE numero_documento = %s AND usuario_id <> %s",
                    (numero_documento, excluir_usuario_id)
                )
            else:
                cur.execute(
                    "SELECT 1 FROM usr_perfiles WHERE numero_documento = %s",
                    (numero_documento,)
                )
            return cur.fetchone() is not None
    finally:
        conn.close()


def crear_o_actualizar(usuario_id: int, datos: dict) -> dict:
    """Upsert: crea el perfil si no existe; lo actualiza si existe."""
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute(
                "SELECT id FROM usr_perfiles WHERE usuario_id = %s",
                (usuario_id,)
            )
            existente = cur.fetchone()

            if existente:
                set_clause = ", ".join(f"{k} = %s" for k in datos)
                valores    = list(datos.values()) + [usuario_id]
                cur.execute(
                    f"""
                    UPDATE usr_perfiles SET {set_clause}
                    WHERE usuario_id = %s RETURNING *
                    """,
                    valores
                )
            else:
                columnas     = ", ".join(["usuario_id"] + list(datos.keys()))
                placeholders = ", ".join(["%s"] * (1 + len(datos)))
                cur.execute(
                    f"""
                    INSERT INTO usr_perfiles ({columnas})
                    VALUES ({placeholders}) RETURNING *
                    """,
                    [usuario_id] + list(datos.values())
                )

            perfil = cur.fetchone()
        conn.commit()
        return dict(perfil)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
```

### repository/preferencias_repository.py

```python
# repository/preferencias_repository.py
from database import get_connection, get_cursor
from typing import Optional


def obtener_por_usuario_id(usuario_id: int) -> Optional[dict]:
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute(
                "SELECT * FROM usr_preferencias_notificacion WHERE usuario_id = %s",
                (usuario_id,)
            )
            fila = cur.fetchone()
            return dict(fila) if fila else None
    finally:
        conn.close()


def crear_o_actualizar(usuario_id: int, datos: dict) -> dict:
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute(
                "SELECT id FROM usr_preferencias_notificacion WHERE usuario_id = %s",
                (usuario_id,)
            )
            existente = cur.fetchone()

            if existente:
                set_clause = ", ".join(f"{k} = %s" for k in datos)
                cur.execute(
                    f"""
                    UPDATE usr_preferencias_notificacion SET {set_clause}
                    WHERE usuario_id = %s RETURNING *
                    """,
                    list(datos.values()) + [usuario_id]
                )
            else:
                columnas     = ", ".join(["usuario_id"] + list(datos.keys()))
                placeholders = ", ".join(["%s"] * (1 + len(datos)))
                cur.execute(
                    f"""
                    INSERT INTO usr_preferencias_notificacion ({columnas})
                    VALUES ({placeholders}) RETURNING *
                    """,
                    [usuario_id] + list(datos.values())
                )

            pref = cur.fetchone()
        conn.commit()
        return dict(pref)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
```

### repository/tipo_documento_repository.py

```python
# repository/tipo_documento_repository.py
from database import get_connection, get_cursor
from typing import Optional


def listar_activos() -> list[dict]:
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute(
                "SELECT id, codigo, nombre, descripcion "
                "FROM usr_tipos_documento WHERE activo = true ORDER BY nombre ASC"
            )
            return [dict(f) for f in cur.fetchall()]
    finally:
        conn.close()


def obtener_por_id(tipo_id: int) -> Optional[dict]:
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute(
                "SELECT id, codigo, nombre, descripcion, activo "
                "FROM usr_tipos_documento WHERE id = %s",
                (tipo_id,)
            )
            fila = cur.fetchone()
            return dict(fila) if fila else None
    finally:
        conn.close()
```

---

## 7. Servicios — services/

Contienen la lógica de negocio. No importan FastAPI. No lanzan `HTTPException`. Retornan `(resultado, error_string)` donde el string de error puede llevar prefijo de código HTTP: `"404:mensaje"`, `"400:mensaje"`, `"503:mensaje"`.

### services/usuario_service.py

```python
# services/usuario_service.py
import math
import re
from typing import Optional

import repository.usuario_repository as repo
from utils.crypto import descifrar_aes256, hashear_bcrypt, verificar_bcrypt
from utils.inter_service import validar_rol_externo
from config import ITEMS_POR_PAGINA_MAX

ESTADOS_VALIDOS = {"activo", "inactivo", "suspendido"}


def obtener_por_id(usuario_id: int) -> Optional[dict]:
    return repo.obtener_por_id(usuario_id)


def obtener_por_email_publico(email: str) -> Optional[dict]:
    return repo.obtener_por_email(email)


def obtener_por_email_con_hash(email: str) -> Optional[dict]:
    """Solo para ms-autenticacion."""
    return repo.obtener_por_email_con_hash(email)


def crear_usuario(
    username: str, email: str, password_encrypted: str, rol_id: int
) -> tuple[Optional[dict], Optional[str]]:
    """USR-RF-006. Retorna (usuario, error)."""
    if repo.existe_username(username):
        return None, "El nombre de usuario ya está registrado"
    if repo.existe_email(email):
        return None, "El correo electrónico ya está registrado"

    rol_valido, error_rol = validar_rol_externo(rol_id)
    if not rol_valido:
        return None, error_rol or "El rol especificado no es válido"

    try:
        password_plano = descifrar_aes256(password_encrypted)
    except Exception:
        return None, "Error al procesar la contraseña"

    password_hash = hashear_bcrypt(password_plano)
    usuario = repo.crear(username, email, password_hash, rol_id)
    return usuario, None


def actualizar_usuario(
    usuario_id: int,
    username:   Optional[str],
    email:      Optional[str],
    rol_id:     Optional[int],
) -> tuple[Optional[dict], Optional[str]]:
    """USR-RF-010."""
    if not any([username, email, rol_id]):
        return None, "Debe proporcionar al menos un campo a actualizar"

    if not repo.obtener_por_id(usuario_id):
        return None, "404:Usuario no encontrado"

    campos = {}

    if username:
        if repo.existe_username(username, excluir_id=usuario_id):
            return None, "El nombre de usuario ya está registrado"
        campos["username"] = username

    if email:
        if repo.existe_email(email, excluir_id=usuario_id):
            return None, "El correo electrónico ya está registrado"
        campos["email"] = email

    if rol_id:
        valido, error = validar_rol_externo(rol_id)
        if not valido:
            return None, error or "El rol especificado no es válido"
        campos["rol_id"] = rol_id

    usuario = repo.actualizar(usuario_id, campos)
    return usuario, None


def cambiar_password(
    usuario_id:                int,
    password_actual_encrypted: str,
    password_nueva_encrypted:  str,
) -> tuple[bool, Optional[str]]:
    """USR-RF-022."""
    usuario = repo.obtener_por_id_con_hash(usuario_id)
    if not usuario:
        return False, "404:Usuario no encontrado"

    try:
        actual_plano = descifrar_aes256(password_actual_encrypted)
        nueva_plano  = descifrar_aes256(password_nueva_encrypted)
    except Exception:
        return False, "Error al procesar las contraseñas"

    if not verificar_bcrypt(actual_plano, usuario["password_hash"]):
        return False, "401:Contraseña actual incorrecta"

    if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$", nueva_plano):
        return False, (
            "La nueva contraseña no cumple con las políticas de seguridad: "
            "mínimo 8 caracteres, al menos 1 mayúscula, 1 minúscula, 1 número"
        )

    repo.actualizar_password(usuario_id, hashear_bcrypt(nueva_plano))
    return True, None


def busqueda_avanzada(
    nombre, numero_documento, email, estado, ciudad, pagina, items_por_pagina
) -> dict:
    if items_por_pagina > ITEMS_POR_PAGINA_MAX:
        items_por_pagina = ITEMS_POR_PAGINA_MAX
    filas, total = repo.busqueda_avanzada(
        nombre, numero_documento, email, estado, ciudad, pagina, items_por_pagina
    )
    return {
        "resultados":       filas,
        "total_registros":  total,
        "total_paginas":    math.ceil(total / items_por_pagina) if total else 0,
        "pagina_actual":    pagina,
        "items_por_pagina": items_por_pagina,
    }


def validar_existencia(usuario_id: int) -> dict:
    """USR-RF-021. Para ms-programas."""
    fila = repo.validar_existencia(usuario_id)
    if not fila:
        return {"existe": False}
    return {
        "existe":   True,
        "estado":   fila["estado"],
        "user_id":  fila["id"],
        "username": fila["username"],
    }


def obtener_estadisticas() -> dict:
    """USR-RF-024."""
    return repo.estadisticas_por_estado()


def listar_por_rol(rol_id, estado, pagina, items_por_pagina) -> dict:
    filas, total = repo.listar_por_rol(rol_id, estado, pagina, items_por_pagina)
    return {
        "resultados":       filas,
        "total_registros":  total,
        "total_paginas":    math.ceil(total / items_por_pagina) if total else 0,
        "pagina_actual":    pagina,
        "items_por_pagina": items_por_pagina,
    }
```

### services/historial_service.py

```python
# services/historial_service.py
from typing import Optional

import repository.usuario_repository  as usuario_repo
import repository.historial_repository as historial_repo
from database import get_connection

ESTADOS_VALIDOS = {"activo", "inactivo", "suspendido"}


def cambiar_estado(
    usuario_id:             int,
    estado_nuevo:           str,
    motivo:                 str,
    usuario_modificador_id: int,
) -> tuple[Optional[dict], Optional[str]]:
    """
    Cambia el estado y registra el historial en una sola transacción atómica.
    USR-RF-015. Retorna (usuario_actualizado, error).
    """
    if estado_nuevo not in ESTADOS_VALIDOS:
        return None, f"Estado inválido. Valores permitidos: {', '.join(ESTADOS_VALIDOS)}"
    if not motivo or not motivo.strip():
        return None, "Debe proporcionar un motivo para el cambio de estado"

    usuario = usuario_repo.obtener_por_id(usuario_id)
    if not usuario:
        return None, "404:Usuario no encontrado"
    if usuario["estado"] == estado_nuevo:
        return None, "El usuario ya se encuentra en el estado especificado"

    estado_anterior = usuario["estado"]

    # Transacción atómica: UPDATE de estado + INSERT de historial
    conn = get_connection()
    try:
        usuario_actualizado = usuario_repo.cambiar_estado_transaccional(
            conn, usuario_id, estado_nuevo
        )
        historial_repo.registrar_cambio_transaccional(
            conn, usuario_id, estado_anterior, estado_nuevo,
            motivo, usuario_modificador_id
        )
        conn.commit()
        return usuario_actualizado, None
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def listar_historial(usuario_id: int) -> list[dict]:
    """USR-RF-016."""
    if not usuario_repo.obtener_por_id(usuario_id):
        return []
    return historial_repo.listar_por_usuario(usuario_id)
```

### services/perfil_service.py

```python
# services/perfil_service.py
from typing import Optional

import repository.perfil_repository         as repo
import repository.usuario_repository        as usuario_repo
import repository.tipo_documento_repository as tipo_repo


def obtener_perfil(usuario_id: int) -> tuple[Optional[dict], Optional[str]]:
    """USR-RF-013."""
    if not usuario_repo.obtener_por_id(usuario_id):
        return None, "404:Usuario no encontrado"
    perfil = repo.obtener_por_usuario_id(usuario_id)
    if not perfil:
        return None, "404:Perfil no encontrado para el usuario especificado"
    return perfil, None


def crear_o_actualizar_perfil(
    usuario_id: int, datos: dict
) -> tuple[Optional[dict], Optional[str], bool]:
    """USR-RF-014. Retorna (perfil, error, fue_creado)."""
    if not usuario_repo.obtener_por_id(usuario_id):
        return None, "404:Usuario no encontrado", False

    tipo = tipo_repo.obtener_por_id(datos["tipo_documento_id"])
    if not tipo or not tipo["activo"]:
        return None, "Tipo de documento inválido", False

    if repo.existe_numero_documento(
        datos["numero_documento"], excluir_usuario_id=usuario_id
    ):
        return None, "El número de documento ya está registrado", False

    existia = repo.obtener_por_usuario_id(usuario_id) is not None
    perfil  = repo.crear_o_actualizar(usuario_id, datos)
    return perfil, None, not existia
```

### services/preferencias_service.py

```python
# services/preferencias_service.py
from typing import Optional

import repository.preferencias_repository as repo
import repository.usuario_repository      as usuario_repo

DEFAULTS = {
    "notif_email":                True,
    "notif_sms":                  False,
    "notif_push":                 True,
    "canal_preferido":            "email",
    "horario_no_molestar_inicio": None,
    "horario_no_molestar_fin":    None,
}


def obtener_preferencias(usuario_id: int) -> tuple[Optional[dict], Optional[str]]:
    """USR-RF-018. Retorna defaults si no hay configuración personalizada."""
    if not usuario_repo.obtener_por_id(usuario_id):
        return None, "404:Usuario no encontrado"
    pref = repo.obtener_por_usuario_id(usuario_id)
    if not pref:
        return {"usuario_id": usuario_id, **DEFAULTS}, None
    return dict(pref), None


def crear_o_actualizar_preferencias(
    usuario_id: int, datos: dict
) -> tuple[Optional[dict], Optional[str]]:
    """USR-RF-019."""
    if not usuario_repo.obtener_por_id(usuario_id):
        return None, "404:Usuario no encontrado"
    pref = repo.crear_o_actualizar(usuario_id, datos)
    return pref, None
```

### services/tipo_documento_service.py

```python
# services/tipo_documento_service.py
import repository.tipo_documento_repository as repo


def listar_activos() -> list[dict]:
    """USR-RF-017."""
    return repo.listar_activos()
```

---

## 8. Utilidades — utils/

### utils/request_id.py — USR-RF-003

```python
# utils/request_id.py
import time
import random
import string
from typing import Optional


def generar_request_id() -> str:
    """
    Genera un Request ID con el formato: USR-{timestamp_unix}-{8_chars_alfanuméricos}
    Ejemplo: USR-1709856234-a3f8b2c1
    """
    timestamp = int(time.time())
    aleatorio = "".join(
        random.choices(string.ascii_lowercase + string.digits, k=8)
    )
    return f"USR-{timestamp}-{aleatorio}"


def obtener_o_generar(x_request_id: Optional[str]) -> str:
    """
    Si la petición trae un Request ID (de otro microservicio), lo reutiliza.
    Si no, genera uno nuevo. Implementa USR-RF-003.
    """
    if x_request_id and x_request_id.strip():
        return x_request_id.strip()
    return generar_request_id()
```

### utils/crypto.py — AES-256 y bcrypt

Los documentos especifican: AES-256 con codificación Base64 y bcrypt con factor de costo ≥ 12. La implementación concreta depende de las librerías disponibles en Python. A continuación se muestra la interfaz y un ejemplo de implementación.

```python
# utils/crypto.py
"""
Cifrado AES-256 y hashing bcrypt.
Según los documentos, las contraseñas se transmiten cifradas con AES-256
en Base64 desde el cliente; el servidor las descifra y genera hash bcrypt.
Los tokens de aplicación siguen la misma política.
"""
import base64
import bcrypt
from config import AES_SECRET_KEY, BCRYPT_ROUNDS


def _obtener_clave_bytes() -> bytes:
    """
    La clave AES-256 se almacena como 64 caracteres hexadecimales en .env
    (32 bytes). Esta función la convierte a bytes.
    """
    return bytes.fromhex(AES_SECRET_KEY)


def descifrar_aes256(texto_cifrado_b64: str) -> str:
    """
    Descifra un texto cifrado con AES-256 recibido en Base64.
    Formato esperado: IV (16 bytes) + datos cifrados, todo codificado en Base64.
    """
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import unpad

    datos   = base64.b64decode(texto_cifrado_b64)
    iv      = datos[:16]
    cifrado = datos[16:]
    cipher  = AES.new(_obtener_clave_bytes(), AES.MODE_CBC, iv)
    plano   = unpad(cipher.decrypt(cifrado), AES.block_size)
    return plano.decode("utf-8")


def cifrar_aes256(texto_plano: str) -> str:
    """
    Cifra texto plano con AES-256-CBC.
    Retorna IV + datos cifrados codificado en Base64.
    """
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad
    from Crypto.Random import get_random_bytes

    iv      = get_random_bytes(16)
    cipher  = AES.new(_obtener_clave_bytes(), AES.MODE_CBC, iv)
    cifrado = cipher.encrypt(pad(texto_plano.encode("utf-8"), AES.block_size))
    return base64.b64encode(iv + cifrado).decode("utf-8")


def hashear_bcrypt(password_plano: str) -> str:
    """Hash bcrypt con factor de costo mínimo 12 (según USR-RF-006 y Sección 6.4)."""
    return bcrypt.hashpw(
        password_plano.encode("utf-8"),
        bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    ).decode("utf-8")


def verificar_bcrypt(password_plano: str, hash_almacenado: str) -> bool:
    return bcrypt.checkpw(
        password_plano.encode("utf-8"),
        hash_almacenado.encode("utf-8")
    )
```

### utils/audit.py — USR-RF-004

```python
# utils/audit.py
"""
Envío asíncrono (fire-and-forget) de logs de auditoría a ms-auditoria [AUD].
Si falla, escribe en archivo de respaldo local.
Implementa USR-RF-004 y la regla transversal 6.6.
"""
import json
import threading
import datetime
import os
from typing import Optional
from urllib import request as urllib_request
from urllib.error import URLError

from config import AUD_SERVICE_URL, AUD_APP_TOKEN, TIMEOUT_AUD

BACKUP_DIR  = "/var/log/ms-usuarios/audit-backup"


def _guardar_respaldo(log: dict) -> None:
    """Escribe el log en un archivo JSONL local si ms-auditoria no está disponible."""
    try:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        fecha   = datetime.date.today().isoformat()
        archivo = os.path.join(BACKUP_DIR, f"audit-{fecha}.jsonl")
        with open(archivo, "a", encoding="utf-8") as f:
            f.write(json.dumps(log, default=str) + "\n")
    except Exception as e:
        print(f"[AUDIT BACKUP ERROR] {e}")


def _enviar_log(log: dict) -> None:
    """Envía el log JSON a ms-auditoria. En caso de error, lo guarda en respaldo."""
    try:
        payload = json.dumps(log, default=str).encode("utf-8")
        req = urllib_request.Request(
            url=f"{AUD_SERVICE_URL}/api/v1/audit/logs",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "X-App-Token":  f"AES256:{AUD_APP_TOKEN}",
                "X-Request-ID": log.get("request_id", ""),
            },
            method="POST",
        )
        urllib_request.urlopen(req, timeout=TIMEOUT_AUD)
    except Exception:
        _guardar_respaldo(log)


def registrar_log_async(
    request_id:    str,
    funcionalidad: str,
    metodo:        str,
    endpoint:      str,
    codigo:        int,
    usuario_id:    Optional[int],
    detalle:       str,
) -> None:
    """
    Construye el log JSON y lo envía en un thread separado (no bloquea).
    Implementa USR-RF-004.
    """
    log = {
        "timestamp":        datetime.datetime.utcnow().isoformat() + "Z",
        "request_id":       request_id,
        "microservicio":    "ms-usuarios",
        "funcionalidad":    funcionalidad,
        "metodo":           metodo,
        "endpoint":         endpoint,
        "codigo_respuesta": codigo,
        "usuario_id":       usuario_id,
        "detalle":          detalle,
    }
    hilo = threading.Thread(target=_enviar_log, args=(log,), daemon=True)
    hilo.start()
```

### utils/inter_service.py — Comunicación entre microservicios

```python
# utils/inter_service.py
"""
Comunicación con ms-autenticacion [AUTH], ms-roles [ROL] y ms-notificaciones [NOT].
Implementa las reglas transversales USR-RF-001, USR-RF-002 y las notificaciones
descritas en la Sección 3.3 del diseño de integración.
"""
import json
import threading
from typing import Optional, Tuple
from urllib import request as urllib_request
from urllib.error import URLError, HTTPError

from fastapi import HTTPException, status

from config import (
    AUTH_SERVICE_URL, ROL_SERVICE_URL, NOT_SERVICE_URL,
    AUTH_APP_TOKEN, ROL_APP_TOKEN, NOT_APP_TOKEN, USR_APP_TOKEN,
    TIMEOUT_AUTH, TIMEOUT_ROL, TIMEOUT_NOT,
)
from utils.crypto import descifrar_aes256, cifrar_aes256


def _cabeceras(app_token: str, request_id: str = "") -> dict:
    """Construye las cabeceras estándar para llamadas inter-servicio."""
    return {
        "Content-Type": "application/json",
        "X-App-Token":  f"AES256:{cifrar_aes256(app_token)}",
        "X-Request-ID": request_id,
    }


def _post_json(url: str, payload: dict, cabeceras: dict, timeout: float) -> dict:
    """Realiza una petición POST y retorna el JSON de respuesta."""
    data = json.dumps(payload).encode("utf-8")
    req  = urllib_request.Request(url=url, data=data, headers=cabeceras, method="POST")
    with urllib_request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _get_json(url: str, cabeceras: dict, timeout: float) -> dict:
    """Realiza una petición GET y retorna el JSON de respuesta."""
    req = urllib_request.Request(url=url, headers=cabeceras, method="GET")
    with urllib_request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


# ── USR-RF-001: Validación de sesión ──────────────────────────────────────────

def validar_sesion_activa(authorization: str, request_id: str) -> dict:
    """
    Consulta ms-autenticacion para validar el token de sesión.
    Lanza HTTPException si no es válido.
    Retorna el payload con user_id y rol_id.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token de sesión no proporcionado"
        )

    token = authorization.split(" ", 1)[1]
    try:
        respuesta = _post_json(
            url=f"{AUTH_SERVICE_URL}/api/v1/auth/validate-session",
            payload={"token": token, "request_id": request_id},
            cabeceras={
                **_cabeceras(AUTH_APP_TOKEN, request_id),
                "Authorization": authorization,
            },
            timeout=TIMEOUT_AUTH,
        )
    except HTTPError as e:
        if e.code == 401:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Sesión no válida o expirada"
            )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio de autenticación no disponible"
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio de autenticación no disponible"
        )

    datos = respuesta.get("data", {})
    if not datos.get("valid"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión no válida o expirada"
        )
    return {"user_id": datos["user_id"], "rol_id": datos["rol_id"]}


# ── USR-RF-002: Validación de permisos ────────────────────────────────────────

def validar_permiso(rol_id: int, codigo_permiso: str, request_id: str) -> None:
    """
    Consulta ms-roles para verificar que el rol tiene el permiso.
    Lanza HTTPException 403 si no tiene autorización.
    """
    try:
        respuesta = _post_json(
            url=f"{ROL_SERVICE_URL}/api/v1/roles/validate-permission",
            payload={
                "rol_id":          rol_id,
                "permission_code": codigo_permiso,
                "request_id":      request_id,
            },
            cabeceras=_cabeceras(ROL_APP_TOKEN, request_id),
            timeout=TIMEOUT_ROL,
        )
    except HTTPError as e:
        if e.code == 403:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para ejecutar esta operación"
            )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio de roles no disponible"
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio de roles no disponible"
        )

    if not respuesta.get("data", {}).get("authorized"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ejecutar esta operación"
        )


# ── Validar existencia de rol en ms-roles ─────────────────────────────────────

def validar_rol_externo(rol_id: int) -> Tuple[bool, Optional[str]]:
    """Verifica que el rol exista y esté activo en ms-roles. Retorna (válido, error)."""
    try:
        respuesta = _get_json(
            url=f"{ROL_SERVICE_URL}/api/v1/roles/{rol_id}/validate",
            cabeceras=_cabeceras(ROL_APP_TOKEN),
            timeout=TIMEOUT_ROL,
        )
    except HTTPError as e:
        if e.code == 404:
            return False, "El rol especificado no es válido"
        return False, "503:Servicio de roles no disponible"
    except Exception:
        return False, "503:Servicio de roles no disponible"

    datos = respuesta.get("data", {})
    if not datos.get("exists") or not datos.get("active"):
        return False, "El rol especificado no existe o está inactivo"
    return True, None


# ── Notificaciones asíncronas (fire-and-forget) ───────────────────────────────

def _enviar_notificacion(
    notification_type: str, user_id: int, data: dict, request_id: str
) -> None:
    try:
        _post_json(
            url=f"{NOT_SERVICE_URL}/api/v1/notifications/send",
            payload={
                "notification_type": notification_type,
                "user_id":           user_id,
                "data":              data,
                "request_id":        request_id,
            },
            cabeceras=_cabeceras(NOT_APP_TOKEN, request_id),
            timeout=TIMEOUT_NOT,
        )
    except Exception:
        pass  # No crítico — fire-and-forget


def notificar_async(
    notification_type: str, user_id: int, data: dict, request_id: str
) -> None:
    """Lanza la notificación en un thread separado. No bloquea la respuesta."""
    hilo = threading.Thread(
        target=_enviar_notificacion,
        args=(notification_type, user_id, data, request_id),
        daemon=True,
    )
    hilo.start()


# ── Validadores de token de aplicación ───────────────────────────────────────

def es_token_de(x_app_token: Optional[str], token_esperado: str) -> bool:
    """
    Verifica si el X-App-Token pertenece a un microservicio específico.
    El token llega cifrado con AES-256 y prefijo 'AES256:'.
    """
    if not x_app_token:
        return False
    try:
        valor     = x_app_token.replace("AES256:", "", 1)
        descifrado = descifrar_aes256(valor)
        return descifrado == token_esperado
    except Exception:
        return False


def es_token_autenticacion(x_app_token: Optional[str]) -> bool:
    return es_token_de(x_app_token, AUTH_APP_TOKEN)


def es_token_notificaciones(x_app_token: Optional[str]) -> bool:
    return es_token_de(x_app_token, NOT_APP_TOKEN)
```

---

## 9. Rutas — routes/

Los routers traducen los resultados de los servicios en respuestas HTTP. Aquí viven `HTTPException`, códigos de estado y las llamadas a las utilidades transversales.

**Patrón de extracción de código HTTP desde el string de error:**

```python
def _parsear_error(error: str) -> tuple[int, str]:
    """Extrae el código HTTP del prefijo '4XX:mensaje' si existe."""
    if error and len(error) > 3 and error[:3].isdigit() and error[3] == ":":
        return int(error[:3]), error[4:]
    return 400, error
```

### routes/usuarios.py

```python
# routes/usuarios.py
from fastapi import APIRouter, Header, HTTPException, status
from typing import Optional

from models.usuario  import (
    UsuarioCrear, UsuarioActualizar, CambiarPassword, CambiarEstadoBody,
    UsuarioRespuesta
)
from models.response import RespuestaEstandar
import services.usuario_service  as svc
import services.historial_service as hist_svc

from utils.request_id    import obtener_o_generar
from utils.audit         import registrar_log_async
from utils.inter_service import (
    validar_sesion_activa, validar_permiso,
    notificar_async, es_token_autenticacion,
)
from config import PAGINA_DEFAULT, ITEMS_POR_PAGINA_DEFAULT, ITEMS_POR_PAGINA_MAX

router = APIRouter(prefix="/users", tags=["Usuarios"])


def _parsear_error(error: str) -> tuple[int, str]:
    if error and len(error) > 3 and error[:3].isdigit() and error[3] == ":":
        return int(error[:3]), error[4:]
    return 400, error


# ── POST /users ───────────────────────────────────────────────────────────────
@router.post("", status_code=status.HTTP_201_CREATED, response_model=RespuestaEstandar)
async def crear_usuario(
    datos: UsuarioCrear,
    authorization: str = Header(..., alias="Authorization"),
    x_request_id:  Optional[str] = Header(None, alias="X-Request-ID"),
    x_app_token:   Optional[str] = Header(None, alias="X-App-Token"),
):
    """USR-RF-006: Crear nuevo usuario. Permiso requerido: USR_CREATE."""
    req_id = obtener_o_generar(x_request_id)
    sesion = validar_sesion_activa(authorization, req_id)   # USR-RF-001
    validar_permiso(sesion["rol_id"], "USR_CREATE", req_id) # USR-RF-002

    usuario, error = svc.crear_usuario(
        datos.username, str(datos.email), datos.password_encrypted, datos.rol_id
    )
    if error:
        codigo, msg = _parsear_error(error)
        registrar_log_async(req_id, "Crear usuario", "POST", "/api/v1/users",
                            codigo, sesion.get("user_id"), msg)
        raise HTTPException(status_code=codigo, detail=msg)

    notificar_async("user_welcome", usuario["id"],
                    {"username": usuario["username"], "email": usuario["email"]},
                    req_id)
    registrar_log_async(req_id, "Crear usuario", "POST", "/api/v1/users",
                        201, sesion.get("user_id"),
                        f"Usuario '{usuario['username']}' creado")

    return RespuestaEstandar.ok(
        req_id, UsuarioRespuesta(**usuario), "Usuario creado exitosamente"
    )


# ── GET /users (búsqueda avanzada) ────────────────────────────────────────────
@router.get("", response_model=RespuestaEstandar)
async def busqueda_avanzada(
    nombre:           Optional[str] = None,
    numero_documento: Optional[str] = None,
    email:            Optional[str] = None,
    estado:           Optional[str] = None,
    ciudad:           Optional[str] = None,
    pagina:           int = PAGINA_DEFAULT,
    items_por_pagina: int = ITEMS_POR_PAGINA_DEFAULT,
    authorization: str = Header(..., alias="Authorization"),
    x_request_id:  Optional[str] = Header(None, alias="X-Request-ID"),
):
    """USR-RF-012: Búsqueda avanzada con filtros y paginación. Permiso: USR_SEARCH."""
    req_id = obtener_o_generar(x_request_id)
    sesion = validar_sesion_activa(authorization, req_id)
    validar_permiso(sesion["rol_id"], "USR_SEARCH", req_id)

    if pagina < 1:
        raise HTTPException(400, detail="El número de página debe ser mayor o igual a 1")
    if not (1 <= items_por_pagina <= ITEMS_POR_PAGINA_MAX):
        raise HTTPException(400, detail=f"items_por_pagina debe estar entre 1 y {ITEMS_POR_PAGINA_MAX}")

    resultado = svc.busqueda_avanzada(
        nombre, numero_documento, email, estado, ciudad, pagina, items_por_pagina
    )
    registrar_log_async(req_id, "Búsqueda avanzada", "GET", "/api/v1/users",
                        200, sesion.get("user_id"), "OK")
    return RespuestaEstandar.ok(req_id, resultado, "Búsqueda completada")


# ── GET /users/stats/by-state ─────────────────────────────────────────────────
@router.get("/stats/by-state", response_model=RespuestaEstandar)
async def estadisticas(
    authorization: str = Header(..., alias="Authorization"),
    x_request_id:  Optional[str] = Header(None, alias="X-Request-ID"),
):
    """USR-RF-024: Estadísticas por estado. Permiso: USR_STATS_READ."""
    req_id = obtener_o_generar(x_request_id)
    sesion = validar_sesion_activa(authorization, req_id)
    validar_permiso(sesion["rol_id"], "USR_STATS_READ", req_id)
    return RespuestaEstandar.ok(req_id, svc.obtener_estadisticas(), "Estadísticas obtenidas")


# ── GET /users/by-role/{rol_id} ───────────────────────────────────────────────
@router.get("/by-role/{rol_id}", response_model=RespuestaEstandar)
async def listar_por_rol(
    rol_id: int,
    estado: Optional[str] = None,
    pagina: int = PAGINA_DEFAULT,
    items_por_pagina: int = ITEMS_POR_PAGINA_DEFAULT,
    authorization: str = Header(..., alias="Authorization"),
    x_request_id:  Optional[str] = Header(None, alias="X-Request-ID"),
):
    """USR-RF-023: Listar usuarios por rol. Permiso: USR_LIST_BY_ROLE."""
    req_id = obtener_o_generar(x_request_id)
    sesion = validar_sesion_activa(authorization, req_id)
    validar_permiso(sesion["rol_id"], "USR_LIST_BY_ROLE", req_id)
    return RespuestaEstandar.ok(
        req_id, svc.listar_por_rol(rol_id, estado, pagina, items_por_pagina), "OK"
    )


# ── GET /users/by-email/{email} ───────────────────────────────────────────────
@router.get("/by-email/{email}", response_model=RespuestaEstandar)
async def obtener_por_email(
    email: str,
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID"),
    x_app_token:  Optional[str] = Header(None, alias="X-App-Token"),
    authorization: Optional[str] = Header(None, alias="Authorization"),
):
    """
    USR-RF-008: Consultar usuario por email.
    Si el X-App-Token pertenece a ms-autenticacion → incluye password_hash.
    """
    req_id  = obtener_o_generar(x_request_id)
    es_auth = es_token_autenticacion(x_app_token)

    if es_auth:
        usuario = svc.obtener_por_email_con_hash(email)
    else:
        sesion = validar_sesion_activa(authorization, req_id)
        validar_permiso(sesion["rol_id"], "USR_READ", req_id)
        usuario = svc.obtener_por_email_publico(email)

    if not usuario:
        raise HTTPException(404, detail="Usuario no encontrado")

    registrar_log_async(req_id, "Consultar por email", "GET",
                        f"/api/v1/users/by-email/{email}", 200, None, "OK")
    return RespuestaEstandar.ok(req_id, usuario, "Usuario encontrado")


# ── GET /users/{usuario_id} ───────────────────────────────────────────────────
@router.get("/{usuario_id}", response_model=RespuestaEstandar)
async def obtener_usuario(
    usuario_id: int,
    authorization: str = Header(..., alias="Authorization"),
    x_request_id:  Optional[str] = Header(None, alias="X-Request-ID"),
):
    """USR-RF-007: Consultar usuario por ID. Permiso: USR_READ."""
    req_id = obtener_o_generar(x_request_id)
    sesion = validar_sesion_activa(authorization, req_id)
    validar_permiso(sesion["rol_id"], "USR_READ", req_id)

    usuario = svc.obtener_por_id(usuario_id)
    if not usuario:
        raise HTTPException(404, detail="Usuario no encontrado")

    registrar_log_async(req_id, "Consultar usuario", "GET",
                        f"/api/v1/users/{usuario_id}", 200, sesion.get("user_id"), "OK")
    return RespuestaEstandar.ok(req_id, UsuarioRespuesta(**usuario), "Usuario encontrado")


# ── GET /users/{usuario_id}/validate ─────────────────────────────────────────
@router.get("/{usuario_id}/validate", response_model=RespuestaEstandar)
async def validar_existencia(
    usuario_id: int,
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID"),
    x_app_token:  Optional[str] = Header(None, alias="X-App-Token"),
):
    """USR-RF-021: Validar existencia (servicio interno para ms-programas)."""
    req_id    = obtener_o_generar(x_request_id)
    resultado = svc.validar_existencia(usuario_id)
    registrar_log_async(req_id, "Validar existencia", "GET",
                        f"/api/v1/users/{usuario_id}/validate", 200, None, "OK")
    return RespuestaEstandar.ok(req_id, resultado, "Validación completada")


# ── PUT /users/{usuario_id} ───────────────────────────────────────────────────
@router.put("/{usuario_id}", response_model=RespuestaEstandar)
async def actualizar_usuario(
    usuario_id: int,
    datos: UsuarioActualizar,
    authorization: str = Header(..., alias="Authorization"),
    x_request_id:  Optional[str] = Header(None, alias="X-Request-ID"),
):
    """USR-RF-010: Actualizar datos básicos. Permiso: USR_UPDATE."""
    req_id = obtener_o_generar(x_request_id)
    sesion = validar_sesion_activa(authorization, req_id)
    validar_permiso(sesion["rol_id"], "USR_UPDATE", req_id)

    usuario, error = svc.actualizar_usuario(
        usuario_id,
        datos.username,
        str(datos.email) if datos.email else None,
        datos.rol_id,
    )
    if error:
        codigo, msg = _parsear_error(error)
        raise HTTPException(status_code=codigo, detail=msg)

    registrar_log_async(req_id, "Actualizar usuario", "PUT",
                        f"/api/v1/users/{usuario_id}", 200,
                        sesion.get("user_id"), "Actualizado")
    return RespuestaEstandar.ok(req_id, UsuarioRespuesta(**usuario),
                                "Usuario actualizado exitosamente")


# ── DELETE /users/{usuario_id} ────────────────────────────────────────────────
@router.delete("/{usuario_id}", response_model=RespuestaEstandar)
async def desactivar_usuario(
    usuario_id: int,
    body: CambiarEstadoBody,
    authorization: str = Header(..., alias="Authorization"),
    x_request_id:  Optional[str] = Header(None, alias="X-Request-ID"),
):
    """USR-RF-011: Desactivar usuario (soft delete). Permiso: USR_DELETE."""
    req_id = obtener_o_generar(x_request_id)
    sesion = validar_sesion_activa(authorization, req_id)
    validar_permiso(sesion["rol_id"], "USR_DELETE", req_id)

    if not body.motivo.strip():
        raise HTTPException(400, detail="Debe proporcionar un motivo para la desactivación")

    usuario, error = hist_svc.cambiar_estado(
        usuario_id, "inactivo", body.motivo, sesion["user_id"]
    )
    if error:
        codigo, msg = _parsear_error(error)
        raise HTTPException(status_code=codigo, detail=msg)

    notificar_async("user_state_change", usuario_id,
                    {"new_state": "inactivo", "reason": body.motivo}, req_id)
    registrar_log_async(req_id, "Desactivar usuario", "DELETE",
                        f"/api/v1/users/{usuario_id}", 200,
                        sesion.get("user_id"), "Usuario desactivado")
    return RespuestaEstandar.ok(req_id, None, "Usuario desactivado exitosamente")


# ── PATCH /users/{usuario_id}/state ──────────────────────────────────────────
@router.patch("/{usuario_id}/state", response_model=RespuestaEstandar)
async def cambiar_estado(
    usuario_id: int,
    body: CambiarEstadoBody,
    authorization: str = Header(..., alias="Authorization"),
    x_request_id:  Optional[str] = Header(None, alias="X-Request-ID"),
):
    """USR-RF-015: Cambiar estado de usuario. Permiso: USR_CHANGE_STATE."""
    req_id = obtener_o_generar(x_request_id)
    sesion = validar_sesion_activa(authorization, req_id)
    validar_permiso(sesion["rol_id"], "USR_CHANGE_STATE", req_id)

    if not body.estado_nuevo:
        raise HTTPException(400, detail="Debe proporcionar el nuevo estado")

    usuario, error = hist_svc.cambiar_estado(
        usuario_id, body.estado_nuevo, body.motivo, sesion["user_id"]
    )
    if error:
        codigo, msg = _parsear_error(error)
        raise HTTPException(status_code=codigo, detail=msg)

    notificar_async("user_state_change", usuario_id,
                    {"new_state": body.estado_nuevo, "reason": body.motivo}, req_id)
    registrar_log_async(req_id, "Cambiar estado", "PATCH",
                        f"/api/v1/users/{usuario_id}/state", 200,
                        sesion.get("user_id"), f"Estado → {body.estado_nuevo}")
    return RespuestaEstandar.ok(req_id, None, "Estado actualizado exitosamente")


# ── POST /users/{usuario_id}/reactivate ──────────────────────────────────────
@router.post("/{usuario_id}/reactivate", response_model=RespuestaEstandar)
async def reactivar_usuario(
    usuario_id: int,
    body: CambiarEstadoBody,
    authorization: str = Header(..., alias="Authorization"),
    x_request_id:  Optional[str] = Header(None, alias="X-Request-ID"),
):
    """USR-RF-020: Reactivar usuario. Permiso: USR_REACTIVATE."""
    req_id = obtener_o_generar(x_request_id)
    sesion = validar_sesion_activa(authorization, req_id)
    validar_permiso(sesion["rol_id"], "USR_REACTIVATE", req_id)

    usuario, error = hist_svc.cambiar_estado(
        usuario_id, "activo", body.motivo, sesion["user_id"]
    )
    if error:
        codigo, msg = _parsear_error(error)
        raise HTTPException(status_code=codigo, detail=msg)

    notificar_async("user_state_change", usuario_id,
                    {"new_state": "activo", "reason": body.motivo}, req_id)
    registrar_log_async(req_id, "Reactivar usuario", "POST",
                        f"/api/v1/users/{usuario_id}/reactivate", 200,
                        sesion.get("user_id"), "Usuario reactivado")
    return RespuestaEstandar.ok(req_id, None, "Usuario reactivado exitosamente")


# ── PATCH /users/{usuario_id}/password ───────────────────────────────────────
@router.patch("/{usuario_id}/password", response_model=RespuestaEstandar)
async def cambiar_password(
    usuario_id: int,
    datos: CambiarPassword,
    authorization: str = Header(..., alias="Authorization"),
    x_request_id:  Optional[str] = Header(None, alias="X-Request-ID"),
):
    """USR-RF-022: Actualizar contraseña. Solo el propio usuario."""
    req_id = obtener_o_generar(x_request_id)
    sesion = validar_sesion_activa(authorization, req_id)

    if sesion["user_id"] != usuario_id:
        raise HTTPException(403, detail="Solo puede cambiar su propia contraseña")

    ok, error = svc.cambiar_password(
        usuario_id, datos.password_actual_encrypted, datos.password_nueva_encrypted
    )
    if not ok:
        codigo, msg = _parsear_error(error)
        raise HTTPException(status_code=codigo, detail=msg)

    notificar_async("user_security_alert", usuario_id, {}, req_id)
    registrar_log_async(req_id, "Cambiar contraseña", "PATCH",
                        f"/api/v1/users/{usuario_id}/password", 200,
                        sesion.get("user_id"), "Contraseña actualizada")
    return RespuestaEstandar.ok(req_id, None, "Contraseña actualizada exitosamente")
```

### routes/perfiles.py

```python
# routes/perfiles.py
from fastapi import APIRouter, Header, HTTPException, status
from typing import Optional

from models.perfil   import PerfilCrearActualizar, PerfilRespuesta
from models.response import RespuestaEstandar
import services.perfil_service as svc

from utils.request_id    import obtener_o_generar
from utils.audit         import registrar_log_async
from utils.inter_service import (
    validar_sesion_activa, validar_permiso, es_token_notificaciones
)

router = APIRouter(prefix="/users", tags=["Perfiles"])


@router.get("/{usuario_id}/profile", response_model=RespuestaEstandar)
async def obtener_perfil(
    usuario_id: int,
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID"),
    x_app_token:  Optional[str] = Header(None, alias="X-App-Token"),
    authorization: Optional[str] = Header(None, alias="Authorization"),
):
    """USR-RF-013: Consultar perfil extendido. Permiso: USR_PROFILE_READ."""
    req_id = obtener_o_generar(x_request_id)

    if not es_token_notificaciones(x_app_token):
        sesion = validar_sesion_activa(authorization, req_id)
        validar_permiso(sesion["rol_id"], "USR_PROFILE_READ", req_id)

    perfil, error = svc.obtener_perfil(usuario_id)
    if error:
        codigo = int(error[:3]) if error[:3].isdigit() else 404
        raise HTTPException(status_code=codigo, detail=error[4:] if ":" in error else error)

    registrar_log_async(req_id, "Consultar perfil", "GET",
                        f"/api/v1/users/{usuario_id}/profile", 200, None, "OK")
    return RespuestaEstandar.ok(req_id, PerfilRespuesta(**perfil), "Perfil obtenido")


@router.put("/{usuario_id}/profile", response_model=RespuestaEstandar)
async def actualizar_perfil(
    usuario_id: int,
    datos: PerfilCrearActualizar,
    authorization: str = Header(..., alias="Authorization"),
    x_request_id:  Optional[str] = Header(None, alias="X-Request-ID"),
):
    """USR-RF-014: Crear o actualizar perfil extendido. Permiso: USR_PROFILE_UPDATE."""
    req_id = obtener_o_generar(x_request_id)
    sesion = validar_sesion_activa(authorization, req_id)
    validar_permiso(sesion["rol_id"], "USR_PROFILE_UPDATE", req_id)

    datos_dict          = datos.model_dump(exclude_none=False)
    datos_dict["genero"] = datos.genero.value

    perfil, error, fue_creado = svc.crear_o_actualizar_perfil(usuario_id, datos_dict)
    if error:
        codigo = int(error[:3]) if error[:3].isdigit() else 400
        raise HTTPException(status_code=codigo, detail=error[4:] if ":" in error else error)

    http_code = status.HTTP_201_CREATED if fue_creado else status.HTTP_200_OK
    msg       = "Perfil creado exitosamente" if fue_creado else "Perfil actualizado exitosamente"
    registrar_log_async(req_id, "Actualizar perfil", "PUT",
                        f"/api/v1/users/{usuario_id}/profile",
                        http_code, sesion.get("user_id"), msg)
    return RespuestaEstandar.ok(req_id, PerfilRespuesta(**perfil), msg)
```

### routes/historial.py

```python
# routes/historial.py
from fastapi import APIRouter, Header
from typing import Optional

from models.response import RespuestaEstandar
import services.historial_service as svc
from utils.request_id    import obtener_o_generar
from utils.audit         import registrar_log_async
from utils.inter_service import validar_sesion_activa, validar_permiso

router = APIRouter(prefix="/users", tags=["Historial de Estados"])


@router.get("/{usuario_id}/state-history", response_model=RespuestaEstandar)
async def listar_historial(
    usuario_id: int,
    authorization: str = Header(..., alias="Authorization"),
    x_request_id:  Optional[str] = Header(None, alias="X-Request-ID"),
):
    """USR-RF-016: Consultar historial de cambios de estado. Permiso: USR_HISTORY_READ."""
    req_id   = obtener_o_generar(x_request_id)
    sesion   = validar_sesion_activa(authorization, req_id)
    validar_permiso(sesion["rol_id"], "USR_HISTORY_READ", req_id)

    historial = svc.listar_historial(usuario_id)
    msg       = "Historial obtenido" if historial else "No hay historial de cambios para este usuario"
    registrar_log_async(req_id, "Consultar historial", "GET",
                        f"/api/v1/users/{usuario_id}/state-history",
                        200, sesion.get("user_id"), f"{len(historial)} registros")
    return RespuestaEstandar.ok(req_id, historial, msg)
```

### routes/preferencias.py

```python
# routes/preferencias.py
from fastapi import APIRouter, Header, HTTPException
from typing import Optional

from models.preferencias_notificacion import PreferenciasActualizar, PreferenciasRespuesta
from models.response import RespuestaEstandar
import services.preferencias_service as svc
from utils.request_id    import obtener_o_generar
from utils.audit         import registrar_log_async
from utils.inter_service import (
    validar_sesion_activa, validar_permiso, es_token_notificaciones
)

router = APIRouter(prefix="/users", tags=["Preferencias de Notificación"])


@router.get("/{usuario_id}/notification-preferences", response_model=RespuestaEstandar)
async def obtener_preferencias(
    usuario_id: int,
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID"),
    x_app_token:  Optional[str] = Header(None, alias="X-App-Token"),
    authorization: Optional[str] = Header(None, alias="Authorization"),
):
    """
    USR-RF-018: Consultar preferencias de notificación.
    Accesible por usuario autenticado (USR_PREFERENCES_READ) o ms-notificaciones.
    """
    req_id = obtener_o_generar(x_request_id)

    if not es_token_notificaciones(x_app_token):
        sesion = validar_sesion_activa(authorization, req_id)
        validar_permiso(sesion["rol_id"], "USR_PREFERENCES_READ", req_id)

    pref, error = svc.obtener_preferencias(usuario_id)
    if error:
        raise HTTPException(404, detail=error[4:] if ":" in error else error)

    registrar_log_async(req_id, "Consultar preferencias", "GET",
                        f"/api/v1/users/{usuario_id}/notification-preferences",
                        200, None, "OK")
    return RespuestaEstandar.ok(req_id, pref, "Preferencias de notificación obtenidas")


@router.put("/{usuario_id}/notification-preferences", response_model=RespuestaEstandar)
async def actualizar_preferencias(
    usuario_id: int,
    datos: PreferenciasActualizar,
    authorization: str = Header(..., alias="Authorization"),
    x_request_id:  Optional[str] = Header(None, alias="X-Request-ID"),
):
    """USR-RF-019: Actualizar preferencias de notificación. Permiso: USR_PREFERENCES_UPDATE."""
    req_id = obtener_o_generar(x_request_id)
    sesion = validar_sesion_activa(authorization, req_id)
    validar_permiso(sesion["rol_id"], "USR_PREFERENCES_UPDATE", req_id)

    datos_dict = {k: v for k, v in datos.model_dump().items() if v is not None}
    pref, error = svc.crear_o_actualizar_preferencias(usuario_id, datos_dict)
    if error:
        raise HTTPException(400, detail=error[4:] if ":" in error else error)

    registrar_log_async(req_id, "Actualizar preferencias", "PUT",
                        f"/api/v1/users/{usuario_id}/notification-preferences",
                        200, sesion.get("user_id"), "Actualizado")
    return RespuestaEstandar.ok(req_id, pref, "Preferencias actualizadas exitosamente")
```

### routes/tipos_documento.py

```python
# routes/tipos_documento.py
from fastapi import APIRouter, Header
from typing import Optional

from models.response import RespuestaEstandar
import services.tipo_documento_service as svc
from utils.request_id    import obtener_o_generar
from utils.audit         import registrar_log_async
from utils.inter_service import validar_sesion_activa, validar_permiso

router = APIRouter(prefix="/document-types", tags=["Tipos de Documento"])


@router.get("", response_model=RespuestaEstandar)
async def listar_tipos(
    authorization: str = Header(..., alias="Authorization"),
    x_request_id:  Optional[str] = Header(None, alias="X-Request-ID"),
):
    """USR-RF-017: Catálogo de tipos de documento activos. Permiso: USR_READ."""
    req_id = obtener_o_generar(x_request_id)
    sesion = validar_sesion_activa(authorization, req_id)
    validar_permiso(sesion["rol_id"], "USR_READ", req_id)

    tipos = svc.listar_activos()
    registrar_log_async(req_id, "Listar tipos de documento", "GET",
                        "/api/v1/document-types", 200, sesion.get("user_id"), "OK")
    return RespuestaEstandar.ok(req_id, tipos, "Tipos de documento obtenidos")
```

---

## 10. Punto de entrada — main.py

```python
# main.py
from fastapi import FastAPI
from config import APP_TITULO, APP_DESCRIPCION, APP_VERSION, APP_PREFIX

from routes.usuarios        import router as router_usuarios
from routes.perfiles        import router as router_perfiles
from routes.historial       import router as router_historial
from routes.preferencias    import router as router_preferencias
from routes.tipos_documento import router as router_tipos

app = FastAPI(
    title=APP_TITULO,
    description=APP_DESCRIPCION,
    version=APP_VERSION,
)

app.include_router(router_usuarios,     prefix=APP_PREFIX)
app.include_router(router_perfiles,     prefix=APP_PREFIX)
app.include_router(router_historial,    prefix=APP_PREFIX)
app.include_router(router_preferencias, prefix=APP_PREFIX)
app.include_router(router_tipos,        prefix=APP_PREFIX)


@app.get("/", tags=["Health Check"])
def health_check():
    return {"service": APP_TITULO, "version": APP_VERSION, "status": "ok"}
```

**Arranque:**

```bash
uvicorn main:app --reload --port 8000
```

Documentación Swagger disponible en: `http://localhost:8000/docs`

---

## 11. Flujo completo de una petición

Ejemplo: **POST /api/v1/users** — Crear usuario

```
Cliente
  │
  │  POST /api/v1/users
  │  Authorization: Bearer {token}
  │  Body: {username, email, password_encrypted, rol_id}
  ▼
routes/usuarios.py :: crear_usuario()
  │
  ├─► utils/request_id.py       → genera o reutiliza Request ID (USR-RF-003)
  │
  ├─► utils/inter_service.py    → validar_sesion_activa()       [USR-RF-001]
  │       └─► POST ms-autenticacion/validate-session  (síncrono, 3s timeout)
  │
  ├─► utils/inter_service.py    → validar_permiso("USR_CREATE") [USR-RF-002]
  │       └─► POST ms-roles/validate-permission       (síncrono, 3s timeout)
  │
  ├─► services/usuario_service.py :: crear_usuario()
  │       ├─► repository/ :: existe_username()  → PostgreSQL
  │       ├─► repository/ :: existe_email()     → PostgreSQL
  │       ├─► utils/inter_service.py :: validar_rol_externo()
  │       │       └─► GET ms-roles/{rol_id}/validate
  │       ├─► utils/crypto.py :: descifrar_aes256()
  │       ├─► utils/crypto.py :: hashear_bcrypt()
  │       └─► repository/ :: crear()            → PostgreSQL
  │
  ├─► utils/inter_service.py    → notificar_async("user_welcome")
  │       └─► Thread → POST ms-notificaciones/send  (asíncrono, 1s timeout)
  │
  ├─► utils/audit.py            → registrar_log_async()         [USR-RF-004]
  │       └─► Thread → POST ms-auditoria/audit/logs (asíncrono, 0.5s timeout)
  │
  └─► models/response.py        → RespuestaEstandar.ok()        [USR-RF-005]
          └─► 201 Created
              {request_id, success:true, data:{...}, message, timestamp}
```

**Reglas clave del flujo:**
- El cambio de estado (`PATCH /state`, `DELETE`, `POST /reactivate`) ejecuta UPDATE + INSERT historial en **una sola transacción** PostgreSQL.
- Los envíos a ms-notificaciones y ms-auditoria son **fire-and-forget**: si fallan, la respuesta al cliente no se ve afectada.
- Si ms-autenticacion o ms-roles no responden → `503 Service Unavailable`.
- El `password_hash` **nunca** aparece en respuestas al cliente ni en logs.

---

## 12. Tabla de endpoints y permisos

| Método | Endpoint | RF | Permiso / Acceso |
|--------|----------|----|------------------|
| `POST` | `/users` | USR-RF-006 | `USR_CREATE` |
| `GET` | `/users` | USR-RF-012 | `USR_SEARCH` |
| `GET` | `/users/stats/by-state` | USR-RF-024 | `USR_STATS_READ` |
| `GET` | `/users/by-role/{rol_id}` | USR-RF-023 | `USR_LIST_BY_ROLE` |
| `GET` | `/users/by-email/{email}` | USR-RF-008 | `USR_READ` o token AUTH |
| `GET` | `/users/{id}` | USR-RF-007 | `USR_READ` |
| `GET` | `/users/{id}/validate` | USR-RF-021 | Token de aplicación |
| `PUT` | `/users/{id}` | USR-RF-010 | `USR_UPDATE` |
| `DELETE` | `/users/{id}` | USR-RF-011 | `USR_DELETE` |
| `PATCH` | `/users/{id}/state` | USR-RF-015 | `USR_CHANGE_STATE` |
| `POST` | `/users/{id}/reactivate` | USR-RF-020 | `USR_REACTIVATE` |
| `PATCH` | `/users/{id}/password` | USR-RF-022 | Solo propio usuario |
| `GET` | `/users/{id}/profile` | USR-RF-013 | `USR_PROFILE_READ` o token NOT |
| `PUT` | `/users/{id}/profile` | USR-RF-014 | `USR_PROFILE_UPDATE` |
| `GET` | `/users/{id}/state-history` | USR-RF-016 | `USR_HISTORY_READ` |
| `GET` | `/users/{id}/notification-preferences` | USR-RF-018 | `USR_PREFERENCES_READ` o token NOT |
| `PUT` | `/users/{id}/notification-preferences` | USR-RF-019 | `USR_PREFERENCES_UPDATE` |
| `GET` | `/document-types` | USR-RF-017 | `USR_READ` |

---

*Fin de la guía — ms-usuarios [USR] v1.0*
