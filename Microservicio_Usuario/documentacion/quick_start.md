# ⚡ Quick Start Guide - MS-Usuarios

## 5 Minutos para Empezar

### 1️⃣ Instalación (2 minutos)

```bash
# 1. Navegar al directorio
cd Microservicio_Usuario

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Verificar instalación
pip show fastapi uvicorn psycopg2-binary
```

✅ Si no hay errores, las dependencias están instaladas

---

# 2. Configuración de Base de Datos (2 minutos)

```bash
# 1. Abrir PostgreSQL
psql -U postgres

# 2. Ejecutar script (copiar y pegar todo el contenido de ms_usuario/init_db.sql)
# O si guardaste como archivo:
# psql -U postgres -f ms_usuario/init_db.sql

# 3. Verificar creación
psql -U db_usuarios -c "SELECT * FROM usr_tipos_documento LIMIT 1;"
```

✅ Deberías ver 1 fila con los tipos de documento

---

### 3️⃣ Configurar .env (1 minuto)

Editar el archivo `.env` con tus valores:

```env
# Base de datos
DB_HOST=localhost
DB_PORT=5432
DB_NAME=db_usuarios
DB_USER=postgres
DB_PASSWORD=tu_contraseña_postgres

# Generar AES_SECRET_KEY (solo 1 vez):
# python -c "import secrets; print(secrets.token_hex(32))"
AES_SECRET_KEY=<pega_aqui_64_caracteres_hex>

# Los demás valores pueden ser placeholders por ahora
BCRYPT_ROUNDS=12
USR_APP_TOKEN=token_temporal
AUTH_APP_TOKEN=token_temporal
# ... etc
```

✅ Guardas el archivo

---

### 4️⃣ Iniciar Servidor (1 minuto)

```bash
# Abrir PowerShell en el directorio Microservicio_Usuario
cd C:\Users\User\OneDrive\Escritorio\ms_usuario\Microservicio_Usuario

# Ejecutar servidor
python -m uvicorn main:app --reload --port 8000
```

**Deberías ver:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

✅ El servidor está corriendo

---

### 5️⃣ Probar API (acceso a documentación)

Abre en tu navegador:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

¡Ya puedes explorar y probar todos los endpoints! 🚀

---

## 🧪 Primeros Tests sin Autenticación

### Test 1: Listar Tipos de Documento

```bash
curl -X GET "http://localhost:8000/api/v1/document-types" \
  -H "Authorization: Bearer test_token"
```

**Esperado (200 OK):**
```json
{
  "request_id": "USR-...",
  "status": "success",
  "statusCode": 200,
  "data": [
    {
      "id": 1,
      "codigo": "CC",
      "nombre": "Cédula de Ciudadanía",
      "descripcion": "..."
    },
    ...
  ],
  "message": "Tipos de documento obtenidos"
}
```

---

## 🔑 Obtener Token para Tests

Para probar endpoints que requieren autenticación, necesitas:

1. **Obtener token de ms-autenticacion** (si está corriendo)
   ```bash
   curl -X POST "http://ms-autenticacion:8001/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username":"admin","password":"password"}'
   ```

2. **O usar token dummy para desarrollo**
   ```bash
   BEARER_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
   ```

3. **Usar en requests**
   ```bash
   curl -X GET "http://localhost:8000/api/v1/users/1" \
     -H "Authorization: Bearer $BEARER_TOKEN"
   ```

---

## 📊 Operaciones Comunes

### Crear Usuario

```bash
TOKEN="eyJ..."  # Tu token válido

curl -X POST "http://localhost:8000/api/v1/users" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "juan.perez",
    "email": "juan@example.com",
    "password_encrypted": "AQIDBA==",
    "rol_id": 2
  }'
```

> **Nota:** `password_encrypted` debe ser una contraseña cifrada en AES-256 + Base64

### Obtener Usuario

```bash
curl -X GET "http://localhost:8000/api/v1/users/1" \
  -H "Authorization: Bearer $TOKEN"
```

### Buscar Usuarios

```bash
curl -X GET "http://localhost:8000/api/v1/users?nombre=juan&pagina=1&items_por_pagina=10" \
  -H "Authorization: Bearer $TOKEN"
```

### Crear Perfil

