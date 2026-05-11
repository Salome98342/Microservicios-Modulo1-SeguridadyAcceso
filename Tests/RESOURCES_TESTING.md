# 📚 RECURSOS DE TESTING - MICROSERVICIOS V1

> Guía completa para iniciar pruebas de los 3 microservicios principales

---

## 📦 ARCHIVOS CREADOS

### 1. **`QUICKSTART.ps1`** — 🚀 Inicio en 1 click
**Propósito:** Script automatizado que hace todo

**Qué hace:**
- Navega al directorio correcto
- Detiene y limpia contenedores anteriores
- Levanta `docker-compose`
- Espera a que las BDs estén listas (15 segundos)
- Instala dependencias Python
- Ejecuta script de setup

**Cómo usar:**
```powershell
# Abre PowerShell en el directorio del proyecto
cd "c:\Users\salom\OneDrive\Documentos\7 Semestre\Desarrollo 3\Microservicios"

# Ejecutar script
.\QUICKSTART.ps1
```

**Tiempo total:** ⏱️ ~3-5 minutos

---

### 2. **`setup_initial_data.py`** — 🗄️ Poblar Bases de Datos

**Propósito:** Script Python que inicializa todos los datos de prueba

**Qué crea:**
- ✅ **Usuarios de prueba:**
  - `admin` / `admin123`
  - `estudiante` / `estud123`

- ✅ **Tipos de documento:** CC, TI, CE, PA

- ✅ **Roles básicos:** admin, estudiante, docente, staff

- ✅ **Permisos del sistema:** 
  - USR.READ, USR.CREATE, USR.UPDATE, USR.DELETE
  - ROL.READ, ROL.CREATE, ROL.UPDATE, ROL.DELETE
  - AUTH.LOGIN, AUTH.LOGOUT, AUTH.ADMIN

- ✅ **Asignaciones de permisos** a cada rol

- ✅ **Tokens de aplicación** para inter-servicios

**Dependencias:**
```bash
pip install requests psycopg2-binary bcrypt
```

**Uso manual (si no usas QUICKSTART.ps1):**
```bash
python setup_initial_data.py
```

---

### 3. **`TESTING_GUIDE.md`** — 📖 Guía Completa

**Propósito:** Documentación exhaustiva del proceso de testing

**Contiene:**
1. **Configuración Inicial** — Pasos 1-3 del setup
2. **Estructura de Pruebas** — URLs y puertos de cada servicio
3. **Flujo de Autenticación** — Paso a paso del login
4. **Ejemplos Prácticos** — Código cURL listo para copiar/pegar
5. **Troubleshooting** — Soluciones a errores comunes
6. **Checklist de Validación** — ✅ Pasos para verificar que todo funciona

**Secciones principales:**
- 🔐 Login (obtener token)
- 👥 Crear usuarios y perfiles
- 🛡️ Gestionar roles y permisos
- 🔄 Flujo completo de autenticación
- 🐛 Errores y cómo resolverlos

---

### 4. **`postman_auth_profile.json`** — 📬 Colección de Postman

**Propósito:** Colección lista para importar en Postman

**Qué incluye:**
- 🔐 **Autenticación (5 requests)**
  - Login ADMIN
  - Login Estudiante
  - Validar Token
  - Listar Sesiones Activas
  - Logout

- 👥 **Usuarios (6 requests)**
  - Listar Tipos de Documento
  - Listar Usuarios
  - Obtener Usuario por ID
  - Crear Nuevo Usuario
  - Crear Perfil
  - Actualizar Usuario

- 🛡️ **Roles y Permisos (5 requests)**
  - Listar Roles
  - Obtener Rol por ID
  - Obtener Permisos del Rol
  - Listar Permisos
  - Crear Rol

- 🏥 **Health Checks (3 requests)**
  - Health Auth Service
  - Health Usuarios Service
  - Health Roles Service

**Variables preconfiguradas:**
- `auth_url` = http://localhost:8002
- `usuarios_url` = http://localhost:8000
- `roles_url` = http://localhost:8003
- `token` = (se auto-llena al hacer login)
- `user_id` = (se auto-llena al crear usuario)

**Cómo importar:**
1. Abre Postman
2. Click en **Import** 
3. Selecciona archivo `postman_auth_profile.json`
4. Click en **1️⃣ Login como ADMIN** para obtener token
5. ¡Listo para hacer pruebas!

---

## 🚀 FLUJO RECOMENDADO

### **OPCIÓN A: Automático (Recomendado)**

```powershell
# 1. Ejecutar script de inicio
.\QUICKSTART.ps1

# Esperar a que termine...

# 2. Abrir Postman
# 3. Importar postman_auth_profile.json
# 4. Hacer clic en "1️⃣ Login como ADMIN"
# 5. ¡A probar!
```

---

### **OPCIÓN B: Manual (Si algo falla)**

