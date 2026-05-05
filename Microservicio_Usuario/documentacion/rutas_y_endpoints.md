# 🚀 API Reference - Rutas y Endpoints

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

### 1. **Crear Usuario**
**Endpoint:** `POST /users`  
**Permiso Requerido:** `USR_CREATE`  
**Requisito Funcional:** USR-RF-006  

**Request:**
```json
{
  "username": "john.doe",
  "email": "john@example.com",
  "password_encrypted": "base64_aes256_cipher",
  "rol_id": 2
}
```

**Response (201 Created):**
```json
{
  "request_id": "USR-1713623400000-a1b2c3d4",
  "status": "success",
  "statusCode": 201,
  "data": {
    "id": 1,
    "username": "john.doe",
    "email": "john@example.com",
    "estado": "activo",
    "rol_id": 2,
    "created_at": "2026-04-19T10:30:00Z",
    "updated_at": "2026-04-19T10:30:00Z"
  },
  "message": "Usuario creado exitosamente"
}
```

**Error Responses:**
| Código | Causa | Mensaje |
|--------|-------|---------|
| 400 | Username corto | "El username debe tener al menos 3 caracteres" |
| 400 | Email inválido | "Email inválido" |
| 409 | Username duplicado | "Username ya existe" |
| 409 | Email duplicado | "Email ya existe" |
| 403 | Permiso insuficiente | "Permiso denegado" |
| 401 | No autenticado | "Sesión inválida" |

---

### 2. **Obtener Usuario por ID**
**Endpoint:** `GET /users/{usuario_id}`  
**Permiso Requerido:** `USR_READ`  
**Requisito Funcional:** USR-RF-007  

**Response (200 OK):**
```json
{
  "request_id": "USR-1713623400001-x9y8z7w6",
  "status": "success",
  "statusCode": 200,
  "data": {
    "id": 1,
    "username": "john.doe",
    "email": "john@example.com",
    "estado": "activo",
    "rol_id": 2,
    "created_at": "2026-04-19T10:30:00Z",
    "updated_at": "2026-04-19T10:30:00Z"
  },
  "message": "Usuario encontrado"
}
```

**Error Responses:**
| Código | Causa |
|--------|-------|
| 404 | Usuario no existe |
| 401 | No autenticado |
| 403 | Permiso insuficiente |

---

### 3. **Obtener Usuario por Email**
**Endpoint:** `GET /users/by-email/{email}`  
**Permiso Requerido:** `USR_READ` (o token de ms-autenticacion)  
**Requisito Funcional:** USR-RF-008  
**Nota:** Si es ms-autenticacion, incluye `password_hash`  

**Response (200 OK):**
```json
{
  "request_id": "USR-1713623400002-p5q4r3s2",
  "status": "success",
  "statusCode": 200,
  "data": {
    "id": 1,
    "username": "john.doe",
    "email": "john@example.com",
    "estado": "activo",
    "rol_id": 2,
    "created_at": "2026-04-19T10:30:00Z",
    "updated_at": "2026-04-19T10:30:00Z"
  },
  "message": "Usuario encontrado"
}
```

**Error Responses:**
| Código | Causa |
|--------|-------|
| 404 | Email no existe |
| 401 | No autenticado |

---

### 4. **Actualizar Usuario**
**Endpoint:** `PUT /users/{usuario_id}`  
**Permiso Requerido:** `USR_UPDATE`  
**Requisito Funcional:** USR-RF-010  
**Nota:** Todos los campos son opcionales  

**Request:**
```json
{
  "username": "john.updated",
  "email": "john.new@example.com",
  "rol_id": 3
}
```

**Response (200 OK):**
```json
{
  "request_id": "USR-1713623400003-m1n0o9p8",
  "status": "success",
  "statusCode": 200,
  "data": {
    "id": 1,
    "username": "john.updated",
    "email": "john.new@example.com",
    "estado": "activo",
    "rol_id": 3,
    "created_at": "2026-04-19T10:30:00Z",
    "updated_at": "2026-04-19T10:40:00Z"
  },
  "message": "Usuario actualizado exitosamente"
}
```

