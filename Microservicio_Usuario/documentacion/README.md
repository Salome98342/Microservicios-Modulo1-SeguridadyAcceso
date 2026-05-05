# 📚 Documentación - Microservicio de Usuarios (MS-Usuarios)

## 🎯 Descripción General

Este microservicio gestiona todo lo relacionado con la administración de usuarios en la plataforma, incluyendo:
- ✅ Crear, leer, actualizar y eliminar usuarios
- ✅ Gestión de perfiles extendidos con información personal
- ✅ Historial de cambios de estado de usuario
- ✅ Preferencias de notificación configurables
- ✅ Validación de integridad mediante tipos de documento
- ✅ Auditoría completa de operaciones
- ✅ Encriptación de contraseñas y datos sensibles

---

## 📁 Estructura de Documentación

```
documentacion/
├── README.md                    (este archivo)
├── modelo_relacional.md         (Diagrama ER y descripción de tablas)
├── rutas_y_endpoints.md         (API Reference completa)
└── Nota: la guía de desarrollo completa se encuentra en `ms_usuario/ms-usuarios_guia_desarrollo_completa_v2.md`
```

---

## 📄 Documentos Disponibles

### 1. **[Modelo Relacional](modelo_relacional.md)** 📊
Diagrama de entidades y relaciones de la base de datos con:
- Diagrama ER en Mermaid
- Descripción detallada de cada tabla
- Relaciones y restricciones
- Índices para optimización
- Integridad referencial

**Contenido principal:**
- Tabla `usr_usuarios` - Datos de autenticación
- Tabla `usr_perfiles` - Información extendida del usuario
- Tabla `usr_historial_estados` - Registro de auditoría
- Tabla `usr_preferencias_notificacion` - Configuración de notificaciones
- Tabla `usr_tipos_documento` - Catálogo de documentos

### 2. **[Rutas y Endpoints](rutas_y_endpoints.md)** 🚀
Referencia completa de API con:
- 19 endpoints detallados
- Request/Response de ejemplo para cada ruta
- Códigos de error y validaciones
- Permisos requeridos
- Headers obligatorios y opcionales

**Endpoint Summary:**
| Método | Ruta | Propósito |
|--------|------|----------|
| `POST` | `/users` | Crear usuario |
| `GET` | `/users/{id}` | Obtener usuario |
| `GET` | `/users` | Búsqueda avanzada |
| `PUT` | `/users/{id}` | Actualizar usuario |
| `DELETE` | `/users/{id}` | Desactivar usuario |
| `PATCH` | `/users/{id}/state` | Cambiar estado |
| `POST` | `/users/{id}/reactivate` | Reactivar usuario |
| `PATCH` | `/users/{id}/password` | Cambiar contraseña |
| `GET` | `/users/{id}/profile` | Obtener perfil |
| `PUT` | `/users/{id}/profile` | Crear/Actualizar perfil |
| `GET` | `/users/{id}/state-history` | Historial de cambios |
| `GET` | `/users/{id}/notification-preferences` | Obtener preferencias |
| `PUT` | `/users/{id}/notification-preferences` | Actualizar preferencias |
| `GET` | `/document-types` | Listar tipos de documento |

---

## 🏗️ Arquitectura

```
FastAPI Application
│
├─ routes/
│  ├─ usuarios.py          (13 endpoints)
│  ├─ perfiles.py          (2 endpoints)
│  ├─ historial.py         (1 endpoint)
│  ├─ preferencias.py      (2 endpoints)
│  └─ tipos_documento.py   (1 endpoint)
│
├─ services/
│  ├─ usuario_service.py
│  ├─ perfil_service.py
│  ├─ historial_service.py
│  ├─ preferencias_service.py
│  └─ tipo_documento_service.py
│
├─ repository/
│  ├─ usuario_repository.py
│  ├─ perfil_repository.py
│  ├─ historial_repository.py
│  ├─ preferencias_repository.py
│  └─ tipo_documento_repository.py
│
├─ models/
│  ├─ usuario.py
│  ├─ perfil.py
│  ├─ historial_estado.py
│  ├─ preferencias_notificacion.py
│  ├─ tipo_documento.py
│  └─ response.py
│
├─ utils/
│  ├─ crypto.py            (AES-256, bcrypt)
│  ├─ request_id.py        (Generación de request IDs)
│  ├─ audit.py             (Logging a ms-auditoria)
│  └─ inter_service.py     (Comunicación entre servicios)
│
├─ config.py               (Configuración centralizada)
├─ database.py             (Conexión a PostgreSQL)
├─ main.py                 (Punto de entrada FastAPI)
└─ requirements.txt        (Dependencias)
```