```bash
curl -X PUT "http://localhost:8000/api/v1/users/1/profile" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_documento_id": 1,
    "numero_documento": "1234567890",
    "primer_nombre": "Juan",
    "primer_apellido": "Pérez",
    "fecha_nacimiento": "1990-05-15",
    "genero": "masculino",
    "ciudad": "Bogotá",
    "departamento": "Cundinamarca",
    "telefono_movil": "3001234567",
    "contacto_emergencia_nombre": "Maria Pérez",
    "contacto_emergencia_telefono": "3009876543"
  }'
```

### Cambiar Estado

```bash
curl -X PATCH "http://localhost:8000/api/v1/users/1/state" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "estado_nuevo": "suspendido",
    "motivo": "Violación de términos de servicio"
  }'
```

---

## 🐛 Troubleshooting Rápido

### Error: "uvicorn: El término no se reconoce"
```bash
# Solución: Usar python -m
python -m uvicorn main:app --reload --port 8000
```

### Error: "could not translate host name"
```bash
# Verificar en .env:
DB_HOST=localhost  # o 127.0.0.1
DB_PORT=5432
```

### Error: "Base de datos no existe"
```bash
# Crear base de datos:
psql -U postgres -f ms_usuario/init_db.sql
```

### Error: "401 Unauthorized"
```bash
# Verificar que pasas el Authorization header:
-H "Authorization: Bearer {token}"
```

### Error: "psycopg2.IntegrityError: duplicate key"
```bash
# Significa que el usuario/email ya existe
# Verifica que no estés creando con datos duplicados
```

---

## 📈 Estructura de Respuesta

**Éxito (200/201):**
```json
{
  "request_id": "USR-1713623400000-a1b2c3d4",
  "status": "success",
  "statusCode": 200,
  "data": { /* datos */ },
  "message": "Descripción del éxito"
}
```

**Error (400/401/403/404/500):**
```json
{
  "request_id": "USR-1713623400000-a1b2c3d4",
  "status": "error",
  "statusCode": 400,
  "data": null,
  "message": "Descripción del error"
}
```

---

## 🔐 Notas de Seguridad

1. **Nunca** guardes tokens en el código
2. **Nunca** envíes contraseñas en texto plano
3. **Siempre** usa HTTPS en producción
4. **Rota** las `AES_SECRET_KEY` periódicamente
5. **Monitorea** los logs de auditoría

---

## 📚 Próximos Pasos

1. **Leer documentación completa:**
   - [API Reference](rutas_y_endpoints.md)
   - [Modelo Relacional](modelo_relacional.md)
   - [Arquitectura](arquitectura_y_diagramas.md)

2. **Integrar ms-autenticacion:**
   - Configurar token real
   - Validar sesiones
   - Obtener permisos

3. **Testear endpoints:**
   - Usar Postman o Insomnia
   - Importar OpenAPI schema
   - Ejecutar flujos completos

4. **Deployment:**
   - Crear Dockerfile
   - Usar docker-compose
   - Configurar CI/CD

---

## ✅ Checklist Rápido

- [ ] Python 3.13 instalado (`python --version`)
- [ ] pip funcionando (`pip --version`)
- [ ] PostgreSQL corriendo (`psql --version`)
- [ ] Dependencias instaladas (`pip list | grep fastapi`)
- [ ] Base de datos creada (`psql -l | grep db_usuarios`)
- [ ] .env configurado con DB_HOST, DB_NAME, etc
- [ ] AES_SECRET_KEY generado
- [ ] Servidor inicia sin errores
- [ ] Swagger UI accesible en localhost:8000/docs
- [ ] Tipo documento endpoint retorna datos

---

## 🎓 Conceptos Clave

| Concepto | Explicación |
|----------|-------------|
| **Request ID** | Identificador único para rastrear una solicitud en logs |
| **Bearer Token** | JWT token en header Authorization |
| **Permiso** | Validación de rol para acceder a endpoint |
| **Transacción** | Cambios de estado son atómicos (todo o nada) |
| **Soft Delete** | Usuario no se elimina, se marca como eliminado |
| **Auditoría** | Todos los cambios se registran en ms-auditoria |

---

## 📞 Contacto & Soporte

Para problemas:
1. Revisar logs en terminal
2. Verificar .env
3. Chequear BD está corriendo
4. Revisar documentación en `/documentacion/`

---

**¡Listo para desarrollar! 🚀**

