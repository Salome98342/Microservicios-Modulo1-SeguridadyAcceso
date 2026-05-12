# Especificación de Requisitos

## 1. Introducción

Este documento define los requisitos funcionales a nivel de sistema del **Microservicio de Usuarios** con base en el comportamiento implementado en rutas, servicios, validaciones y persistencia.

## 2. Requisitos Funcionales a Nivel del Sistema

Los requisitos se expresan como capacidades funcionales del sistema (no como casos de uso), incluyendo creación y gestión de usuarios, seguridad, auditoría e integración con otros microservicios.

| Código | Nombre | Descripción |
|---|---|---|
| REQ1 | Crear usuario | El sistema registra un usuario con `username`, `email`, contraseña cifrada y `rol_id`, validando unicidad y rol. |
| REQ2 | Consultar usuario por ID | El sistema permite consultar datos públicos del usuario por identificador. |
| REQ3 | Consultar usuario por email | El sistema permite consultar por correo; para ms-autenticación puede incluir `password_hash`. |
| REQ4 | Actualizar datos básicos de usuario | El sistema permite actualizar `username`, `email` y/o `rol_id` con validaciones de colisión y rol válido. |
| REQ5 | Cambiar estado de usuario | El sistema permite cambiar estado (`activo`, `inactivo`, `suspendido`) registrando motivo e historial. |
| REQ6 | Desactivar usuario | El sistema permite desactivar (soft delete) un usuario dejando estado `inactivo`. |
| REQ7 | Reactivar usuario | El sistema permite reactivar un usuario cambiando estado a `activo`. |
| REQ8 | Cambiar contraseña | El sistema permite al usuario autenticado cambiar su contraseña cumpliendo política de seguridad. |
| REQ9 | Consultar perfil extendido | El sistema permite obtener perfil extendido de un usuario. |
| REQ10 | Crear/actualizar perfil extendido | El sistema permite upsert de perfil con validación de edad mínima y datos personales. |
| REQ11 | Consultar preferencias de notificación | El sistema permite consultar preferencias de notificación por usuario. |
| REQ12 | Actualizar preferencias de notificación | El sistema permite actualizar canales y horario de no molestar con reglas de consistencia. |
| REQ13 | Consultar historial de estados | El sistema permite consultar el historial cronológico de cambios de estado. |
| REQ14 | Consultar catálogo de tipos de documento | El sistema expone tipos de documento activos para perfiles. |
| REQ15 | Búsqueda avanzada de usuarios | El sistema permite búsqueda por filtros (`nombre`, `documento`, `email`, `estado`, `ciudad`) con paginación. |
| REQ16 | Estadísticas de usuarios por estado | El sistema entrega total de usuarios y distribución por estado. |
| REQ17 | Listar usuarios por rol | El sistema permite listar usuarios por `rol_id` y opcionalmente por estado, con paginación. |
| REQ18 | Validaciones internas para autenticación | El sistema expone validación interna de existencia y verificación de credenciales para consumo inter-servicio. |
| REQ19 | Seguridad transversal (sesión, permisos, auditoría y notificación) | El sistema valida sesión/permisos en endpoints protegidos, registra auditoría y emite notificaciones asíncronas en eventos críticos. |

### 2.1 Detalle de requisitos funcionales

**REQ1 - Crear usuario**
- Entradas: `username`, `email`, `password_encrypted` (o `password_plana` en debug), `rol_id`.
- Reglas: username mínimo 3 caracteres, email válido, username/email únicos, rol válido.
- Resultado: usuario creado en estado `activo` con contraseña almacenada como hash bcrypt.

**REQ2 - Consultar usuario por ID**
- Entrada: `usuario_id`.
- Reglas: requiere sesión válida y permiso `USR_READ`.
- Resultado: datos públicos del usuario o `404` si no existe.

**REQ3 - Consultar usuario por email**
- Entrada: `email`.
- Reglas: si la llamada proviene de ms-autenticación (token de app válido), puede retornar hash; en caso contrario requiere sesión y permiso `USR_READ`.
- Resultado: usuario encontrado o `404`.

