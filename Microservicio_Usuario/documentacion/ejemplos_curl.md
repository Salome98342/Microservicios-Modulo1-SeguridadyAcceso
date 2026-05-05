# 🧪 Ejemplos de Requests - Colección cURL

## 🎯 Base URL
```
http://localhost:8000/api/v1
```

## 📌 Variables Globales

```bash
# Almacenar estas variables para usar en los requests
export BASE_URL="http://localhost:8000/api/v1"
export TOKEN="Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
export REQUEST_ID="USR-$(date +%s)-$(openssl rand -hex 4)"
```

---

## 👥 Endpoints de USUARIOS

### 1. Crear Usuario

```bash
curl -X POST "${BASE_URL}/users" \
  -H "Authorization: ${TOKEN}" \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: ${REQUEST_ID}" \
  -d '{
    "username": "carlos.lopez",
    "email": "carlos.lopez@example.com",
    "password_encrypted": "AQIDBA==",
    "rol_id": 2
  }' | jq
```

**Respuesta esperada (201 Created):**
```json
{
  "request_id": "USR-1713623400000-a1b2c3d4",
  "status": "success",
  "statusCode": 201,
  "data": {
    "id": 1,
    "username": "carlos.lopez",
    "email": "carlos.lopez@example.com",
    "estado": "activo",
    "rol_id": 2,
    "created_at": "2026-04-19T10:30:00Z",
    "updated_at": "2026-04-19T10:30:00Z"
  },
  "message": "Usuario creado exitosamente"
}
```

---

### 2. Obtener Usuario por ID

```bash
curl -X GET "${BASE_URL}/users/1" \
  -H "Authorization: ${TOKEN}" \
  -H "X-Request-ID: ${REQUEST_ID}" | jq
```

**Respuesta esperada (200 OK):**
```json
{
  "request_id": "USR-1713623400001-x9y8z7w6",
  "status": "success",
  "statusCode": 200,
  "data": {
    "id": 1,
    "username": "carlos.lopez",
    "email": "carlos.lopez@example.com",
    "estado": "activo",
    "rol_id": 2,
    "created_at": "2026-04-19T10:30:00Z",
    "updated_at": "2026-04-19T10:30:00Z"
  },
  "message": "Usuario encontrado"
}
```

---

### 3. Obtener Usuario por Email

```bash
curl -X GET "${BASE_URL}/users/by-email/carlos.lopez@example.com" \
  -H "Authorization: ${TOKEN}" \
  -H "X-Request-ID: ${REQUEST_ID}" | jq
```

---

### 4. Búsqueda Avanzada (Sin Filtros)

```bash
curl -X GET "${BASE_URL}/users?pagina=1&items_por_pagina=10" \
  -H "Authorization: ${TOKEN}" \
  -H "X-Request-ID: ${REQUEST_ID}" | jq
```

---

### 5. Búsqueda Avanzada (Con Filtros)

```bash
curl -X GET "${BASE_URL}/users?nombre=carlos&ciudad=Bogota&estado=activo&pagina=1&items_por_pagina=10" \
  -H "Authorization: ${TOKEN}" \
  -H "X-Request-ID: ${REQUEST_ID}" | jq
```

**Parámetros disponibles:**
- `nombre` - Busca en primer_nombre y primer_apellido
- `numero_documento` - Búsqueda exacta
- `email` - Búsqueda exacta
- `estado` - Valores: activo, inactivo, suspendido, eliminado
- `ciudad` - Busca en ciudad del perfil
- `pagina` - Número de página (default: 1)
- `items_por_pagina` - Registros por página (default: 10, máx: 100)

---

### 6. Actualizar Usuario

```bash
curl -X PUT "${BASE_URL}/users/1" \
  -H "Authorization: ${TOKEN}" \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: ${REQUEST_ID}" \
  -d '{
    "username": "carlos.lopez.updated",
    "email": "carlos.new@example.com",
    "rol_id": 3
  }' | jq
```

---

### 7. Desactivar Usuario (Soft Delete)

```bash
curl -X DELETE "${BASE_URL}/users/1" \
  -H "Authorization: ${TOKEN}" \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: ${REQUEST_ID}" \
  -d '{
    "motivo": "Usuario solicita desactivación de cuenta"
  }' | jq
```

---

### 8. Cambiar Estado

```bash
curl -X PATCH "${BASE_URL}/users/1/state" \
  -H "Authorization: ${TOKEN}" \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: ${REQUEST_ID}" \
  -d '{
    "estado_nuevo": "suspendido",
    "motivo": "Violación de términos de servicio"
  }' | jq
```

**Estados válidos:** `activo`, `inactivo`, `suspendido`, `eliminado`

---

### 9. Reactivar Usuario