---

## 🔐 Seguridad

### Autenticación
- JWT Bearer Tokens via `Authorization` header
- Validación de sesión activa en ms-autenticacion
- Request IDs únicos para trazabilidad (`X-Request-ID`)

### Autorización
- 13+ permisos granulares (RBAC)
- Validación de roles contra ms-roles
- Control de acceso a nivel de endpoint

### Cifrado
- **Contraseñas:** bcrypt (cost factor 12)
- **Datos sensibles en tránsito:** AES-256-CBC
- **Base de datos:** Contraseñas hasheadas, nunca en texto plano

### Auditoría
- Todas las operaciones se registran en ms-auditoria
- Historial completo de cambios de estado
- Backup local JSONL si ms-auditoria está fuera de línea

---

## 💾 Base de Datos

**Motor:** PostgreSQL 12+  
**Tablas:** 5 tablas normalizadas  
**Registros iniciales:** 7 tipos de documento  

### Configuración .env

```bash
# Base de datos
DB_HOST=localhost
DB_PORT=5432
DB_NAME=db_usuarios
DB_USER=postgres
DB_PASSWORD=password_seguro

# Cifrado
AES_SECRET_KEY=<64_caracteres_hex>  # python -c "import secrets; print(secrets.token_hex(32))"
BCRYPT_ROUNDS=12

# Tokens internos
USR_APP_TOKEN=token_de_ms_usuarios
AUTH_APP_TOKEN=token_de_ms_autenticacion
ROL_APP_TOKEN=token_de_ms_roles
NOT_APP_TOKEN=token_de_ms_notificaciones
AUD_APP_TOKEN=token_de_ms_auditoria

# URLs de servicios
AUTH_SERVICE_URL=http://ms-autenticacion:8001
ROL_SERVICE_URL=http://ms-roles:8002
NOT_SERVICE_URL=http://ms-notificaciones:8003
AUD_SERVICE_URL=http://ms-auditoria:8004

# Timeouts
TIMEOUT_AUTH=3
TIMEOUT_ROL=3
TIMEOUT_NOT=1
TIMEOUT_AUD=0.5
```

---

## 🚀 Inicio Rápido

### 1. Instalación de dependencias
```bash
pip install -r requirements.txt
```

### 2. Crear base de datos
```bash
psql -U postgres -f ms_usuario/init_db.sql
```

### 3. Configurar .env
```bash
cp .env.example .env
# Editar .env con tus valores
```

### 4. Iniciar servidor
```bash
python -m uvicorn main:app --reload --port 8000
```

### 5. Acceder a documentación
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 📦 Dependencias Principales

| Paquete | Versión | Uso |
|---------|---------|-----|
| FastAPI | 0.115.12 | Framework web |
| uvicorn | 0.34.2 | Servidor ASGI |
| psycopg2-binary | >=2.9.9 | Driver PostgreSQL |
| Pydantic | 2.11.3 | Validación de datos |
| bcrypt | 4.1.3 | Hash de contraseñas |
| pycryptodome | 3.21.0 | Cifrado AES-256 |
| python-dotenv | 1.0.1 | Variables de entorno |

---

## 🔄 Flujos Principales

### Crear Usuario
```
POST /users
  ↓ [Validar sesión y permisos]
  ↓ [Desencriptar contraseña AES]
  ↓ [Hash bcrypt]
  ↓ [Insertar en BD]
  ↓ [Registrar en auditoria]
  ↓ [Notificar bienvenida]
  ↓ 201 Created
```

