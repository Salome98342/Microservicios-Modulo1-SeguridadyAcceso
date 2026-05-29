# Diseño de Integración: ms-usuarios [USR]

Documento actualizado con base en:
- `documentacion/rutas_y_endpoints.md`
- `documentacion/arquitectura_y_diagramas.md`
- `documentacion/requisitos/especificacion_requisitos.md`

## 1. Vista general de integración

`ms-usuarios` opera como proveedor de datos de usuario para el dominio de Seguridad y Acceso y como consumidor de servicios transversales de autenticación, autorización, notificaciones y auditoría.

## 2. Contratos de comunicación saliente (ms-usuarios consume)

### 2.1 ms-autenticacion
- **Propósito:** validar sesión activa.
- **Uso:** antes de ejecutar endpoints protegidos.
- **Entrada mínima:** token de usuario.
- **Salida esperada:** `user_id`, `rol_id`, sesión válida/invalidada.
- **Errores manejados:** `401`, timeout/servicio no disponible.

### 2.2 ms-roles
- **Propósito:** validar permisos por funcionalidad y validar existencia de `rol_id`.
- **Uso:** autorización por endpoint y alta/edición de usuario.
- **Entrada mínima:** `rol_id` + código de permiso.
- **Errores manejados:** `403`, `404` de rol, timeout.

### 2.3 ms-notificaciones
- **Propósito:** envío asíncrono de eventos de usuario (ej. bienvenida, cambio de estado).
- **Uso:** fire-and-forget posterior a operación principal.
- **Comportamiento:** no bloquea respuesta al cliente.

### 2.4 ms-auditoria
- **Propósito:** registro de auditoría en JSON.
- **Uso:** al finalizar operaciones (éxito/error).
- **Comportamiento:** envío asíncrono; ante fallo se mantiene resiliencia con respaldo local.

## 3. Contratos de comunicación entrante (ms-usuarios expone)

### 3.1 Consumo externo/autenticado
- Gestión de usuarios: crear, consultar, actualizar, buscar, cambiar estado, reactivar, estadísticas.
- Gestión de perfil: obtener y crear/actualizar.
- Gestión de preferencias: obtener y actualizar.
- Historial de estado y tipos de documento.

### 3.2 Consumo interno entre microservicios
- `GET /users/{usuario_id}/validate` (validación de existencia).
- `POST /internal/users/credentials/verify` (validación interna de credenciales).
- `GET /users/by-email/{email}` con token interno para ms-autenticación (incluye hash cuando aplica).
- consulta de perfil/preferencias por ms-notificaciones usando token de aplicación.

## 4. Seguridad de integración

### 4.1 Headers
- `Authorization: ****** para rutas protegidas.
- `X-App-Token` para integración inter-servicio.
- `X-Request-ID` para trazabilidad distribuida.

### 4.2 Reglas
- Validación de sesión y permiso previa a la lógica funcional.
- Token interno obligatorio en endpoints internos.
- Respuesta estándar uniforme en todos los contratos.

## 5. Trazabilidad y observabilidad

- `request_id` se propaga entre servicios; si no viene, se genera.
- Log de auditoría estructurado (JSON): timestamp, request_id, microservicio, funcionalidad, método, código, duración, usuario, detalle.
- Integraciones no críticas son no bloqueantes (notificaciones/auditoría).

## 6. Flujos integrados críticos

### 6.1 Crear usuario
1. Validar sesión en ms-autenticacion.
2. Validar permiso y rol en ms-roles.
3. Crear usuario en base local.
4. Disparar notificación de bienvenida en ms-notificaciones.
5. Registrar auditoría en ms-auditoria.

### 6.2 Cambio de estado (transaccional)
1. Validar sesión y permiso.
2. Actualizar estado + registrar historial en una transacción.
3. Notificar cambio de estado.
4. Registrar auditoría.

## 7. Endpoints de integración principales

- `POST /users`
- `GET /users/{usuario_id}`
- `GET /users/by-email/{email}`
- `PUT /users/{usuario_id}`
- `PATCH /users/{usuario_id}/state`
- `DELETE /users/{usuario_id}`
- `POST /users/{usuario_id}/reactivate`
- `PATCH /users/{usuario_id}/password`
- `GET/PUT /users/{usuario_id}/profile`
- `GET/PUT /users/{usuario_id}/notification-preferences`
- `GET /users/{usuario_id}/state-history`
- `GET /document-types`
- `GET /users` (búsqueda)
- `GET /users/by-role/{rol_id}`
- `GET /users/stats/by-state`
- `GET /users/{usuario_id}/validate`
- `POST /internal/users/credentials/verify`
