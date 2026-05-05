# 📋 Firmas de Funciones y Endpoints

## Información General

**Base URL:** `http://localhost:8000/api/v1`  
**Autenticación:** Bearer Token en header `Authorization`  
**Request ID:** Header `X-Request-ID` (se genera automáticamente si no se proporciona)  
**App Token:** Header `X-App-Token` (para servicios internos)  

---

## 📑 Tabla de Contenidos

1. [Usuarios](#usuarios)
2. [Perfiles](#perfiles)
3. [Historial de Estados](#historial-de-estados)
4. [Preferencias de Notificación](#preferencias-de-notificación)
5. [Tipos de Documento](#tipos-de-documento)

---

## 👥 Usuarios

### 1. Crear Usuario
```
POST /users
Status Code: 201 Created
Permiso: USR_CREATE
RF: USR-RF-006
```

**Firma:**
```python
async def crear_usuario(
    datos: UsuarioCrear,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID"),
    x_app_token: Optional[str] = Header(None, alias="X-App-Token"),
) -> RespuestaEstandar
```

**Modelo Request - UsuarioCrear:**
```python
class UsuarioCrear(BaseModel):
    username: str              # Mín. 3 caracteres
    email: EmailStr           # Formato email válido
    password_encrypted: str   # Cifrado AES-256 + Base64
    rol_id: int              # ID del rol válido
```

**Modelo Response - UsuarioRespuesta:**
```python
class UsuarioRespuesta(BaseModel):
    id: int
    username: str
    email: str
    estado: str
    rol_id: int
    created_at: datetime
    updated_at: datetime
```

---

### 2. Obtener Usuario por ID
```
GET /users/{usuario_id}
Status Code: 200 OK
Permiso: USR_READ
RF: USR-RF-007
```

**Firma:**
```python
async def obtener_usuario(
    usuario_id: int,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID"),
) -> RespuestaEstandar
```

**Path Parameters:**
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `usuario_id` | int | ID del usuario a consultar |

---

### 3. Obtener Usuario por Email
```
GET /users/by-email/{email}
Status Code: 200 OK
Permiso: USR_READ (o token ms-autenticacion)
RF: USR-RF-008
```

**Firma:**
```python
async def obtener_usuario_por_email(
    email: str,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID"),
    x_app_token: Optional[str] = Header(None, alias="X-App-Token"),
) -> RespuestaEstandar
```

**Path Parameters:**
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `email` | str | Email del usuario a consultar |

**Nota:** Si es ms-autenticacion incluye `password_hash`

---

### 4. Actualizar Usuario
```
PUT /users/{usuario_id}
Status Code: 200 OK
Permiso: USR_UPDATE
RF: USR-RF-010
```

**Firma:**
```python
async def actualizar_usuario(
    usuario_id: int,
    datos: UsuarioActualizar,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID"),
) -> RespuestaEstandar
```

**Modelo Request - UsuarioActualizar:**
```python
class UsuarioActualizar(BaseModel):
    username: Optional[str] = None      # Mín. 3 caracteres (opcional)
    email: Optional[EmailStr] = None    # Formato email (opcional)
    rol_id: Optional[int] = None        # ID del rol (opcional)
```

---

### 5. Búsqueda Avanzada de Usuarios
```
GET /users
Status Code: 200 OK
Permiso: USR_SEARCH
RF: USR-RF-012
```

**Firma:**
```python
async def busqueda_avanzada(
    nombre: Optional[str] = None,
    numero_documento: Optional[str] = None,
    email: Optional[str] = None,
    estado: Optional[str] = None,
    ciudad: Optional[str] = None,
    pagina: int = PAGINA_DEFAULT,
    items_por_pagina: int = ITEMS_POR_PAGINA_DEFAULT,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID"),
) -> RespuestaEstandar
```

**Query Parameters:**
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `nombre` | string | Búsqueda en primer_nombre y primer_apellido (ILIKE) |
| `numero_documento` | string | Búsqueda exacta en usr_perfiles |
| `email` | string | Búsqueda exacta |
| `estado` | string | activo, inactivo, suspendido, eliminado |
| `ciudad` | string | Búsqueda en ciudad del perfil |
| `pagina` | int | Número de página (default: 1) |
| `items_por_pagina` | int | Registros por página (default: 10, máx: 100) |

---

### 6. Desactivar Usuario (Soft Delete)
```
DELETE /users/{usuario_id}
Status Code: 200 OK
Permiso: USR_DELETE
RF: USR-RF-011
```

**Firma:**
```python
async def desactivar_usuario(
    usuario_id: int,
    datos: CambiarEstadoBody,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID"),
) -> RespuestaEstandar
```

**Modelo Request - CambiarEstadoBody:**
```python
class CambiarEstadoBody(BaseModel):
    motivo: str  # Razón de desactivación
```

---

### 7. Cambiar Estado de Usuario
```
PATCH /users/{usuario_id}/state
Status Code: 200 OK
Permiso: USR_CHANGE_STATE
RF: USR-RF-015
```

**Firma:**
```python
async def cambiar_estado_usuario(
    usuario_id: int,
    datos: CambiarEstadoBody,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID"),
) -> RespuestaEstandar
```

**Modelo Request - CambiarEstadoBody:**
```python
class CambiarEstadoBody(BaseModel):
    estado_nuevo: str  # activo, inactivo, suspendido, eliminado
    motivo: str       # Razón del cambio de estado
```

---

### 8. Reactivar Usuario
```
POST /users/{usuario_id}/reactivate
Status Code: 200 OK
Permiso: USR_REACTIVATE
RF: USR-RF-020
```

**Firma:**
```python
async def reactivar_usuario(
    usuario_id: int,
    datos: CambiarEstadoBody,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID"),
) -> RespuestaEstandar
```

---

### 9. Validar Existencia de Usuario
```
GET /users/{usuario_id}/validate
Status Code: 200 OK
Permiso: Ninguno (servicio interno)
RF: USR-RF-021
```

**Firma:**
```python
async def validar_usuario(
    usuario_id: int,
    x_app_token: Optional[str] = Header(None, alias="X-App-Token"),
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID"),
) -> RespuestaEstandar
```

---

### 10. Cambiar Contraseña
```
POST /users/{usuario_id}/change-password
Status Code: 200 OK
Permiso: USR_CHANGE_PASSWORD
RF: USR-RF-022
```

**Firma:**
```python
async def cambiar_password(
    usuario_id: int,
    datos: CambiarPassword,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID"),
) -> RespuestaEstandar
```

**Modelo Request - CambiarPassword:**
```python
class CambiarPassword(BaseModel):
    password_actual_encrypted: str   # Contraseña actual (AES-256 + Base64)
    password_nueva_encrypted: str    # Nueva contraseña (AES-256 + Base64)
```

---

## 👤 Perfiles

### 1. Obtener Perfil de Usuario
```
GET /users/{usuario_id}/profile
Status Code: 200 OK
Permiso: USR_PROFILE_READ (o token ms-notificaciones)
RF: USR-RF-013
```

**Firma:**
```python
async def obtener_perfil(
    usuario_id: int,
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID"),
    x_app_token: Optional[str] = Header(None, alias="X-App-Token"),
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> RespuestaEstandar
```

---

### 2. Crear o Actualizar Perfil
```
PUT /users/{usuario_id}/profile
Status Code: 200 OK / 201 Created
Permiso: USR_PROFILE_UPDATE
RF: USR-RF-014
```

**Firma:**
```python
async def actualizar_perfil(
    usuario_id: int,
    datos: PerfilCrearActualizar,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID"),
) -> RespuestaEstandar
```

**Modelo Request - PerfilCrearActualizar:**
```python
class PerfilCrearActualizar(BaseModel):
    tipo_documento_id: int
    numero_documento: str
    primer_nombre: str
    segundo_nombre: Optional[str] = None
    primer_apellido: str
    segundo_apellido: Optional[str] = None
    fecha_nacimiento: date             # Mín. 14 años
    genero: GeneroEnum                 # masculino, femenino, otro, prefiero_no_decir
    direccion_residencia: str
    ciudad: str
    departamento: str
    telefono_fijo: Optional[str] = None
    telefono_movil: str
    contacto_emergencia_nombre: str
    contacto_emergencia_telefono: str
    biografia: Optional[str] = None
```

**Enum - GeneroEnum:**
```python
class GeneroEnum(str, Enum):
    masculino = "masculino"
    femenino = "femenino"
    otro = "otro"
    prefiero_no_decir = "prefiero_no_decir"
```

---

## 📜 Historial de Estados

### 1. Listar Historial de Usuario
```
GET /users/{usuario_id}/state-history
Status Code: 200 OK
Permiso: USR_HISTORY_READ
RF: USR-RF-016
```

**Firma:**
```python
async def listar_historial(
    usuario_id: int,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID"),
) -> RespuestaEstandar
```

**Modelo Response - HistorialEstado:**
```python
class HistorialEstado(BaseModel):
    id: int
    usuario_id: int
    estado_anterior: str
    estado_nuevo: str
    motivo: str
    usuario_modificador_id: Optional[int]
    created_at: datetime
```

---

## 🔔 Preferencias de Notificación

### 1. Obtener Preferencias de Notificación
```
GET /users/{usuario_id}/notification-preferences
Status Code: 200 OK
Permiso: USR_PREFERENCES_READ (o token ms-notificaciones)
RF: USR-RF-018
```

**Firma:**
```python
async def obtener_preferencias(
    usuario_id: int,
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID"),
    x_app_token: Optional[str] = Header(None, alias="X-App-Token"),
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> RespuestaEstandar
```

---

### 2. Actualizar Preferencias de Notificación
```
PUT /users/{usuario_id}/notification-preferences
Status Code: 200 OK / 201 Created
Permiso: USR_PREFERENCES_UPDATE
RF: USR-RF-019
```

**Firma:**
```python
async def actualizar_preferencias(
    usuario_id: int,
    datos: PreferenciasActualizar,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID"),
) -> RespuestaEstandar
```

**Modelo Request - PreferenciasActualizar:**
```python
class PreferenciasActualizar(BaseModel):
    notif_email: Optional[bool] = None
    notif_sms: Optional[bool] = None
    notif_push: Optional[bool] = None
    canal_preferido: Optional[str] = None  # email, sms, push
    horario_no_molestar_inicio: Optional[time] = None
    horario_no_molestar_fin: Optional[time] = None
```

---

## 📄 Tipos de Documento

### 1. Listar Tipos de Documento
```
GET /document-types
Status Code: 200 OK
Permiso: USR_READ
RF: USR-RF-017
```

**Firma:**
```python
async def listar_tipos(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID"),
) -> RespuestaEstandar
```

**Modelo Response - TipoDocumento:**
```python
class TipoDocumento(BaseModel):
    id: int
    codigo: str           # CC, PA, CE, etc.
    nombre: str          # Cédula de Ciudadanía, Pasaporte, etc.
    descripcion: str
    activo: bool
    created_at: datetime
    updated_at: datetime
```

---

## 🔐 Modelo de Respuesta Estándar

Todos los endpoints devuelven una respuesta estandarizada:

```python
class RespuestaEstandar(BaseModel):
    request_id: str      # ID único de la solicitud
    status: str          # "success" o "error"
    statusCode: int      # Código HTTP
    data: Any           # Datos de la respuesta (puede ser null)
    message: str        # Mensaje descriptivo
```

**Ejemplo de respuesta exitosa:**
```json
{
  "request_id": "USR-1713623400000-a1b2c3d4",
  "status": "success",
  "statusCode": 200,
  "data": { /* datos */ },
  "message": "Operación completada exitosamente"
}
```

**Ejemplo de respuesta con error:**
```json
{
  "request_id": "USR-1713623400001-x9y8z7w6",
  "status": "error",
  "statusCode": 400,
  "data": null,
  "message": "El username debe tener al menos 3 caracteres"
}
```

---

## 🔗 Headers Comunes

| Header | Requerido | Descripción |
|--------|-----------|-------------|
| `Authorization` | Sí (excepto endpoints internos) | Bearer Token |
| `X-Request-ID` | No | ID único de solicitud (se genera si no se proporciona) |
| `X-App-Token` | No | Token de servicio interno (para validaciones internas) |
| `Content-Type` | Sí (en POST/PUT/PATCH) | application/json |

---

## ✅ Códigos HTTP

| Código | Significado |
|--------|-------------|
| 200 | OK - Solicitud exitosa |
| 201 | Created - Recurso creado |
| 400 | Bad Request - Error en la solicitud |
| 401 | Unauthorized - Autenticación requerida |
| 403 | Forbidden - Permiso insuficiente |
| 404 | Not Found - Recurso no encontrado |
| 409 | Conflict - Conflicto (ej: usuario duplicado) |
| 500 | Internal Server Error - Error del servidor |

---

## 📝 Notas Importantes

- Todas las contraseñas deben ser cifradas con **AES-256 + Base64** antes de enviarse
- El `request_id` se genera automáticamente si no se proporciona (formato: `USR-{timestamp}-{random}`)
- Las búsquedas paginadas por defecto traen 10 registros, máximo 100
- Los estados válidos de usuario son: `activo`, `inactivo`, `suspendido`, `eliminado`
- Los cambios de estado se registran automáticamente en el historial
- Las notificaciones se envían de forma asincrónica a ms-notificaciones
