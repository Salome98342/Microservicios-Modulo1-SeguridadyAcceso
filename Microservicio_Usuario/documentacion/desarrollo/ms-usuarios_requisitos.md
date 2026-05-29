# Microservicio: ms-usuarios [USR]

## Documento de Requisitos Funcionales (Actualizado)

Fuente principal: `documentacion/requisitos/especificacion_requisitos.md`.

## 1. Alcance

El microservicio **ms-usuarios** gestiona:
- usuarios y credenciales (hash bcrypt),
- perfiles extendidos,
- preferencias de notificación,
- historial de cambios de estado,
- catálogo de tipos de documento,
- validaciones internas para integración con otros microservicios.

## 2. Matriz de requisitos funcionales vigentes

| Código | Nombre | Resumen |
|---|---|---|
| REQ1 | Crear usuario | Crear usuario con `username`, `email`, contraseña y `rol_id` válido. |
| REQ2 | Consultar usuario por ID | Obtener datos públicos por `usuario_id`. |
| REQ3 | Consultar usuario por email | Consulta por email; para integración interna puede incluir `password_hash`. |
| REQ4 | Actualizar datos básicos | Actualizar `username`, `email` y/o `rol_id` con validaciones de colisión y rol. |
| REQ5 | Cambiar estado de usuario | Cambiar a `activo`, `inactivo`, `suspendido` o `eliminado` con motivo e historial. |
| REQ6 | Desactivar y reactivar usuario | Soft delete (`inactivo`) y reactivación (`activo`) con trazabilidad. |
| REQ7 | Gestionar contraseña | Cambio de contraseña propia con validación de actual y política de seguridad. |
| REQ8 | Gestionar perfil extendido | Consultar y crear/actualizar perfil por usuario. |
| REQ9 | Gestionar preferencias | Consultar/actualizar canales y horario de no molestar. |
| REQ10 | Consultar historial de estados | Consultar trazabilidad cronológica de cambios de estado. |
| REQ11 | Consultar tipos de documento | Listar catálogo activo para uso en perfiles. |
| REQ12 | Búsqueda avanzada y paginación | Filtros por nombre, documento, email, estado y ciudad con paginación. |
| REQ13 | Estadísticas por estado | Métricas agregadas por estado y total de usuarios. |
| REQ14 | Listar usuarios por rol | Listado por `rol_id`, con filtro opcional de estado y paginación. |
| REQ15 | Validaciones internas | Validar existencia y credenciales para integraciones internas. |

## 3. Reglas de negocio y seguridad

1. Validación obligatoria de sesión y permiso por funcionalidad en endpoints públicos.
2. Contraseñas en tránsito cifradas (AES-256) y almacenamiento en hash bcrypt.
3. `request_id` obligatorio para trazabilidad (se reutiliza o genera automáticamente).
4. Auditoría JSON asíncrona (no bloqueante) con fallback local si falla ms-auditoría.
5. Estados funcionales para operación: `activo`, `inactivo`, `suspendido`; adicionalmente el estado técnico `eliminado` se usa en flujos de soft delete registrados en base de datos.
6. Formato de respuesta estándar: `request_id`, `status`, `statusCode`, `data`, `message`.

## 4. Datos clave del dominio

- `usr_usuarios`: username, email, password_hash, estado, rol_id.
- `usr_perfiles`: información personal extendida y contacto.
- `usr_preferencias_notificacion`: canales y horario no molestar.
- `usr_historial_estados`: trazabilidad de cambios de estado.
- `usr_tipos_documento`: catálogo activo de tipos de documento.

## 5. Dependencias

### Servicios que ms-usuarios consume
- **ms-autenticacion:** validación de sesión y flujos internos de credenciales.
- **ms-roles:** validación de permisos y consistencia de `rol_id`.
- **ms-notificaciones:** envío asíncrono de notificaciones (bienvenida/cambios de estado).
- **ms-auditoria:** envío asíncrono de logs operativos.

### Consumidores de ms-usuarios
- **ms-autenticacion:** consulta por email con hash y verificación de credenciales.
- **ms-programas:** validación interna de existencia de usuario.
- **ms-notificaciones:** consulta de perfil y preferencias para entrega de mensajes.

## 6. Permisos funcionales relevantes

`USR_CREATE`, `USR_READ`, `USR_UPDATE`, `USR_DELETE`, `USR_SEARCH`, `USR_PROFILE_READ`, `USR_PROFILE_UPDATE`, `USR_HISTORY_READ`, `USR_CHANGE_STATE`, `USR_REACTIVATE`, `USR_PREFERENCES_READ`, `USR_PREFERENCES_UPDATE`, `USR_STATS_READ`, `USR_LIST_BY_ROLE`, `USR_ADMIN_PASSWORD`.