```bash
curl -X POST "${BASE_URL}/users/1/reactivate" \
  -H "Authorization: ${TOKEN}" \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: ${REQUEST_ID}" \
  -d '{
    "motivo": "El usuario apeló y fue aprobado"
  }' | jq
```

---

### 10. Validar Existencia de Usuario

```bash
curl -X GET "${BASE_URL}/users/1/validate" \
  -H "X-Request-ID: ${REQUEST_ID}" | jq
```

**Respuesta esperada (200 OK):**
```json
{
  "request_id": "USR-1713623400008-j6k5l4m3",
  "status": "success",
  "statusCode": 200,
  "data": {
    "existe": true,
    "usuario_id": 1,
    "username": "carlos.lopez",
    "estado": "activo"
  },
  "message": "Validación completada"
}
```

---

### 11. Listar Usuarios por Rol

```bash
curl -X GET "${BASE_URL}/users/by-role/2?pagina=1&items_por_pagina=10" \
  -H "Authorization: ${TOKEN}" \
  -H "X-Request-ID: ${REQUEST_ID}" | jq
```

**Parámetros opcionales:**
- `estado` - Filtrar por estado
- `pagina` - Número de página
- `items_por_pagina` - Registros por página

---

### 12. Obtener Estadísticas

```bash
curl -X GET "${BASE_URL}/users/stats/by-state" \
  -H "Authorization: ${TOKEN}" \
  -H "X-Request-ID: ${REQUEST_ID}" | jq
```

**Respuesta esperada (200 OK):**
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

### 13. Cambiar Contraseña

```bash
curl -X PATCH "${BASE_URL}/users/1/password" \
  -H "Authorization: ${TOKEN}" \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: ${REQUEST_ID}" \
  -d '{
    "password_actual_encrypted": "AQIDBA==",
    "password_nueva_encrypted": "BQYHCSI=="
  }' | jq
```

---

## 👤 Endpoints de PERFILES

### 1. Obtener Perfil

```bash
curl -X GET "${BASE_URL}/users/1/profile" \
  -H "Authorization: ${TOKEN}" \
  -H "X-Request-ID: ${REQUEST_ID}" | jq
```

---

### 2. Crear o Actualizar Perfil

```bash
curl -X PUT "${BASE_URL}/users/1/profile" \
  -H "Authorization: ${TOKEN}" \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: ${REQUEST_ID}" \
  -d '{
    "tipo_documento_id": 1,
    "numero_documento": "1234567890",
    "primer_nombre": "Carlos",
    "segundo_nombre": "Alberto",
    "primer_apellido": "López",
    "segundo_apellido": "García",
    "fecha_nacimiento": "1990-05-15",
    "genero": "masculino",
    "direccion_residencia": "Calle 123 #45-67, Apto 202",
    "ciudad": "Bogotá",
    "departamento": "Cundinamarca",
    "telefono_fijo": "1 2345678",
    "telefono_movil": "3001234567",
    "contacto_emergencia_nombre": "Ana López",
    "contacto_emergencia_telefono": "3009876543",
    "biografia": "Ingeniero de software con 5 años de experiencia en desarrollo backend"
  }' | jq
```

**Validaciones:**
- Edad mínima: 14 años (basado en fecha_nacimiento)
- Género: `masculino`, `femenino`, `otro`, `prefiero_no_decir`
- numero_documento debe ser único

---

## 📜 Endpoints de HISTORIAL

### 1. Obtener Historial de Cambios de Estado

```bash
curl -X GET "${BASE_URL}/users/1/state-history" \
  -H "Authorization: ${TOKEN}" \
  -H "X-Request-ID: ${REQUEST_ID}" | jq
```

**Respuesta esperada (200 OK):**
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
    }
  ],
  "message": "Historial obtenido"
}
```

---

## 🔔 Endpoints de PREFERENCIAS DE NOTIFICACIÓN

### 1. Obtener Preferencias

```bash
curl -X GET "${BASE_URL}/users/1/notification-preferences" \
  -H "Authorization: ${TOKEN}" \
  -H "X-Request-ID: ${REQUEST_ID}" | jq
```

---

### 2. Actualizar Preferencias

```bash
curl -X PUT "${BASE_URL}/users/1/notification-preferences" \
  -H "Authorization: ${TOKEN}" \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: ${REQUEST_ID}" \
  -d '{
    "notif_email": true,
    "notif_sms": false,
    "notif_push": true,
    "canal_preferido": "email",
    "horario_no_molestar_inicio": "22:00",
    "horario_no_molestar_fin": "08:00"
  }' | jq