**REQ4 - Actualizar datos básicos de usuario**
- Entradas: `usuario_id` y al menos un campo entre `username`, `email`, `rol_id`.
- Reglas: valida duplicados de username/email y existencia/estado de rol.
- Resultado: usuario actualizado o error de validación.

**REQ5 - Cambiar estado de usuario**
- Entradas: `usuario_id`, `estado_nuevo`, `motivo`.
- Reglas: estado permitido (`activo`, `inactivo`, `suspendido`), motivo obligatorio.
- Resultado: cambio de estado en transacción atómica con registro en historial.

**REQ6 - Desactivar usuario**
- Entradas: `usuario_id`, `motivo`.
- Reglas: requiere permiso `USR_DELETE`.
- Resultado: estado cambia a `inactivo`, con trazabilidad y notificación.

**REQ7 - Reactivar usuario**
- Entradas: `usuario_id`, `motivo`.
- Reglas: requiere permiso `USR_REACTIVATE`.
- Resultado: estado cambia a `activo`, con trazabilidad y notificación.

**REQ8 - Cambiar contraseña**
- Entradas: `usuario_id`, contraseña actual cifrada y nueva contraseña cifrada.
- Reglas: solo el propio usuario puede ejecutar la acción; verifica contraseña actual; aplica política mínima (8+ caracteres, mayúscula, minúscula y número).
- Resultado: contraseña actualizada y alerta de seguridad.

**REQ9 - Consultar perfil extendido**
- Entrada: `usuario_id`.
- Reglas: requiere permiso `USR_PROFILE_READ` (excepto integración autorizada de notificaciones).
- Resultado: perfil extendido del usuario o error si no existe.

**REQ10 - Crear/actualizar perfil extendido**
- Entradas: datos de documento, identidad, contacto y ubicación.
- Reglas: edad mínima 14 años y validaciones de esquema.
- Resultado: perfil creado o actualizado.

**REQ11 - Consultar preferencias de notificación**
- Entrada: `usuario_id`.
- Reglas: requiere permiso `USR_PREFERENCES_READ` (o token de app autorizado).
- Resultado: preferencias actuales del usuario.

**REQ12 - Actualizar preferencias de notificación**
- Entrada: configuración de canales y horario de no molestar.
- Reglas: si se define horario, deben venir inicio y fin, e inicio < fin.
- Resultado: preferencias creadas/actualizadas.

**REQ13 - Consultar historial de estados**
- Entrada: `usuario_id`.
- Reglas: requiere permiso `USR_HISTORY_READ`.
- Resultado: lista cronológica de cambios de estado.

**REQ14 - Consultar catálogo de tipos de documento**
- Entrada: sin parámetros de negocio.
- Reglas: requiere sesión y permiso `USR_READ`.
- Resultado: tipos de documento activos.

**REQ15 - Búsqueda avanzada de usuarios**
- Entradas: filtros opcionales y paginación (`pagina`, `items_por_pagina`).
- Reglas: `pagina >= 1`, `items_por_pagina` dentro de rango permitido.
- Resultado: resultados paginados con totales y metadatos.

**REQ16 - Estadísticas de usuarios por estado**
- Entrada: sin parámetros de negocio.
- Reglas: requiere permiso `USR_STATS_READ`.
- Resultado: total general y conteo por estado.

**REQ17 - Listar usuarios por rol**
- Entradas: `rol_id`, filtro opcional `estado`, paginación.
- Reglas: requiere permiso `USR_LIST_BY_ROLE`.
- Resultado: lista paginada de usuarios para el rol.

**REQ18 - Validaciones internas para autenticación**
- Entradas: `usuario_id` para existencia y (`username`, `encrypted_password`) para credenciales.
- Reglas: uso interno entre microservicios.
- Resultado: existencia/estado del usuario y validación de credenciales (activo/bloqueado/inválido).

**REQ19 - Seguridad transversal (sesión, permisos, auditoría y notificación)**
- Autenticación: validación de sesión contra ms-autenticación en endpoints protegidos.
- Autorización: validación de permisos por rol contra ms-roles.
- Auditoría: envío asíncrono de logs de operación a ms-auditoría con respaldo local en falla.
- Notificación: publicación asíncrona de eventos relevantes (bienvenida, cambio de estado, alerta de seguridad).