---

### 5. **Búsqueda Avanzada de Usuarios**
**Endpoint:** `GET /users?nombre=&numero_documento=&email=&estado=&ciudad=&pagina=1&items_por_pagina=10`  
**Permiso Requerido:** `USR_SEARCH`  
**Requisito Funcional:** USR-RF-012  
**Nota:** Todos los parámetros de búsqueda son opcionales  

**Parámetros de Query:**
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `nombre` | string | Busca en primer_nombre y primer_apellido (ILIKE) |
| `numero_documento` | string | Búsqueda exacta en usr_perfiles |
| `email` | string | Búsqueda exacta |
| `estado` | string | Valores: activo, inactivo, suspendido, eliminado |
| `ciudad` | string | Búsqueda en ciudad del perfil |
| `pagina` | int | Número de página (default: 1, mín: 1) |
| `items_por_pagina` | int | Registros por página (default: 10, máx: 100) |

**Response (200 OK):**
```json
{
  "request_id": "USR-1713623400004-e7f6g5h4",
  "status": "success",
  "statusCode": 200,
  "data": {
    "resultados": [
      {
        "id": 1,
        "username": "john.doe",
        "email": "john@example.com",
        "estado": "activo",
        "rol_id": 2,
        "created_at": "2026-04-19T10:30:00Z",
        "updated_at": "2026-04-19T10:30:00Z"
      }
    ],
    "total_registros": 1,
    "total_paginas": 1,
    "pagina_actual": 1,
    "items_por_pagina": 10
  },
  "message": "Búsqueda completada"
}
```

---

### 6. **Desactivar Usuario (Soft Delete)**
**Endpoint:** `DELETE /users/{usuario_id}`  
**Permiso Requerido:** `USR_DELETE`  
**Requisito Funcional:** USR-RF-011  
**Nota:** Cambia estado a "inactivo", no elimina datos  

**Request:**
```json
{
  "motivo": "Usuario solicita desactivación de cuenta"
}
```

**Response (200 OK):**
```json
{
  "request_id": "USR-1713623400005-k3l2m1n0",
  "status": "success",
  "statusCode": 200,
  "data": null,
  "message": "Usuario desactivado exitosamente"
}
```

---

### 7. **Cambiar Estado de Usuario**
**Endpoint:** `PATCH /users/{usuario_id}/state`  
**Permiso Requerido:** `USR_CHANGE_STATE`  
**Requisito Funcional:** USR-RF-015  
**Nota:** Registra en historial de estados  

**Request:**
```json
{
  "estado_nuevo": "suspendido",
  "motivo": "Violación de términos de servicio"
}
```

**Response (200 OK):**
```json
{
  "request_id": "USR-1713623400006-d9e8f7g6",
  "status": "success",
  "statusCode": 200,
  "data": null,
  "message": "Estado actualizado exitosamente"
}
```

**Estados válidos:** `activo`, `inactivo`, `suspendido`, `eliminado`

---

### 8. **Reactivar Usuario**
**Endpoint:** `POST /users/{usuario_id}/reactivate`  
**Permiso Requerido:** `USR_REACTIVATE`  
**Requisito Funcional:** USR-RF-020  

**Request:**
```json
{
  "motivo": "El usuario apeló y fue aprobado"
}
```

**Response (200 OK):**
```json
{
  "request_id": "USR-1713623400007-v5w4x3y2",
  "status": "success",
  "statusCode": 200,
  "data": null,
  "message": "Estado actualizado exitosamente"
}
```

---

### 9. **Validar Existencia de Usuario**
**Endpoint:** `GET /users/{usuario_id}/validate`  
**Permiso Requerido:** Ninguno (servicio interno)  
**Requisito Funcional:** USR-RF-021  
**Nota:** Usado por ms-programas para validar usuarios  

