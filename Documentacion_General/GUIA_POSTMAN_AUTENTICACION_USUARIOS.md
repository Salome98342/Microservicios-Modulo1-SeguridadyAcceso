# 📋 Guía real para Postman: Autenticación + Usuarios

Esta guía usa solo URLs que existen en el código actual y evita variables inventadas. Está pensada para una demo estable ante el docente.

## 1. Base URLs

- Autenticación: `http://localhost:8002`
- Usuarios: `http://localhost:8000`
- Roles: `http://localhost:8003` (solo si luego quieres probar permisos)

## 2. Variables mínimas de Postman

Crea un environment llamado `Microservicios Local` con estas variables:

| Variable | Valor |
|---|---|
| `auth_url` | `http://localhost:8002` |
| `usuarios_url` | `http://localhost:8000` |
| `token` | vacío |
| `request_id` | vacío |

## 3. Flujo de demo sin errores

### Paso 1. Health de autenticación

- Método: `GET`
- URL: `{{auth_url}}/api/v1/health`

### Paso 2. Health de usuarios

- Método: `GET`
- URL: `{{usuarios_url}}/api/v1/health`

### Paso 3. Login real en autenticación

- Método: `POST`
- URL: `{{auth_url}}/api/v1/auth/login`
- Headers: `Content-Type: application/json`
- Body:

```json
{
   "username": "admin",
   "encrypted_password": "enc_admin123",
   "ip": "127.0.0.1",
   "user_agent": "Postman"
}
```

### Script para guardar el token

Pégalo en la pestaña Tests de ese request:

```javascript
if (pm.response.code === 200) {
   const body = pm.response.json();
   pm.environment.set("token", body.access_token);
   pm.environment.set("request_id", "REQ-" + Date.now());
}
```

### Paso 4. Validar sesión

- Método: `POST`
- URL: `{{auth_url}}/api/v1/auth/session/validate`
- Headers: `Content-Type: application/json`
- Body:

```json
{
   "token": "{{token}}"
}
```

### Paso 5. Probar la conexión real Auth -> Usuarios

- Método: `POST`
- URL: `{{usuarios_url}}/internal/users/credentials/verify`
- Headers: `Content-Type: application/json`
- Body:

```json
{
   "username": "admin",
   "encrypted_password": "enc_admin123",
   "request_trace_id": "{{request_id}}"
}
```

Respuesta esperada:

```json
{
   "user_id": "1",
   "status": "ACTIVE"
}
```

### Paso 6. Logout

- Método: `POST`
- URL: `{{auth_url}}/api/v1/auth/logout`
- Headers:
   - `Authorization: Bearer {{token}}`
   - `X-Request-ID: {{request_id}}`

## 4. Rutas funcionales reales que sí existen

### Autenticación

- `GET /api/v1/health`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/session/validate`
- `POST /api/v1/auth/validate-session`
- `POST /api/v1/auth/logout`
- `POST /api/v1/app-tokens`
- `GET /api/v1/app-tokens`
- `PUT /api/v1/app-tokens/{token_id}`
- `DELETE /api/v1/app-tokens/{token_id}`
- `GET /api/v1/sessions`
- `POST /api/v1/sessions/{session_id}/force-close`
- `GET /api/v1/access-history`

### Usuarios

- `GET /api/v1/health`
- `GET /api/v1/users`
- `POST /api/v1/users`
- `GET /api/v1/users/{usuario_id}`
- `GET /api/v1/users/by-email/{email}`
- `PUT /api/v1/users/{usuario_id}`
- `DELETE /api/v1/users/{usuario_id}`
- `PATCH /api/v1/users/{usuario_id}/state`
- `POST /api/v1/users/{usuario_id}/reactivate`
- `GET /api/v1/users/{usuario_id}/validate`
- `GET /api/v1/users/by-role/{rol_id}`
- `GET /api/v1/users/stats/by-state`
- `PATCH /api/v1/users/{usuario_id}/password`
- `GET /api/v1/users/{usuario_id}/profile`
- `PUT /api/v1/users/{usuario_id}/profile`
- `GET /api/v1/users/{usuario_id}/state-history`
- `GET /api/v1/users/{usuario_id}/notification-preferences`
- `PUT /api/v1/users/{usuario_id}/notification-preferences`
- `GET /api/v1/document-types`
- `POST /internal/users/credentials/verify`

## 5. Qué no debes usar en la demo

- No uses `POST /api/v1/sesiones` porque no existe en el código actual.
- No uses `POST /api/v1/users/profiles` porque la ruta real es `PUT /api/v1/users/{usuario_id}/profile`.
- No uses `page` o `size` en usuarios; los parámetros reales son `pagina` e `items_por_pagina`.
- No uses `password` en login; usa `encrypted_password`.

## 6. Recomendación para Postman

Usa esta secuencia exacta para evitar errores:

1. `GET {{auth_url}}/api/v1/health`
2. `GET {{usuarios_url}}/api/v1/health`
3. `POST {{auth_url}}/api/v1/auth/login`
4. `POST {{auth_url}}/api/v1/auth/session/validate`
5. `POST {{usuarios_url}}/internal/users/credentials/verify`
6. `POST {{auth_url}}/api/v1/auth/logout`

Con eso demuestras claramente que autenticación y usuarios están conectados.
    console.warn("⚠️ Falta Header Authorization");
}

// Validar que la respuesta no sea 401
if (pm.response.code === 401) {
    console.error("✗ Token inválido o expirado. Ejecuta Login nuevamente");
    pm.environment.set("auth_token", "");
}

// Validar que hay Request-ID
if (!pm.request.headers.get("X-Request-ID")) {
    console.warn("⚠️ Falta Header X-Request-ID");
}
```

