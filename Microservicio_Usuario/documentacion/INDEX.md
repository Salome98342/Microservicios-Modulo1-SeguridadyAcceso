# 📚 Documentación Completa - MS-Usuarios

```
██╗   ██╗███████╗██╗   ██╗ █████╗ ██████╗ ██╗ ██████╗ ███████╗
██║   ██║██╔════╝██║   ██║██╔══██╗██╔══██╗██║██╔═══██╗██╔════╝
██║   ██║███████╗██║   ██║███████║██████╔╝██║██║   ██║███████╗
██║   ██║╚════██║██║   ██║██╔══██║██╔══██╗██║██║   ██║╚════██║
╚██████╔╝███████║╚██████╔╝██║  ██║██║  ██║██║╚██████╔╝███████║
 ╚═════╝ ╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝ ╚═════╝ ╚══════╝
                     Microservicio de Usuarios
```

---

## 🗺️ Mapa de Documentación

Elige el archivo que necesitas según tu tarea:

### 🚀 **[Inicio Rápido](quick_start.md)** ⭐ START HERE
> Para comenzar en 5 minutos
- Instalación de dependencias
- Configuración de base de datos
- Inicio del servidor
- Primeros tests

**Perfil:** Desarrolladores nuevos, onboarding rápido

---

### 📘 **[README Principal](README.md)**
> Visión general y referencia rápida
- Descripción general del servicio
- Estructura de carpetas
- Requisitos funcionales implementados
- Checklist de deployment

**Perfil:** Arquitectos, DevOps, líderes técnicos

---

### 🔌 **[Rutas y Endpoints](rutas_y_endpoints.md)** ⭐ API REFERENCE
> Documentación completa de cada endpoint
 - 19 endpoints detallados
- Request/Response de ejemplo
- Parámetros y validaciones
- Códigos de error
- Permisos requeridos

**Perfil:** Desarrolladores frontend, integradores

---

### 📊 **[Modelo Relacional](modelo_relacional.md)**
> Diagrama ER y estructura de datos
- Diagrama entidades-relaciones en Mermaid
- Descripción detallada de 5 tablas
- Índices para optimización
- Integridad referencial
- Datos iniciales

**Perfil:** DBAs, arquitectos de datos

---

### 🏛️ **[Arquitectura y Diagramas](arquitectura_y_diagramas.md)** ⭐ SYSTEM DESIGN
> Diagramas de flujo y arquitectura
- Arquitectura de capas
- Flujos de autenticación
- Cifrado de datos
- Estados del usuario
- Integración con otros microservicios

**Perfil:** Arquitectos, desarrolladores senior

---

### 🧪 **[Ejemplos cURL](ejemplos_curl.md)**
> Colección de requests listos para copiar/pegar
 - 18 ejemplos de cURL
- Scenarios de prueba
- Comandos útiles
- Tips para testing

**Perfil:** QA, desarrolladores, testers

---

### 📋 **[Firmas de Endpoints](firmas.md)** ⭐ QUICK REFERENCE
> Resumen técnico de todas las funciones y endpoints
- Firmas completas de funciones Python
- Parámetros de headers requeridos
- Modelos Pydantic (Request/Response)
- Enums y tipos de datos
- Códigos HTTP y estructura de respuesta

**Perfil:** Desarrolladores backend, integradores API

---

### 🗄️ **[Creación de Base de Datos](creacion_base_datos.md)** ⭐ DB SETUP
> Guía completa para crear e inicializar la BD
- Instalación de PostgreSQL en Windows/Linux/macOS
- Script SQL para crear todas las tablas
- Creación de índices para optimización
- Datos predeterminados (tipos de documento)
- Triggers para automatización
- Backup y restauración
- Troubleshooting y mantenimiento

**Perfil:** DevOps, DBAs, desarrolladores backend

---

## 📊 Matriz de Contenido

| Archivo | Contenido | Tiempo | Público |
|---------|----------|--------|---------|
| quick_start.md | Inicio rápido | 5 min | ✅ |
| README.md | Visión general | 10 min | ✅ |
| rutas_y_endpoints.md | API Reference | 20 min | ✅ |
| firmas.md | Firmas técnicas | 15 min | ✅ |
| modelo_relacional.md | BD + Tablas | 15 min | 🔒 |
| arquitectura_y_diagramas.md | Diagramas técnicos | 15 min | 🔒 |
| creacion_base_datos.md | Setup BD | 20 min | 🔒 |
| ejemplos_curl.md | Testing | 10 min | ✅ |

---

## 🎯 Guías por Caso de Uso

### 👤 Soy Desarrollador Frontend
```
Lectura recomendada:
1. quick_start.md (para setup)
2. rutas_y_endpoints.md (endpoints disponibles)
3. firmas.md (modelos Request/Response)
4. ejemplos_curl.md (para testing)
```