**Response (200 OK):**
```json
{
  "request_id": "USR-1713623400008-j6k5l4m3",
  "status": "success",
  "statusCode": 200,
  "data": {
    "existe": true,
    "usuario_id": 1,
    "username": "john.doe",
    "estado": "activo"
  },
  "message": "Validación completada"
}
```

---

### 10. **Listar Usuarios por Rol**
**Endpoint:** `GET /users/by-role/{rol_id}?estado=&pagina=1&items_por_pagina=10`  
**Permiso Requerido:** `USR_LIST_BY_ROLE`  
**Requisito Funcional:** USR-RF-023  

**Parámetros de Query:**
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `estado` | string | Filtro opcional por estado |
| `pagina` | int | Número de página (default: 1) |
| `items_por_pagina` | int | Registros por página (default: 10) |

**Response (200 OK):**
```json
{
  "request_id": "USR-1713623400009-t3u2v1w0",
  "status": "success",
  "statusCode": 200,
  "data": {
    "resultados": [
      {
        "id": 1,
        "username": "john.doe",
        "email": "john@example.com",
        "estado": "activo",
        "rol_id": 2,
        "created_at": "2026-04-19T10:30:00Z",
        "updated_at": "2026-04-19T10:30:00Z"
      }
    ],
    "total_registros": 5,
    "total_paginas": 1,
    "pagina_actual": 1,
    "items_por_pagina": 10
  },
  "message": "OK"
}
```

---

### 11. **Estadísticas de Usuarios por Estado**
**Endpoint:** `GET /users/stats/by-state`  
**Permiso Requerido:** `USR_STATS_READ`  
**Requisito Funcional:** USR-RF-024  

**Response (200 OK):**
```json
{
  "request_id": "USR-1713623400010-h9i8j7k6",
  "status": "success",
  "statusCode": 200,
  "data": {
    "activo": 45,
    "inactivo": 12,
    "suspendido": 3,
    "eliminado": 2,
    "total": 62
  },
  "message": "Estadísticas obtenidas"
}
```

---

### 12. **Cambiar Contraseña**
**Endpoint:** `PATCH /users/{usuario_id}/password`  
**Permiso Requerido:** Ser el usuario autenticado o `USR_ADMIN_PASSWORD`  
**Requisito Funcional:** USR-RF-022  
**Nota:** Ambas contraseñas deben ser cifradas en AES-256  

**Request:**
```json
{
  "password_actual_encrypted": "base64_aes256_cipher",
  "password_nueva_encrypted": "base64_aes256_cipher"
}
```

**Response (200 OK):**
```json
{
  "request_id": "USR-1713623400011-a5b4c3d2",
  "status": "success",
  "statusCode": 200,
  "data": null,
  "message": "Contraseña actualizada exitosamente"
}
```

**Error Responses:**
| Código | Causa |
|--------|-------|
| 401 | Contraseña actual incorrecta |
| 404 | Usuario no existe |

---

## 👤 Perfiles

### 1. **Obtener Perfil Extendido**
**Endpoint:** `GET /users/{usuario_id}/profile`  
**Permiso Requerido:** `USR_PROFILE_READ` (o token de ms-notificaciones)  
**Requisito Funcional:** USR-RF-013  

**Response (200 OK):**
```json
{
  "request_id": "USR-1713623400012-n7o6p5q4",
  "status": "success",
  "statusCode": 200,
  "data": {
    "id": 1,
    "usuario_id": 1,
    "tipo_documento_id": 1,
    "tipo_documento_codigo": "CC",
    "tipo_documento_nombre": "Cédula de Ciudadanía",
    "numero_documento": "1234567890",
    "primer_nombre": "John",
    "segundo_nombre": "Michael",
    "primer_apellido": "Doe",
    "segundo_apellido": "Smith",
    "fecha_nacimiento": "1990-05-15",
    "genero": "masculino",
    "direccion_residencia": "Calle 123 #45-67",
    "ciudad": "Bogotá",
    "departamento": "Cundinamarca",
    "telefono_fijo": "1 2345678",
    "telefono_movil": "3001234567",
    "contacto_emergencia_nombre": "Jane Doe",
    "contacto_emergencia_telefono": "3009876543",
    "biografia": "Desarrollador de software con 10 años de experiencia",
    "created_at": "2026-04-19T10:30:00Z",
    "updated_at": "2026-04-19T10:30:00Z"
  },
  "message": "Perfil obtenido"
}
```

