# 🔗 Lista Completa de URLs - Autenticación & Usuarios

## 📡 BASE URLs

```
Autenticación:  http://localhost:8002/api/v1
Usuarios:       http://localhost:8000/api/v1
```
                                                                                          
---

## 🔐 CARPETA: AUTENTICACION

| # | Nombre | Método | URL Completa |
|---|--------|--------|-------------|
| 1 | **Health Check** | GET | `http://localhost:8002/health` |
| 2 | **Login** | POST | `http://localhost:8002/v1/auth/login` |
| 3 | **Validate Session** | POST | `http://localhost:8002/v1/auth/session/validate` |
| 4 | **Logout** | POST | `http://localhost:8002/v1/auth/logout` |
| 5 | **Listar Sesiones** | GET | `http://localhost:8002/v1/sessions` |

---

## 👥 CARPETA: USUARIOS

### 📁 Sub-carpeta: Usuarios (CRUD)

| # | Nombre | Método | URL Completa | Headers Requeridos |
|---|--------|--------|-------------|-------------------|
| 6 | **Crear Usuario** | POST | `http://localhost:8000/api/v1/users` | `Authorization: Bearer <token>` |
| 7 | **Listar Usuarios (Búsqueda)** | GET | `http://localhost:8000/api/v1/users` | `Authorization: Bearer <token>` |
| 8 | **Consultar Usuario por ID** | GET | `http://localhost:8000/api/v1/users/{usuario_id}` | `Authorization: Bearer <token>` |
| 9 | **Consultar por Email** | GET | `http://localhost:8000/api/v1/users/by-email/{email}` | `Authorization: Bearer <token>` |
| 10 | **Actualizar Usuario** | PUT | `http://localhost:8000/api/v1/users/{usuario_id}` | `Authorization: Bearer <token>` |
| 11 | **Desactivar Usuario** | DELETE | `http://localhost:8000/api/v1/users/{usuario_id}` | `Authorization: Bearer <token>` |
| 12 | **Cambiar Estado** | PATCH | `http://localhost:8000/api/v1/users/{usuario_id}/state` | `Authorization: Bearer <token>` |
| 13 | **Reactivar Usuario** | POST | `http://localhost:8000/api/v1/users/{usuario_id}/reactivate` | `Authorization: Bearer <token>` |
| 14 | **Validar Existencia** | GET | `http://localhost:8000/api/v1/users/{usuario_id}/validate` | `Authorization: Bearer <token>` |
| 15 | **Listar por Rol** | GET | `http://localhost:8000/api/v1/users/by-role/{rol_id}` | `Authorization: Bearer <token>` |
| 16 | **Estadísticas por Estado** | GET | `http://localhost:8000/api/v1/users/stats/by-state` | `Authorization: Bearer <token>` |
| 17 | **Cambiar Contraseña** | PATCH | `http://localhost:8000/api/v1/users/{usuario_id}/password` | `Authorization: Bearer <token>` |

---

### 📁 Sub-carpeta: Perfiles

| # | Nombre | Método | URL Completa | Headers Requeridos |
|---|--------|--------|-------------|-------------------|
| 18 | **Obtener Perfil Extendido** | GET | `http://localhost:8000/api/v1/users/{usuario_id}/profile` | `Authorization: Bearer <token>` |
| 19 | **Crear/Actualizar Perfil** | PUT | `http://localhost:8000/api/v1/users/{usuario_id}/profile` | `Authorization: Bearer <token>` |

---

### 📁 Sub-carpeta: Historial

| # | Nombre | Método | URL Completa | Headers Requeridos |
|---|--------|--------|-------------|-------------------|
| 20 | **Obtener Historial de Estados** | GET | `http://localhost:8000/api/v1/users/{usuario_id}/state-history` | `Authorization: Bearer <token>` |

---

### 📁 Sub-carpeta: Preferencias