```powershell
# 1. Levantar Docker
cd "c:\Users\salom\OneDrive\Documentos\7 Semestre\Desarrollo 3\Microservicios"
docker-compose up -d

# 2. Instalar Python deps
pip install requests psycopg2-binary bcrypt

# 3. Esperar 15 segundos y ejecutar setup
Start-Sleep -Seconds 15
python setup_initial_data.py

# 4. Continuar con Postman...
```

---

## 📊 VERIFICACIÓN RÁPIDA

Después de ejecutar `QUICKSTART.ps1`, ejecuta estos comandos para verificar que todo está listo:

```bash
# ✅ Ver estado de contenedores
docker-compose ps

# ✅ Ver logs de cada servicio
docker-compose logs ms-autenticacion
docker-compose logs ms-usuarios-app
docker-compose logs ms-roles

# ✅ Health check manual
curl http://localhost:8002/api/v1/health
curl http://localhost:8000/api/v1/health
curl http://localhost:8003/api/v1/health

# ✅ Ver documentación Swagger
# Abre en el navegador:
# http://localhost:8002/docs
# http://localhost:8000/docs
# http://localhost:8003/docs
```

---

## 🔐 CREDENCIALES DE PRUEBA

```
┌─────────────────────────────────────────┐
│ ADMIN                                   │
├─────────────────────────────────────────┤
│ Usuario:     admin                      │
│ Contraseña:  admin123                   │
│ Email:       admin@universidad.edu.co   │
│ Rol:         admin                      │
│ Permisos:    TODOS                      │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ ESTUDIANTE                              │
├─────────────────────────────────────────┤
│ Usuario:     estudiante                 │
│ Contraseña:  estud123                   │
│ Email:       estudiante@universidad...  │
│ Rol:         estudiante                 │
│ Permisos:    Lectura básica              │
└─────────────────────────────────────────┘
```

---

## 🎯 CASOS DE USO PROBADOS

Con esta configuración puedes probar:

### ✅ **Autenticación**
- [x] Login con credenciales correctas
- [x] Login con credenciales incorrectas
- [x] Validación de token JWT
- [x] Manejo de tokens expirados
- [x] Logout correctamente

### ✅ **Gestión de Usuarios**
- [x] Ver listado de usuarios
- [x] Crear nuevo usuario
- [x] Crear perfil de usuario
- [x] Actualizar datos de usuario
- [x] Ver tipos de documento

### ✅ **Roles y Permisos**
- [x] Ver roles disponibles
- [x] Consultar permisos de un rol
- [x] Crear nuevo rol
- [x] Asignar permisos a rol

### ✅ **Inter-servicio**
- [x] MS-Autenticación valida con MS-Usuarios
- [x] MS-Autenticación consulta roles en MS-Roles
- [x] Tokens de aplicación funcionan
- [x] Health checks OK

---

## 📋 CHECKLIST PRE-TESTING

Antes de hacer pruebas, asegúrate que:

- [ ] Docker Desktop está corriendo
- [ ] `QUICKSTART.ps1` ejecutó sin errores
- [ ] Todos los 6 contenedores están en status "Up"
- [ ] `setup_initial_data.py` mostró "✅ INICIALIZACIÓN COMPLETADA"
- [ ] Postman está instalado
- [ ] Importaste `postman_auth_profile.json` en Postman
- [ ] Las URLs en las variables de Postman están correctas

---

## 🐛 TROUBLESHOOTING RÁPIDO

| Problema | Solución |
|----------|----------|
| **"Connection Refused"** | Los servicios no están corriendo. Ejecuta `docker-compose up -d` |
| **"Database does not exist"** | Las BDs no inicializaron. Ejecuta `python setup_initial_data.py` |
| **"Invalid credentials"** | Verifica credenciales: `admin` / `admin123` |
| **"Token Expired"** | Haz login nuevamente para obtener un token fresco |
| **Puerto 8002/8000/8003 en uso** | Cambia los puertos en `docker-compose.yml` |

---

## 📞 ARCHIVOS RELACIONADOS

- 📄 [TESTING_GUIDE.md](TESTING_GUIDE.md) — Guía detallada de testing
- 🐍 [setup_initial_data.py](setup_initial_data.py) — Script de inicialización
- 📬 [postman_auth_profile.json](postman_auth_profile.json) — Colección de Postman
- 🚀 [QUICKSTART.ps1](QUICKSTART.ps1) — Script de inicio automático

---

## 🎓 PRÓXIMAS PRUEBAS

Después de validar estos 3 microservicios, puedes:
1. Integrar MS-Notificaciones
2. Integrar MS-Auditoría
3. Crear flujos de integración más complejos
4. Implementar tests automatizados

---

**Última actualización:** Mayo 2025  
**Versión:** 1.0  
**Estado:** ✅ Listo para Testing