---

## 🚀 PASO 9: Ejecutar Colección Completa

**Collection Runner en Postman:**

1. Click en **Ejecutar** (Run Collection)
2. Seleccionar carpetas en orden:
   - ✅ AUTENTICACION (para obtener token)
   - ✅ USUARIOS (usa el token)
3. Configurar:
   - Environment: `Microservicios Local`
   - Iterations: 1
   - Delay: 500ms entre peticiones
4. Click **Run**

---

## 📊 ORDEN RECOMENDADO DE EJECUCIÓN

```
1. AUTENTICACION
   ├─ Health Check (verificar que está online)
   └─ Login (obtener token)

2. USUARIOS - Listar Tipos Documento
   └─ (No requiere autenticación, pero usa el entorno)

3. USUARIOS - Usuarios
   ├─ Crear Usuario (requiere token)
   ├─ Consultar Usuario por ID
   ├─ Búsqueda Avanzada
   └─ ... resto de operaciones

4. USUARIOS - Perfiles
   ├─ Obtener Perfil Extendido
   └─ Crear o Actualizar Perfil

5. USUARIOS - Historial
   └─ Obtener Historial de Cambios

6. USUARIOS - Preferencias
   ├─ Obtener Preferencias
   └─ Actualizar Preferencias

7. AUTENTICACION - Validate Session
   └─ (Verificar que el token sigue siendo válido)
```

---

## 📚 Resumen Rápido

| Paso | Acción |
|------|--------|
| 1 | Crear `base_url_auth` y `base_url_users` en Variables |
| 2 | Agregar carpeta "AUTENTICACION" con Login y Validate Session |
| 3 | Cambiar `{{base_url}}` → `{{base_url_users}}` en todas las URLs de Usuarios |
| 4 | Agregar Header `Authorization: Bearer {{auth_token}}` a peticiones de Usuarios |
| 5 | Ejecutar Login primero para obtener token |
| 6 | Luego ejecutar peticiones de Usuarios (usarán el token automáticamente) |

---

## ✅ Verificación Final

Después de configurar, ejecuta esto para verificar:

```
1. GET {{base_url_auth}}/health
   Respuesta: {"status":"ok"}

2. POST {{base_url_auth}}/auth/login
   Respuesta: {"token": "...", "token_type": "bearer"}

3. GET {{base_url_users}}/
   Headers: Authorization: Bearer {{auth_token}}
   Respuesta: {"service":"ms-usuarios [USR]", ...}
```

Si todos retornan 200, ¡está todo configurado correctamente! 🎉

---

## 🆘 Troubleshooting

| Problema | Solución |
|----------|----------|
| **401 Unauthorized** | Ejecuta Login en AUTENTICACION para obtener token fresco |
| **404 Not Found** | Verifica que `base_url_auth` y `base_url_users` sean correctas |
| **Variables no se guardan** | Verifica que hayas seleccionado el Environment correcto |
| **Petición devuelve 500** | Revisa los logs en las terminales de Docker |
| **No hay respuesta** | Verifica que Docker está corriendo: `docker ps` |

---

## ✅ Verificación Final

Después de configurar, ejecuta esto para verificar:

```
1. GET {{base_url_auth}}/health -> {"status":"ok"}
2. POST {{base_url_auth}}/auth/login -> {"token": "..."}
3. GET {{base_url_users}}/ -> Headers: Authorization: Bearer {{auth_token}} -> {"service":"ms-usuarios [USR]"}
```