**Error Responses:**
| Código | Causa |
|--------|-------|
| 404 | Usuario o perfil no existe |
| 403 | Permiso insuficiente |

---

### 2. **Crear o Actualizar Perfil**
**Endpoint:** `PUT /users/{usuario_id}/profile`  
**Permiso Requerido:** `USR_PROFILE_UPDATE`  
**Requisito Funcional:** USR-RF-014  
**Nota:** Crea si no existe (201), actualiza si existe (200)  

**Request:**
```json
{
  "tipo_documento_id": 1,
  "numero_documento": "1234567890",
  "primer_nombre": "John",
  "segundo_nombre": "Michael",
  "primer_apellido": "Doe",
  "segundo_apellido": "Smith",
  "fecha_nacimiento": "1990-05-15",
  "genero": "masculino",
  "direccion_residencia": "Calle 123 #45-67",
  "ciudad": "Bogotá",
  "departamento": "Cundinamarca",
  "telefono_fijo": "1 2345678",
  "telefono_movil": "3001234567",
  "contacto_emergencia_nombre": "Jane Doe",
  "contacto_emergencia_telefono": "3009876543",
  "biografia": "Desarrollador de software"
}
```

**Response (201 Created) - Nuevo perfil:**
```json
{
  "request_id": "USR-1713623400013-x3y2z1a0",
  "status": "success",
  "statusCode": 201,
  "data": {
    "id": 1,
    "usuario_id": 1,
    "tipo_documento_id": 1,
    "numero_documento": "1234567890",
    "primer_nombre": "John",
    "segundo_nombre": "Michael",
    "primer_apellido": "Doe",
    "segundo_apellido": "Smith",
    "fecha_nacimiento": "1990-05-15",
    "genero": "masculino",
    "direccion_residencia": "Calle 123 #45-67",
    "ciudad": "Bogotá",
    "departamento": "Cundinamarca",
    "telefono_fijo": "1 2345678",
    "telefono_movil": "3001234567",
    "contacto_emergencia_nombre": "Jane Doe",
    "contacto_emergencia_telefono": "3009876543",
    "biografia": "Desarrollador de software",
    "created_at": "2026-04-19T10:30:00Z",
    "updated_at": "2026-04-19T10:30:00Z"
  },
  "message": "Perfil creado exitosamente"
}
```

**Response (200 OK) - Perfil actualizado:**
```json
{
  "request_id": "USR-1713623400014-b9c8d7e6",
  "status": "success",
  "statusCode": 200,
  "data": { /* ... mismo formato ... */ },
  "message": "Perfil actualizado exitosamente"
}
```

**Validaciones:**
- `fecha_nacimiento`: Usuario debe tener ≥ 14 años
- `genero`: Valores permitidos: `masculino`, `femenino`, `otro`, `prefiero_no_decir`
- `numero_documento`: Debe ser único en el sistema

---

## 📜 Historial de Estados

### 1. **Obtener Historial de Cambios de Estado**
**Endpoint:** `GET /users/{usuario_id}/state-history`  
**Permiso Requerido:** `USR_HISTORY_READ`  
**Requisito Funcional:** USR-RF-016  

**Response (200 OK):**
```json
{
  "request_id": "USR-1713623400015-f5g4h3i2",
  "status": "success",
  "statusCode": 200,
  "data": [
    {
      "id": 1,
      "usuario_id": 1,
      "estado_anterior": "activo",
      "estado_nuevo": "suspendido",
      "motivo": "Violación de términos de servicio",
      "usuario_modificador_id": 5,
      "created_at": "2026-04-19T11:00:00Z"
    },
    {
      "id": 2,
      "usuario_id": 1,
      "estado_anterior": "suspendido",
      "estado_nuevo": "activo",
      "motivo": "Apelación aprobada",
      "usuario_modificador_id": 7,
      "created_at": "2026-04-19T12:30:00Z"
    }
  ],
  "message": "Historial obtenido"
}
```