### 🔧 Soy Desarrollador Backend
```
Lectura recomendada:
1. quick_start.md (setup)
2. README.md (estructura)
3. arquitectura_y_diagramas.md (flujos)
4. modelo_relacional.md (BD)
5. firmas.md (firmas técnicas)
6. rutas_y_endpoints.md (integración)
7. creacion_base_datos.md (setup BD)
```

### 🏗️ Soy Arquitecto
```
Lectura recomendada:
1. README.md (overview)
2. arquitectura_y_diagramas.md (diseño)
3. modelo_relacional.md (datos)
4. rutas_y_endpoints.md (API)
5. firmas.md (referencia técnica)
```

### 📊 Soy DBA / Data Engineer
```
Lectura recomendada:
1. creacion_base_datos.md (setup completo)
2. modelo_relacional.md (tablas + índices)
3. README.md (datos iniciales)
4. arquitectura_y_diagramas.md (integraciones)
```

### 🧪 Soy QA / Tester
```
Lectura recomendada:
1. quick_start.md (setup)
2. ejemplos_curl.md (requests)
3. rutas_y_endpoints.md (validaciones)
4. firmas.md (tipos de datos)
```

---

## 📋 Estructura de Carpeta

```
documentacion/
│
├── 📄 INDEX.md (este archivo)
│   └─ Te encuentras aquí → Guía de navegación
│
├── 🚀 quick_start.md ⭐
│   └─ Inicio en 5 minutos
│
├── 📘 README.md
│   └─ Descripción general y checklist
│
├── 🔌 rutas_y_endpoints.md ⭐
│   └─ API Reference completa (19 endpoints)
│
├── 📊 modelo_relacional.md
│   └─ ER diagram + 5 tablas + índices
│
├── 🏛️ arquitectura_y_diagramas.md ⭐
│   └─ Flujos, estados, integraciones
│
└── 🧪 ejemplos_curl.md
   └─ 18 ejemplos cURL + testing
```

---

## ⚡ Búsqueda Rápida