```

**Notas:**
- `canal_preferido`: `email`, `sms`, `push`
- Si proporcionas `horario_no_molestar_inicio`, debes proporcionar `horario_no_molestar_fin`
- `inicio < fin` (no pueden ser iguales)

---

## 📋 Endpoints de TIPOS DE DOCUMENTO

### 1. Listar Tipos de Documento

```bash
curl -X GET "${BASE_URL}/document-types" \
  -H "Authorization: ${TOKEN}" \
  -H "X-Request-ID: ${REQUEST_ID}" | jq
```

**Respuesta esperada (200 OK):**
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
    }
  ],
  "message": "Tipos de documento obtenidos"
}
```

---

## 🔧 Comandos Útiles

### Guardar respuesta en archivo

```bash
curl -X GET "${BASE_URL}/users/1" \
  -H "Authorization: ${TOKEN}" \
  -H "X-Request-ID: ${REQUEST_ID}" \
  -o response.json
```

### Ver headers de respuesta

```bash
curl -X GET "${BASE_URL}/users/1" \
  -H "Authorization: ${TOKEN}" \
  -i
```

### Medir tiempo de respuesta

```bash
curl -X GET "${BASE_URL}/users/1" \
  -H "Authorization: ${TOKEN}" \
  -w "\nTiempo total: %{time_total}s\n"
```

### Usar variables de entorno

```bash
# Definir en .env local
TOKEN="tu_token_aqui"
USUARIO_ID=1

curl -X GET "${BASE_URL}/users/${USUARIO_ID}" \
  -H "Authorization: Bearer ${TOKEN}"
```

### Formatear JSON con jq

```bash
# Pretty print
curl -X GET "${BASE_URL}/users/1" \
  -H "Authorization: ${TOKEN}" | jq

# Extraer campo específico
curl -X GET "${BASE_URL}/users/1" \
  -H "Authorization: ${TOKEN}" | jq '.data.username'

# Filtrar array
curl -X GET "${BASE_URL}/users?pagina=1" \
  -H "Authorization: ${TOKEN}" | jq '.data.resultados[] | select(.estado=="activo")'
```

---

## 📊 Scenarios de Prueba

### Scenario 1: Flujo Completo de Usuario

```bash
# 1. Crear usuario
USUARIO=$(curl -s -X POST "${BASE_URL}/users" \
  -H "Authorization: ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test.user",
    "email": "test@example.com",
    "password_encrypted": "AQIDBA==",
    "rol_id": 2
  }')

# Extraer ID del usuario creado
USUARIO_ID=$(echo $USUARIO | jq '.data.id')

# 2. Obtener usuario
curl -s -X GET "${BASE_URL}/users/${USUARIO_ID}" \
  -H "Authorization: ${TOKEN}" | jq

# 3. Actualizar usuario
curl -s -X PUT "${BASE_URL}/users/${USUARIO_ID}" \
  -H "Authorization: ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test.user.updated"
  }' | jq

# 4. Crear perfil
curl -s -X PUT "${BASE_URL}/users/${USUARIO_ID}/profile" \
  -H "Authorization: ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_documento_id": 1,
    "numero_documento": "9876543210",
    "primer_nombre": "Test",
    "primer_apellido": "User",
    "fecha_nacimiento": "1990-01-01",
    "genero": "otro",
    "ciudad": "Bogotá",
    "departamento": "Cundinamarca",
    "telefono_movil": "3001234567",
    "contacto_emergencia_nombre": "Contact",
    "contacto_emergencia_telefono": "3009876543"
  }' | jq

# 5. Ver historial
curl -s -X GET "${BASE_URL}/users/${USUARIO_ID}/state-history" \
  -H "Authorization: ${TOKEN}" | jq
```

---

## ⚠️ Códigos de Error Comunes

| Código | Significa | Causa |
|--------|-----------|-------|
| 400 | Bad Request | Datos inválidos o incompletos |
| 401 | Unauthorized | Token ausente o expirado |
| 403 | Forbidden | Permiso insuficiente |
| 404 | Not Found | Usuario/recurso no existe |
| 409 | Conflict | Datos duplicados (email, username, documento) |
| 500 | Internal Server Error | Error del servidor |

---

## 🎓 Tips para Testing

1. **Guardar tokens en archivo temporal:**
   ```bash
   echo "Bearer $TOKEN" > token.txt
   TOKEN=$(cat token.txt | cut -d' ' -f2)
   ```

2. **Crear script de prueba:**
   ```bash
   #!/bin/bash
   source .env
   curl -X GET "${BASE_URL}/users/1" \
     -H "Authorization: Bearer ${TOKEN}"
   ```

3. **Usar Postman/Insomnia:**
   - Importar colección: `requests.postman_collection.json`
   - Configurar variables: `{{BASE_URL}}`, `{{TOKEN}}`
   - Ejecutar secuencias de requests

---

**¡Happy Testing! 🚀**