**Respuesta vacía:**
```json
{
  "request_id": "USR-1713623400016-p1q0r9s8",
  "status": "success",
  "statusCode": 200,
  "data": [],
  "message": "No hay historial de cambios para este usuario"
}
```

---

## 🔔 Preferencias de Notificación

### 1. **Obtener Preferencias de Notificación**
**Endpoint:** `GET /users/{usuario_id}/notification-preferences`  
**Permiso Requerido:** `USR_PREFERENCES_READ` (o token de ms-notificaciones)  
**Requisito Funcional:** USR-RF-018  

**Response (200 OK):**
```json
{
  "request_id": "USR-1713623400017-m9n8o7p6",
  "status": "success",
  "statusCode": 200,
  "data": {
    "id": 1,
    "usuario_id": 1,
    "notif_email": true,
    "notif_sms": false,
    "notif_push": true,
    "canal_preferido": "email",
    "horario_no_molestar_inicio": "22:00:00",
    "horario_no_molestar_fin": "08:00:00",
    "created_at": "2026-04-19T10:30:00Z",
    "updated_at": "2026-04-19T10:30:00Z"
  },
  "message": "Preferencias de notificación obtenidas"
}
```

---

### 2. **Actualizar Preferencias de Notificación**
**Endpoint:** `PUT /users/{usuario_id}/notification-preferences`  
**Permiso Requerido:** `USR_PREFERENCES_UPDATE`  
**Requisito Funcional:** USR-RF-019  
**Nota:** Todos los campos son opcionales  

**Request:**
```json
{
  "notif_email": true,
  "notif_sms": false,
  "notif_push": true,
  "canal_preferido": "email",
  "horario_no_molestar_inicio": "22:00",
  "horario_no_molestar_fin": "08:00"
}
```

**Response (200 OK):**
```json
{
  "request_id": "USR-1713623400018-i7j6k5l4",
  "status": "success",
  "statusCode": 200,
  "data": {
    "id": 1,
    "usuario_id": 1,
    "notif_email": true,
    "notif_sms": false,
    "notif_push": true,
    "canal_preferido": "email",
    "horario_no_molestar_inicio": "22:00:00",
    "horario_no_molestar_fin": "08:00:00",
    "created_at": "2026-04-19T10:30:00Z",
    "updated_at": "2026-04-19T12:45:00Z"
  },
  "message": "Preferencias actualizadas exitosamente"
}
```

**Validaciones:**
- `canal_preferido`: Valores permitidos: `email`, `sms`, `push`
- Horarios: Si se proporciona `horario_no_molestar_inicio`, debe proporcionarse `horario_no_molestar_fin`
- Horarios: `inicio < fin` (no pueden ser iguales)

---

## 📋 Tipos de Documento

### 1. **Listar Tipos de Documento Activos**
**Endpoint:** `GET /document-types`  
**Permiso Requerido:** `USR_READ`  
**Requisito Funcional:** USR-RF-017  
**Nota:** Solo retorna tipos de documento marcados como activos  

**Response (200 OK):**
```json
{
  "request_id": "USR-1713623400019-e3f2g1h0",
  "status": "success",
  "statusCode": 200,
  "data": [
    {
      "id": 1,
      "codigo": "CC",
      "nombre": "Cédula de Ciudadanía",
      "descripcion": "Documento nacional de identidad en Colombia"
    },
    {
      "id": 2,
      "codigo": "PA",
      "nombre": "Pasaporte",
      "descripcion": "Documento de viaje internacional"
    },
    {
      "id": 3,
      "codigo": "CE",
      "nombre": "Cédula de Extranjería",
      "descripcion": "Documento para residentes extranjeros en Colombia"
    },
    {
      "id": 4,
      "codigo": "TI",
      "nombre": "Tarjeta de Identidad",
      "descripcion": "Documento de identidad para menores de edad"
    },
    {
      "id": 5,
      "codigo": "PEP",
      "nombre": "Permiso de Entrada y Permanencia",
      "descripcion": "Documento para extranjeros"
    },
    {
      "id": 6,
      "codigo": "NIT",
      "nombre": "Número de Identificación Tributaria",
      "descripcion": "Documento tributario"
    },
    {
      "id": 7,
      "codigo": "OTR",
      "nombre": "Otro",
      "descripcion": "Otros tipos de documentos"
    }
  ],
  "message": "Tipos de documento obtenidos"
}
```

