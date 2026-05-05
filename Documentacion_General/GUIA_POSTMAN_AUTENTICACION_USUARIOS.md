# 📋 GUÍA: Configurar Postman con Autenticación + Usuarios Conectados

## 🎯 Objetivo

Configurar Postman para hacer peticiones a los 2 microservicios conectados:
- **Autenticación** (http://localhost:8002)
- **Usuarios** (http://localhost:8000)

Con **flujo de autenticación automático**: Login → Token → Usar en peticiones de Usuarios.

---

## 📁 PASO 1: Crear Estructura de Carpetas en Postman

Tu colección debe quedar así:

```
Microservicios
├── 📁 AUTENTICACION
│   ├── Login
│   ├── Validate Session
│   ├── Refresh Token
│   ├── Logout
│   └── Health Check
│
├── 📁 USUARIOS
│   ├── 📁 Usuarios
│   │   ├── Crear Usuario
│   │   ├── Consultar Usuario por ID
│   │   ├── Consultar por Email
│   │   └── ... (tus 12 peticiones)
│   ├── 📁 Perfiles
│   │   ├── Obtener Perfil Extendido
│   │   └── Crear o Actualizar Perfil
│   ├── 📁 Historial
│   │   └── Obtener Historial de Estados
│   ├── 📁 Preferencias
│   │   ├── Obtener Preferencias
│   │   └── Actualizar Preferencias
│   └── 📁 Tipos Documento
│       └── Listar Tipos de Documento
│
└── 📁 VARIABLES Y CONFIGURACIÓN
    ├── Variables de Entorno
    ├── Pre-request Scripts
    └── Tests Globales
```

---

## 🔧 PASO 2: Variables de Entorno

**En Postman: Settings → Environments → New Environment**

Nombre: `Microservicios Local`

| Variable | Valor | Descripción |
|----------|-------|-------------|
| `base_url_auth` | `http://localhost:8002/api/v1` | URL de Autenticación |
| `base_url_users` | `http://localhost:8000/api/v1` | URL de Usuarios |
| `auth_token` | `` | (Se llena automáticamente tras login) |
| `username_admin` | `admin` | Credencial para login |
| `password_admin` | `admin` | Credencial para login |
| `request_id` | `` | ID único para cada petición |

---

## 🔐 PASO 3: Carpeta AUTENTICACION - Endpoints

### 1️⃣ **Login** (Obtener Token)

```
Método: POST
URL: {{base_url_auth}}/auth/login

Headers:
  Content-Type: application/json

Body (raw - JSON):
{
  "username": "{{username_admin}}",
  "password": "{{password_admin}}"
}

Response esperada:
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Tests (Script post-response):**
```javascript
if (pm.response.code === 200) {
    var jsonData = pm.response.json();
    pm.environment.set("auth_token", jsonData.token);
    console.log("✓ Token guardado: " + jsonData.token.substring(0, 20) + "...");
} else {
    console.log("✗ Error en login: " + pm.response.code);
}
```

---

### 2️⃣ **Validate Session** (Verificar Token)

```
Método: POST
URL: {{base_url_auth}}/auth/validate-session

Headers:
  Content-Type: application/json
  Authorization: Bearer {{auth_token}}

Body (raw - JSON):
{
  "token": "{{auth_token}}"
}

Response esperada:
{
  "data": {
    "valid": true,
    "user_id": 1,
    "rol_id": 1
  }
}
```

---

### 3️⃣ **Health Check**

```
Método: GET
URL: {{base_url_auth}}/health

Response esperada:
{
  "status": "ok"
}
```

---

## 👥 PASO 4: Editar Carpeta USUARIOS

### **IMPORTANTE: Cambiar Variable en Todos los Endpoints**

**Antes:**
```
{{base_url}}/users
```

**Después:**
```
{{base_url_users}}/users
```

### **Agregar Autorización a Todas las Peticiones**

En cada petición de Usuarios:

**Headers:**
```
Authorization: Bearer {{auth_token}}
X-Request-ID: {{$timestamp}}
Content-Type: application/json
```

---

## ⚙️ PASO 5: Pre-request Script Global

Para generar Request ID automático en cada petición.

**En Postman: Colección → Pre-request Scripts**

```javascript
// Generar timestamp para Request-ID
pm.environment.set("request_id", "REQ-" + Date.now() + "-" + Math.random().toString(36).substr(2, 9));

// Verificar si el token existe
if (!pm.environment.get("auth_token")) {
    console.warn("⚠️ No hay token. Ejecuta Login primero en la carpeta AUTENTICACION");
}
```

---

## 🔄 PASO 6: Flujo de Pruebas Completo

### **Primera vez:**

1. **Ejecutar: Login** (carpeta AUTENTICACION)
   - Obtiene el token y lo guarda automáticamente
   
2. **Ejecutar: Validate Session** (carpeta AUTENTICACION)
   - Verifica que el token es válido
   
3. **Ejecutar: Cualquier petición de USUARIOS**
   - Usará el token guardado automáticamente

### **Cada vez que expire el token (~1 hora):**
1. Vuelve a ejecutar **Login**
2. Se puede volver a usar cualquier petición de Usuarios

---

## 📝 PASO 7: Ejemplos de Peticiones de USUARIOS (Con Token)

### **Crear Usuario**
```
Método: POST
URL: {{base_url_users}}/users

Headers:
  Authorization: Bearer {{auth_token}}
  X-Request-ID: {{request_id}}
  Content-Type: application/json

Body (raw - JSON):
{
  "username": "juan.perez",
  "email": "juan@example.com",
  "password_encrypted": "base64_encrypted_password",
  "rol_id": 1
}
```

### **Consultar Usuario por ID**
```
Método: GET
URL: {{base_url_users}}/users/1

Headers:
  Authorization: Bearer {{auth_token}}
  X-Request-ID: {{request_id}}
```

### **Búsqueda Avanzada con Filtros**
```
Método: GET
URL: {{base_url_users}}/users?nombre=juan&estado=activo&pagina=1&items_por_pagina=10

Headers:
  Authorization: Bearer {{auth_token}}
  X-Request-ID: {{request_id}}
```

---

## 🧪 PASO 8: Tests Globales para Validación

**En Postman: Colección → Tests**

```javascript
// Validar que todas las peticiones tienen token
if (!pm.request.headers.get("Authorization")) {
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