| # | Nombre | Método | URL Completa | Headers Requeridos |
|---|--------|--------|-------------|-------------------|
| 21 | **Obtener Preferencias** | GET | `http://localhost:8000/api/v1/users/{usuario_id}/notification-preferences` | `Authorization: Bearer <token>` |
| 22 | **Actualizar Preferencias** | PUT | `http://localhost:8000/api/v1/users/{usuario_id}/notification-preferences` | `Authorization: Bearer <token>` |

---

### 📁 Sub-carpeta: Tipos Documento

| # | Nombre | Método | URL Completa | Headers Requeridos |
|---|--------|--------|-------------|-------------------|
| 23 | **Listar Tipos de Documento** | GET | `http://localhost:8000/api/v1/document-types` | *(sin requerimiento)* |

---

## 📋 HEADERS ESTÁNDAR

Todas las peticiones deben incluir:

```
Content-Type: application/json
X-Request-ID: (cualquier valor único)
```

Y para peticiones que requieren autenticación:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 🔄 FLUJO RECOMENDADO EN POSTMAN

### **Paso 1: Obtener Token**
```
POST http://localhost:8002/v1/auth/login

Body (JSON):
{
  "username": "admin",
  "password": "admin"
}

Response:
{
  "token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**→ Copiar el `token` de la respuesta**

---

### **Paso 2: Usar el Token en Usuarios**

En cada petición de Usuarios, en los Headers:
```
Authorization: Bearer <PEGA_EL_TOKEN_AQUI>
```

Ejemplo:
```
GET http://localhost:8000/api/v1/users

Headers:
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJyb2xfaWQiOjEsInN1YiI6ImFkbWluIn0...
  Content-Type: application/json
```

---

## ✅ URLs Copiables (Para pegar directo en Postman)

### **AUTENTICACION**
```
http://localhost:8002/health
http://localhost:8002/v1/auth/login
http://localhost:8002/v1/auth/session/validate
http://localhost:8002/v1/auth/logout
http://localhost:8002/v1/sessions
```

### **USUARIOS - Usuarios**
```
http://localhost:8000/api/v1/users
http://localhost:8000/api/v1/users/1
http://localhost:8000/api/v1/users/by-email/user@example.com
http://localhost:8000/api/v1/users/1/validate
http://localhost:8000/api/v1/users/by-role/1
http://localhost:8000/api/v1/users/stats/by-state
http://localhost:8000/api/v1/users/1/state
http://localhost:8000/api/v1/users/1/password
http://localhost:8000/api/v1/users/1/reactivate
```

### **USUARIOS - Perfiles**
```
http://localhost:8000/api/v1/users/1/profile
```

### **USUARIOS - Historial**
```
http://localhost:8000/api/v1/users/1/state-history
```

### **USUARIOS - Preferencias**
```
http://localhost:8000/api/v1/users/1/notification-preferences
```

### **USUARIOS - Tipos Documento**
```
http://localhost:8000/api/v1/document-types
```

---

## 💡 NOTAS IMPORTANTES

- Reemplaza `{usuario_id}` con un ID real (ej: `1`, `2`, `3`)
- Reemplaza `{email}` con un email real (ej: `admin@example.com`)
- Reemplaza `{rol_id}` con un ID de rol (ej: `1`)
- El token JWT expira en **3600 segundos (1 hora)**
- Si obtienes `401 Unauthorized`, vuelve a hacer login

---

## 🧪 Test Rápido (Sin Variables)

1. **Abre Postman**
2. **Nueva petición → POST**
3. **Pega esta URL:**
   ```
   http://localhost:8002/api/v1/auth/login
   ```
4. **Body → raw → JSON:**
   ```json
   {
     "username": "admin",
     "password": "admin"
   }
   ```
5. **Click "Send"**
6. **Copia el token de la respuesta**
7. **Nueva petición → GET**
8. **Pega esta URL:**
   ```
   http://localhost:8000/api/v1/users
   ```
9. **Headers → Agrega:**
   - Key: `Authorization`
   - Value: `Bearer <PEGA_EL_TOKEN_AQUI>`
10. **Click "Send"**

Si obtienes respuesta, ¡todo funciona! ✅
