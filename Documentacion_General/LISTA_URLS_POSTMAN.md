# 🔗 URLs reales y funcionales para Postman

Estas son las rutas que sí existen en el código actual. Las separo por nivel para que Postman no vuelva a usar endpoints inventados.

## Base URLs

- Autenticación: `http://localhost:8002`
- Usuarios: `http://localhost:8000`
- Roles: `http://localhost:8003`

## 1. Autenticación

| Método | URL | Uso |
|---|---|---|
| GET | `http://localhost:8002/api/v1/health` | Health check |
| POST | `http://localhost:8002/api/v1/auth/login` | Login real |
| POST | `http://localhost:8002/api/v1/auth/session/validate` | Validar token |
| POST | `http://localhost:8002/api/v1/auth/validate-session` | Alias de validación |
| POST | `http://localhost:8002/api/v1/auth/logout` | Cerrar sesión |
| GET | `http://localhost:8002/api/v1/sessions` | Listar sesiones activas |
| POST | `http://localhost:8002/api/v1/sessions/{session_id}/force-close` | Cierre forzado |
| GET | `http://localhost:8002/api/v1/access-history` | Historial de accesos |

## 2. Usuarios

| Método | URL | Uso |
|---|---|---|
| GET | `http://localhost:8000/api/v1/health` | Health check |
| GET | `http://localhost:8000/api/v1/users` | Búsqueda/listado |
| POST | `http://localhost:8000/api/v1/users` | Crear usuario |
| GET | `http://localhost:8000/api/v1/users/{usuario_id}` | Consultar usuario |
| GET | `http://localhost:8000/api/v1/users/by-email/{email}` | Consultar por email |
| PUT | `http://localhost:8000/api/v1/users/{usuario_id}` | Actualizar usuario |
| DELETE | `http://localhost:8000/api/v1/users/{usuario_id}` | Desactivar usuario |
| PATCH | `http://localhost:8000/api/v1/users/{usuario_id}/state` | Cambiar estado |
| POST | `http://localhost:8000/api/v1/users/{usuario_id}/reactivate` | Reactivar usuario |
| GET | `http://localhost:8000/api/v1/users/{usuario_id}/validate` | Validación interna |
| GET | `http://localhost:8000/api/v1/users/by-role/{rol_id}` | Listar por rol |
| GET | `http://localhost:8000/api/v1/users/stats/by-state` | Estadísticas |
| PATCH | `http://localhost:8000/api/v1/users/{usuario_id}/password` | Cambiar contraseña |
| GET | `http://localhost:8000/api/v1/users/{usuario_id}/profile` | Ver perfil |
| PUT | `http://localhost:8000/api/v1/users/{usuario_id}/profile` | Crear/actualizar perfil |
| GET | `http://localhost:8000/api/v1/users/{usuario_id}/state-history` | Historial de estados |
| GET | `http://localhost:8000/api/v1/users/{usuario_id}/notification-preferences` | Ver preferencias |
| PUT | `http://localhost:8000/api/v1/users/{usuario_id}/notification-preferences` | Actualizar preferencias |
| GET | `http://localhost:8000/api/v1/document-types` | Listar tipos de documento |
| POST | `http://localhost:8000/internal/users/credentials/verify` | Verificación interna para auth |

## 3. Roles

| Método | URL | Uso |
|---|---|---|
| GET | `http://localhost:8003/api/v1/health` | Health check |
| GET | `http://localhost:8003/api/v1/validacion/permiso?rol=1&permiso=USR_READ` | Validar permiso de rol |
| GET | `http://localhost:8003/api/v1/validacion/rol?rol=1` | Validar existencia de rol |

## 4. Parametría real que sí usa el código

- En `users`, la búsqueda usa `nombre`, `numero_documento`, `email`, `estado`, `ciudad`, `pagina`, `items_por_pagina`.
- No uses `page` ni `size`.
- En login de autenticación, usa `encrypted_password`.
- No uses `POST /api/v1/sesiones`; en el código actual el login real es `POST /api/v1/auth/login`.
- No uses `POST /api/v1/users/profiles`; la ruta real es `PUT /api/v1/users/{usuario_id}/profile`.

## 5. Flujo mínimo para demo

1. `GET http://localhost:8002/api/v1/health`
2. `GET http://localhost:8000/api/v1/health`
3. `POST http://localhost:8002/api/v1/auth/login`
4. `POST http://localhost:8002/api/v1/auth/session/validate`
5. `POST http://localhost:8000/internal/users/credentials/verify`
6. `POST http://localhost:8002/api/v1/auth/logout`

## 6. Cuerpos reales de ejemplo

### Login

```json
{
  "username": "admin",
  "encrypted_password": "enc_admin123",
  "ip": "127.0.0.1",
  "user_agent": "Postman"
}
```

### Validar sesión

```json
{
  "token": "{{token}}"
}
```

### Verificación interna de usuarios

```json
{
  "username": "admin",
  "encrypted_password": "enc_admin123",
  "request_trace_id": "REQ-123"
}
```