---

## 🔒 Headers Requeridos

| Header | Requerido | Descripción |
|--------|-----------|-------------|
| `Authorization` | Sí* | Bearer token JWT: `Bearer {token}` |
| `X-Request-ID` | No | ID único para rastrear la solicitud |
| `X-App-Token` | Condicional | Token del servicio para validaciones especiales |

*No requerido para endpoints con token de servicios internos

---

## 📊 Códigos de Estado HTTP

| Código | Significado |
|--------|-------------|
| **200** | OK - Solicitud exitosa |
| **201** | Created - Recurso creado exitosamente |
| **400** | Bad Request - Datos inválidos |
| **401** | Unauthorized - No autenticado |
| **403** | Forbidden - Permiso insuficiente |
| **404** | Not Found - Recurso no encontrado |
| **409** | Conflict - Recurso duplicado o violación de integridad |
| **500** | Internal Server Error - Error del servidor |

---

## 🔐 Permisos Requeridos

| Permiso | Descripción | Rutas Asociadas |
|---------|-------------|-----------------|
| `USR_CREATE` | Crear nuevos usuarios | POST /users |
| `USR_READ` | Leer datos de usuarios | GET /users/{id}, GET /users/by-email/{email} |
| `USR_UPDATE` | Actualizar datos de usuarios | PUT /users/{id} |
| `USR_DELETE` | Eliminar/desactivar usuarios | DELETE /users/{id} |
| `USR_SEARCH` | Realizar búsquedas avanzadas | GET /users (con filtros) |
| `USR_PROFILE_READ` | Leer perfiles extendidos | GET /users/{id}/profile |
| `USR_PROFILE_UPDATE` | Actualizar perfiles | PUT /users/{id}/profile |
| `USR_HISTORY_READ` | Leer historial de estados | GET /users/{id}/state-history |
| `USR_CHANGE_STATE` | Cambiar estado de usuario | PATCH /users/{id}/state |
| `USR_REACTIVATE` | Reactivar usuarios | POST /users/{id}/reactivate |
| `USR_PREFERENCES_READ` | Leer preferencias | GET /users/{id}/notification-preferences |
| `USR_PREFERENCES_UPDATE` | Actualizar preferencias | PUT /users/{id}/notification-preferences |
| `USR_STATS_READ` | Ver estadísticas | GET /users/stats/by-state |
| `USR_LIST_BY_ROLE` | Listar por rol | GET /users/by-role/{rol_id} |
| `USR_ADMIN_PASSWORD` | Cambiar contraseña de otros | PATCH /users/{id}/password |

---

## 📋 Estructura de Respuesta Estándar

Todas las respuestas siguen este formato:

```json
{
  "request_id": "USR-{timestamp}-{8_random_chars}",
  "status": "success|error",
  "statusCode": 200,
  "data": {},
  "message": "Descripción del resultado"
}
```

---

## 🧪 Ejemplo de Flujo Completo

```
1. Crear usuario
   POST /users
   ↓
2. Obtener usuario creado
   GET /users/{usuario_id}
   ↓
3. Crear perfil extendido
   PUT /users/{usuario_id}/profile
   ↓
4. Actualizar preferencias de notificación
   PUT /users/{usuario_id}/notification-preferences
   ↓
5. Cambiar estado del usuario
   PATCH /users/{usuario_id}/state
   ↓
6. Ver historial de cambios
   GET /users/{usuario_id}/state-history
```

