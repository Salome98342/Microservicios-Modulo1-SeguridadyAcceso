# Requisitos Funcionales Detallados: ms-usuarios [USR]

Documento consolidado desde `documentacion/requisitos/especificacion_requisitos.md` y `documentacion/rutas_y_endpoints.md`.

## Matriz de trazabilidad (REQ ↔ Endpoint principal)

| REQ | Endpoint(s) principal(es) |
|---|---|
| REQ1 | `POST /api/v1/users` |
| REQ2 | `GET /api/v1/users/{usuario_id}` |
| REQ3 | `GET /api/v1/users/by-email/{email}` |
| REQ4 | `PUT /api/v1/users/{usuario_id}` |
| REQ5 | `PATCH /api/v1/users/{usuario_id}/state` |
| REQ6 | `DELETE /api/v1/users/{usuario_id}`, `POST /api/v1/users/{usuario_id}/reactivate` |
| REQ7 | `PATCH /api/v1/users/{usuario_id}/password` |
| REQ8 | `GET/PUT /api/v1/users/{usuario_id}/profile` |
| REQ9 | `GET/PUT /api/v1/users/{usuario_id}/notification-preferences` |
| REQ10 | `GET /api/v1/users/{usuario_id}/state-history` |
| REQ11 | `GET /api/v1/document-types` |
| REQ12 | `GET /api/v1/users` (filtros + paginación) |
| REQ13 | `GET /api/v1/users/stats/by-state` |
| REQ14 | `GET /api/v1/users/by-role/{rol_id}` |
| REQ15 | `GET /api/v1/users/{usuario_id}/validate`, `POST /api/v1/internal/users/credentials/verify` |

## Detalle por requisito

### REQ1 — Crear usuario
- **Precondiciones:** sesión activa, permiso `USR_CREATE`, `username/email` únicos, `rol_id` válido.
- **Flujo normal:** valida sesión/permisos, valida unicidad y rol, procesa contraseña, crea usuario `activo`, audita y notifica asíncrono.
- **Alternos:** duplicidad (`409`), rol inválido/no disponible (`4xx/503`), validación de contraseña (`400`).
- **Postcondición:** usuario creado sin exponer `password_hash`.

### REQ2 — Consultar usuario por ID
- **Precondiciones:** sesión activa y `USR_READ`.
- **Flujo normal:** consulta por ID y retorna datos públicos.
- **Alternos:** usuario no existe (`404`).
- **Postcondición:** respuesta estándar con datos no sensibles.

### REQ3 — Consultar usuario por email
- **Precondiciones:** email válido; si no es integración interna, sesión activa con `USR_READ`.
- **Flujo normal:** distingue consumo interno (`X-App-Token`) vs externo.
- **Alternos:** email no encontrado (`404`).
- **Postcondición:** hash solo para integración interna autorizada.

### REQ4 — Actualizar datos básicos
- **Precondiciones:** sesión activa, `USR_UPDATE`, usuario objetivo existente.
- **Flujo normal:** valida campos enviados, colisiones y rol; actualiza registro.
- **Alternos:** sin campos (`400`), duplicidad (`409`), rol inválido (`4xx`).
- **Postcondición:** usuario actualizado.

### REQ5 — Cambiar estado de usuario
- **Precondiciones:** sesión activa, `USR_CHANGE_STATE`, estado destino válido, motivo obligatorio.
- **Flujo normal:** actualización transaccional + inserción en historial + notificación.
- **Alternos:** estado inválido/mismo estado/sin motivo (`400`), usuario no existe (`404`).
- **Postcondición:** estado actualizado y trazabilidad persistida.

### REQ6 — Desactivar y reactivar usuario
- **Precondiciones:** `USR_DELETE` (desactivar) o `USR_REACTIVATE` (reactivar), motivo requerido.
- **Flujo normal:** cambia estado (`inactivo`/`activo`) reutilizando flujo transaccional de historial.
- **Alternos:** usuario no existe o cambio no aplicable (`404/400`).
- **Postcondición:** operación de estado completada sin borrado físico de datos.

### REQ7 — Gestionar contraseña
- **Precondiciones:** sesión activa; sólo propia contraseña o permiso administrativo; payload cifrado.
- **Flujo normal:** valida identidad, descifra, verifica actual, valida política, actualiza hash.
- **Alternos:** intento sobre otro usuario (`403`), contraseña actual incorrecta (`401`), política inválida (`400`).
- **Postcondición:** contraseña actualizada de forma segura.

### REQ8 — Gestionar perfil extendido
- **Precondiciones:** usuario existente; permisos `USR_PROFILE_READ`/`USR_PROFILE_UPDATE` o token interno permitido.
- **Flujo normal:** consulta y/o upsert del perfil con validación de tipo de documento y unicidad.
- **Alternos:** usuario/perfil no encontrado (`404`), documento inválido o duplicado (`400/409`).
- **Postcondición:** perfil asociado al usuario.

### REQ9 — Gestionar preferencias de notificación
- **Precondiciones:** usuario existente; permisos `USR_PREFERENCES_READ`/`USR_PREFERENCES_UPDATE` o token interno.
- **Flujo normal:** consulta (incluye defaults si no existe) y actualización parcial.
- **Alternos:** usuario no existe (`404`), horario inválido (`400`).
- **Postcondición:** preferencias guardadas y disponibles.

### REQ10 — Consultar historial de estados
- **Precondiciones:** sesión activa, `USR_HISTORY_READ`.
- **Flujo normal:** retorna historial cronológico por usuario.
- **Alternos:** sin historial retorna lista vacía con mensaje informativo (`200`).
- **Postcondición:** trazabilidad consultable.

### REQ11 — Consultar catálogo de tipos de documento
- **Precondiciones:** sesión activa con `USR_READ`.
- **Flujo normal:** lista tipos activos.
- **Alternos:** sin datos retorna lista vacía (`200`).
- **Postcondición:** catálogo de referencia disponible.

### REQ12 — Búsqueda avanzada y paginación
- **Precondiciones:** sesión activa, `USR_SEARCH`, `pagina>=1`, `items_por_pagina<=100`.
- **Flujo normal:** aplica filtros opcionales y retorna metadatos de paginación.
- **Alternos:** parámetros inválidos (`400`).
- **Postcondición:** resultados paginados consistentes.

### REQ13 — Estadísticas por estado
- **Precondiciones:** sesión activa, `USR_STATS_READ`.
- **Flujo normal:** calcula conteos por estado y total.
- **Alternos:** sin usuarios retorna métricas en cero.
- **Postcondición:** estadísticas listas para consumo administrativo.

### REQ14 — Listar usuarios por rol
- **Precondiciones:** sesión activa, `USR_LIST_BY_ROLE`, `rol_id` válido.
- **Flujo normal:** consulta por rol, filtro opcional de estado y paginación.
- **Alternos:** sin coincidencias retorna lista vacía (`200`).
- **Postcondición:** listado por rol disponible.

### REQ15 — Validaciones internas de existencia y credenciales
- **Precondiciones:** consumo inter-servicio.
- **Flujo normal:** validar existencia (`/validate`) y verificar credenciales internas (`/internal/users/credentials/verify`).
- **Alternos:** credenciales inválidas (`401`), usuario bloqueado/no activo (`423`).
- **Postcondición:** ms consumidores reciben decisión de validación.
