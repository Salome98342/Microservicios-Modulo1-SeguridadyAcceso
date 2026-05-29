# Modelo de Datos: ms-usuarios [USR]

Documento actualizado a partir de:
- `documentacion/modelo_relacional.md`
- `ms_usuario/init_db.sql`

## 1. Resumen

- **Motor:** PostgreSQL
- **Esquema funcional:** 5 tablas principales
- **Objetivo:** gestionar usuarios, perfiles, preferencias, historial y tipos de documento.

## 2. Entidades

### 2.1 `usr_usuarios`
Campos principales: `id`, `username`, `email`, `password_hash`, `estado`, `rol_id`, `created_at`, `updated_at`.

Reglas:
- `username` y `email` únicos.
- `estado` válido: `activo`, `inactivo`, `suspendido`, `eliminado`.
- `rol_id` se valida contra ms-roles a nivel aplicación.

### 2.2 `usr_perfiles`
Campos principales: identificación, nombres/apellidos, fecha de nacimiento, género, dirección, contactos, biografía.

Reglas:
- relación 1:1 con `usr_usuarios` (`usuario_id` único).
- `tipo_documento_id` referencia `usr_tipos_documento`.
- `numero_documento` único.
- validaciones de dominio: edad mínima y género permitido en capa de aplicación/modelo.

### 2.3 `usr_preferencias_notificacion`
Campos: `notif_email`, `notif_sms`, `notif_push`, `canal_preferido`, horario no molestar.

Reglas:
- relación 1:1 con `usr_usuarios` (`usuario_id` único).
- `canal_preferido` en (`email`, `sms`, `push`).
- consistencia de horario de no molestar validada en servicios.

### 2.4 `usr_historial_estados`
Campos: `usuario_id`, `estado_anterior`, `estado_nuevo`, `motivo`, `usuario_modificador_id`, `created_at`.

Reglas:
- relación N:1 hacia `usr_usuarios`.
- `estado_nuevo` validado contra estados permitidos.
- alimentado por cambios de estado transaccionales.

### 2.5 `usr_tipos_documento`
Catálogo de tipos de documento con `codigo`, `nombre`, `descripcion`, `activo`.

Reglas:
- `codigo` único.
- se consultan sólo tipos activos para formularios de perfil.

## 3. Relaciones y claves

- `usr_perfiles.usuario_id -> usr_usuarios.id` (1:1, `ON DELETE CASCADE`).
- `usr_perfiles.tipo_documento_id -> usr_tipos_documento.id` (N:1).
- `usr_preferencias_notificacion.usuario_id -> usr_usuarios.id` (1:1, `ON DELETE CASCADE`).
- `usr_historial_estados.usuario_id -> usr_usuarios.id` (N:1, `ON DELETE CASCADE`).

## 4. Índices relevantes

- Usuarios: `idx_usuarios_username`, `idx_usuarios_email`, `idx_usuarios_estado`, `idx_usuarios_rol_id`.
- Perfiles: `idx_perfiles_usuario_id`, `idx_perfiles_tipo_documento_id`, `idx_perfiles_numero_documento`, `idx_perfiles_ciudad`, `idx_perfiles_primer_nombre`, `idx_perfiles_primer_apellido`.
- Preferencias: `idx_preferencias_usuario_id`.
- Historial: `idx_historial_usuario_id`, `idx_historial_created_at`.
- Tipos documento: `idx_tipos_documento_codigo`, `idx_tipos_documento_activo`.

## 5. Integridad y comportamiento de persistencia

- Restricciones `CHECK` para estados, género y canal preferido.
- Triggers para actualización automática de `updated_at`.
- Integridad referencial local con FK internas.
- Integridad entre microservicios (ej. `rol_id`) resuelta por validación en lógica de negocio.

## 6. Datos semilla

Catálogo inicial recomendado para `usr_tipos_documento`:
`CC` (Cédula de Ciudadanía), `PA` (Pasaporte), `CE` (Cédula de Extranjería), `TI` (Tarjeta de Identidad), `PEP` (Permiso de Entrada y Permanencia), `NIT` (Número de Identificación Tributaria), `OTR` (Otro tipo de documento).