### Cambiar Estado
```
PATCH /users/{id}/state
  ↓ [Validar sesión y permisos]
  ↓ [Validar nuevo estado]
  ↓ [Transacción atómica]:
     ├─ [Actualizar estado en usr_usuarios]
     └─ [Registrar en usr_historial_estados]
  ↓ [Registrar en auditoria]
  ↓ [Notificar cambio]
  ↓ 200 OK
```

### Búsqueda Avanzada
```
GET /users?nombre=&ciudad=&pagina=1
  ↓ [Validar sesión y permisos]
  ↓ [Construir query SQL con JOINs]
  ↓ [Aplicar filtros ILIKE]
  ↓ [Contar registros totales]
  ↓ [Aplicar paginación]
  ↓ [Retornar ResultadoPaginado]
  ↓ 200 OK
```

---

## ✅ Requisitos Funcionales Implementados

| RF | Descripción | Estado |
|----|-------------|--------|
| USR-RF-001 | Validar sesión activa | ✅ |
| USR-RF-002 | Validar permisos de rol | ✅ |
| USR-RF-006 | Crear usuario | ✅ |
| USR-RF-007 | Obtener usuario por ID | ✅ |
| USR-RF-008 | Obtener usuario por email | ✅ |
| USR-RF-010 | Actualizar usuario | ✅ |
| USR-RF-011 | Desactivar usuario | ✅ |
| USR-RF-012 | Búsqueda avanzada | ✅ |
| USR-RF-013 | Obtener perfil | ✅ |
| USR-RF-014 | Crear/Actualizar perfil | ✅ |
| USR-RF-015 | Cambiar estado | ✅ |
| USR-RF-016 | Obtener historial | ✅ |
| USR-RF-017 | Listar tipos documento | ✅ |
| USR-RF-018 | Obtener preferencias | ✅ |
| USR-RF-019 | Actualizar preferencias | ✅ |
| USR-RF-020 | Reactivar usuario | ✅ |
| USR-RF-021 | Validar existencia | ✅ |
| USR-RF-022 | Cambiar contraseña | ✅ |
| USR-RF-023 | Listar por rol | ✅ |
| USR-RF-024 | Estadísticas | ✅ |

---

## 🧪 Testing

### Ejecutar tests
```bash
pytest tests/ -v
```

### Ejemplos con cURL

**Crear usuario:**
```bash
curl -X POST http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john.doe",
    "email": "john@example.com",
    "password_encrypted": "base64_encoded_aes_cipher",
    "rol_id": 2
  }'
```

**Obtener usuario:**
```bash
curl -X GET http://localhost:8000/api/v1/users/1 \
  -H "Authorization: Bearer {token}"
```

**Búsqueda avanzada:**
```bash
curl -X GET "http://localhost:8000/api/v1/users?nombre=john&ciudad=Bogota&pagina=1&items_por_pagina=10" \
  -H "Authorization: Bearer {token}"
```

---

## 📞 Integración con Otros Microservicios

| Servicio | Puerto | Uso |
|----------|--------|-----|
| ms-autenticacion | 8001 | Validar sesiones, obtener contraseñas |
| ms-roles | 8002 | Validar permisos de usuario |
| ms-notificaciones | 8003 | Enviar notificaciones (bienvenida, cambios) |
| ms-auditoria | 8004 | Registrar logs de operaciones |

---

## 🐛 Troubleshooting

### Error: "psycopg2.Error: could not translate host name..."
**Causa:** Base de datos no accesible  
**Solución:** Verificar `DB_HOST`, `DB_PORT`, credenciales en `.env`

### Error: "Invalid X-App-Token"
**Causa:** Token de servicio incorrecto  
**Solución:** Verificar tokens en `.env` para ms-autenticacion, ms-roles, etc.

### Error: "Permiso denegado (USR_CREATE)"
**Causa:** Usuario no tiene permisos  
**Solución:** Verificar rol del usuario en ms-roles

---

## 📚 Referencias Adicionales

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [bcrypt Documentation](https://github.com/pyca/bcrypt)

---

**Última actualización:** 19 de Abril de 2026  
**Versión:** 1.0.0  
**Estado:** ✅ Completo y funcional