### 🔍 ¿Cómo inicio el servidor?
→ [quick_start.md - Paso 4](quick_start.md#4️⃣-iniciar-servidor-1-minuto)

### 🔍 ¿Cuáles son los endpoints disponibles?
→ [rutas_y_endpoints.md](rutas_y_endpoints.md)

### 🔍 ¿Cómo se ve el diagrama ER?
→ [modelo_relacional.md - Diagrama](modelo_relacional.md#diagrama-de-entidades-y-relaciones)

### 🔍 ¿Cómo cambio el estado de un usuario?
→ [rutas_y_endpoints.md - Cambiar Estado](rutas_y_endpoints.md#7-cambiar-estado-de-usuario)

### 🔍 ¿Cuáles son los permisos requeridos?
→ [README.md - Permisos](README.md#-permisos-requeridos)

### 🔍 ¿Cuál es la arquitectura del sistema?
→ [arquitectura_y_diagramas.md](arquitectura_y_diagramas.md)

### 🔍 ¿Cómo pruebo los endpoints?
→ [ejemplos_curl.md](ejemplos_curl.md)

---

## 📚 Documentación por Tema

### 🔐 Seguridad
- [Autenticación y Autorización](arquitectura_y_diagramas.md#flujo-de-autenticación-y-autorización)
- [Cifrado de Datos](arquitectura_y_diagramas.md#flujo-de-cifrado-y-desencriptado)
- [Permisos Requeridos](README.md#-permisos-requeridos)

### 🗄️ Base de Datos
- [Modelo Relacional](modelo_relacional.md)
- [Descripción de Tablas](modelo_relacional.md#-descripción-detallada-de-tablas)
- [Índices](modelo_relacional.md#-índices-para-optimización)

### 🔌 API
- [Todos los Endpoints](rutas_y_endpoints.md#-tabla-de-contenidos)
- [Estructura de Respuesta](rutas_y_endpoints.md#-estructura-de-respuesta-estándar)
- [Ejemplos cURL](ejemplos_curl.md)

### 🏗️ Arquitectura
- [Diagrama General](arquitectura_y_diagramas.md#diagrama-de-arquitectura-completa)
- [Flujos de Datos](arquitectura_y_diagramas.md#flujo-de-solicitud---crear-usuario)
- [Integraciones](arquitectura_y_diagramas.md#integración-con-otros-microservicios)

### 🚀 Deployment
- [Checklist](README.md#-checklist-de-deployment)
- [Variables de Entorno](README.md#configuración-env)
- [Início Rápido](quick_start.md)

---

## 🎓 Conceptos Clave

| Concepto | Documentación |
|----------|---------------|
| Request ID | [README.md](README.md#-permisos-requeridos) |
| Soft Delete | [README.md](README.md#conceptos-clave) |
| Transacción Atómica | [arquitectura_y_diagramas.md](arquitectura_y_diagramas.md#flujo-de-solicitud---cambiar-estado-transaccional) |
| AES-256 Encryption | [arquitectura_y_diagramas.md](arquitectura_y_diagramas.md#flujo-de-cifrado-y-desencriptado) |
| Paginación | [arquitectura_y_diagramas.md](arquitectura_y_diagramas.md#modelo-de-paginación) |

---

## 📞 Stack Técnico

```
┌─────────────────────────────────────────┐
│ FastAPI 0.115.12                        │
│ uvicorn 0.34.2                          │
│ Pydantic 2.11.3                         │
├─────────────────────────────────────────┤
│ bcrypt 4.1.3 (password hashing)         │
│ pycryptodome 3.21.0 (AES-256)           │
│ python-dotenv 1.0.1 (.env)              │
├─────────────────────────────────────────┤
│ psycopg2-binary >=2.9.9 (PostgreSQL)    │
│ PostgreSQL 12+                          │
└─────────────────────────────────────────┘
```

---

## ✅ Requisitos Funcionales

Todos los requisitos están **100% implementados**:

- ✅ USR-RF-001 a USR-RF-024 (24 requisitos)
- ✅ 19 endpoints totales
- ✅ 5 tablas normalizadas
- ✅ Auditoría completa
- ✅ Encriptación AES-256
- ✅ Autenticación JWT
- ✅ Autorización RBAC

[Ver lista completa →](README.md#-requisitos-funcionales-implementados)

---

## 🔧 Troubleshooting Rápido

| Problema | Solución |
|----------|----------|
| "uvicorn no se reconoce" | [quick_start.md](quick_start.md#-troubleshooting-rápido) |
| "Base de datos no existe" | [quick_start.md](quick_start.md#2️⃣-configuración-de-base-de-datos-2-minutos) |
| "401 Unauthorized" | [ejemplos_curl.md](ejemplos_curl.md#🔑-obtener-token-para-tests) |
| "404 Usuario no encontrado" | [rutas_y_endpoints.md](rutas_y_endpoints.md#2-obtener-usuario-por-id) |

---

## 📌 Notas Importantes

1. **Seguridad:**
   - Nunca guardes tokens en código
   - Nunca envíes contraseñas en texto plano
   - Rota AES_SECRET_KEY periódicamente

2. **Performance:**
   - Los índices están optimizados para búsquedas comunes
   - Paginación por defecto: 10 items/página
   - Máximo 100 items por página

3. **Validaciones:**
   - Edad mínima: 14 años
   - Username mínimo: 3 caracteres
   - Email debe ser válido
   - Documento único por usuario

4. **Estados de Usuario:**
   - `activo` - Usuario funcional
   - `inactivo` - Desactivado por el sistema
   - `suspendido` - En revisión
   - `eliminado` - Soft delete

---

## 🎯 Next Steps

1. **Para empezar hoy:**
   - Lee [quick_start.md](quick_start.md)
   - Ejecuta los comandos de setup
   - Accede a http://localhost:8000/docs

2. **Para entender el sistema:**
   - Lee [arquitectura_y_diagramas.md](arquitectura_y_diagramas.md)
   - Estudia el [modelo relacional](modelo_relacional.md)
   - Revisa los [flujos de datos](arquitectura_y_diagramas.md#flujo-de-solicitud---crear-usuario)

3. **Para integrar:**
   - Consulta [rutas_y_endpoints.md](rutas_y_endpoints.md)
   - Usa [ejemplos_curl.md](ejemplos_curl.md)
   - Configura los tokens en `.env`

4. **Para desplegar:**
   - Revisa el [checklist](README.md#-checklist-de-deployment)
   - Actualiza credenciales reales
   - Configura backups y monitoreo

---

## 📊 Estadísticas de Documentación

```
Total de archivos:    6 archivos MD
Total de líneas:      ~3,000 líneas
Endpoints documentados: 19 endpoints
Tablas documentadas:   5 tablas
Diagramas:            10 diagramas Mermaid
Ejemplos cURL:        18 ejemplos
Tiempo de lectura:    ~90 minutos (todo)
```

---

## 📄 Versionado

```
Versión:      1.0.0
Última actualización: 19 de Abril de 2026
Estado:       ✅ Completo y funcional
Mantenedor:   Equipo de Desarrollo
```

---

## 🚀 ¡Comienza Ahora!

```bash
# 1. Abre quick_start.md
# 2. Sigue los 5 pasos
# 3. ¡Listo para desarrollar!

→ [Abrir Quick Start →](quick_start.md)
```

---

**Última actualización:** 19 de Abril de 2026 📅  
**Versión:** 1.0.0 ✅  
**Estado:** Producción lista 🚀

