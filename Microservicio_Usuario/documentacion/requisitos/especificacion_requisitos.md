# Especificación de Requisitos

## 1. Introducción

Este documento consolida los requisitos funcionales del **Microservicio de Usuarios** a partir del comportamiento implementado en el código (`ms_usuario`), sus rutas, servicios y capa de persistencia.  
El alcance se limita a funcionalidades disponibles para gestión de usuarios, perfiles, preferencias de notificación, historial de estados, tipos de documento y validaciones internas de autenticación.

## 2. Requisitos Funcionales a Nivel del Sistema

Declaración de requisitos funcionales del sistema (no expresados como casos de uso), tomando únicamente comportamiento verificable en el código del microservicio.
La matriz y las tablas de detalle mantienen trazabilidad con endpoints, validaciones y reglas de negocio implementadas.

### 2.1 Matriz de requisitos funcionales

| Código | Nombre | Descripción |
|---|---|---|
| REQ1 | Crear usuario | El cliente crea el usuario con `username`, `email`, contraseña y `rol_id`; el sistema valida unicidad y registra estado inicial `activo`. |
| REQ2 | Consultar usuario por ID | El sistema permite consultar datos públicos del usuario por identificador. |
| REQ3 | Consultar usuario por email | El sistema permite consulta por correo; para integración interna con autenticación puede incluir `password_hash`. |
| REQ4 | Actualizar datos básicos de usuario | El sistema permite actualizar `username`, `email` y/o `rol_id`, validando colisiones y reglas de rol. |
| REQ5 | Cambiar estado de usuario | El sistema permite cambiar estado (`activo`, `inactivo`, `suspendido`) registrando motivo y auditoría. |
| REQ6 | Desactivar y reactivar usuario | El sistema permite desactivación lógica y reactivación, con notificación y trazabilidad. |
| REQ7 | Gestionar contraseña | El sistema permite actualizar contraseña del propio usuario validando contraseña actual y política de seguridad. |
| REQ8 | Gestionar perfil extendido | El sistema permite crear/actualizar y consultar perfil extendido asociado a usuario. |
| REQ9 | Gestionar preferencias de notificación | El sistema permite consultar y actualizar preferencias por usuario, incluyendo horarios de no molestar. |
| REQ10 | Consultar historial de estados | El sistema permite consultar el historial cronológico de cambios de estado por usuario. |
| REQ11 | Consultar catálogo de tipos de documento | El sistema expone tipos de documento activos para uso en perfiles. |
| REQ12 | Búsqueda avanzada y paginación | El sistema permite búsqueda de usuarios por filtros (nombre, documento, email, estado, ciudad) con paginación. |
| REQ13 | Estadísticas por estado | El sistema entrega total de usuarios y distribución por estado. |
| REQ14 | Listar usuarios por rol | El sistema permite consultar usuarios filtrando por rol y opcionalmente por estado. |
| REQ15 | Validación interna de existencia y credenciales | El sistema soporta endpoints internos para validar existencia de usuario y verificación de credenciales. |

### 2.2 Tablas de detalle por requisito funcional

#### 2.2.1 REQ1 — Crear usuario

| Código | REQ1 | |
|---|---|---|
| Nombre | Crear usuario | |
| Actores | Cliente, administrador | |
| Descripción | Permite registrar un nuevo usuario con `username`, `email`, contraseña cifrada y `rol_id` válido | |
| Precondición | Sesión activa con permiso `USR_CREATE`; `username` y `email` no registrados; contraseña suministrada (`password_encrypted` o `password_plana` solo en `DEBUG_MODE`) | |
| Secuencia normal | Paso | Descripción |
| | 1 | El cliente envía `POST /users` con los datos requeridos |
| | 2 | El sistema valida sesión, permiso, unicidad de `username`/`email` y validez de `rol_id` |
| | 3 | El sistema procesa la contraseña, genera `password_hash`, crea el usuario con estado inicial `activo` y retorna `201` |
| | 4 | El sistema registra auditoría y dispara notificación de bienvenida de forma asíncrona |
| Secuencia alterna | Paso | Descripción |
| | 2.1 | Si `username` o `email` ya existen, el sistema rechaza la solicitud |
| | 2.2 | Si `rol_id` es inválido o el servicio de roles no está disponible, el sistema rechaza la operación |
| | 3.1 | Si la contraseña no puede procesarse, el sistema responde error de validación |
| Postcondición | El usuario queda registrado y puede usar el sistema | |
| Comentarios | El endpoint no expone `password_hash` y mantiene trazabilidad por `request_id` | |

#### 2.2.2 REQ2 — Consultar usuario por ID
| Código | REQ2 | |
|---|---|---|
| Nombre | Consultar usuario por ID | |
| Actores | Cliente, administrador | |
| Descripción | Permite recuperar datos públicos de un usuario por su identificador | |
| Precondición | Sesión activa con permiso `USR_READ` y `usuario_id` válido | |
| Secuencia normal | Paso | Descripción |
| | 1 | El cliente envía la solicitud `GET /users/{usuario_id}` con token de autorización |
| | 2 | El sistema valida sesión y permiso `USR_READ` |
| | 3 | El sistema consulta el usuario por ID y retorna datos públicos |
| Secuencia alterna | Paso | Descripción |
| | 3.1 | Si el usuario no existe, el sistema responde `404 Usuario no encontrado` |
| Postcondición | El cliente obtiene el usuario sin exponer `password_hash` | |
| Comentarios | El endpoint registra auditoría de la consulta | |

#### 2.2.3 REQ3 — Consultar usuario por email
| Código | REQ3 | |
|---|---|---|
| Nombre | Consultar usuario por email | |
| Actores | Cliente, administrador, ms-autenticación | |
| Descripción | Permite consultar un usuario por correo electrónico; para ms-autenticación puede incluir `password_hash` | |
| Precondición | Email válido; si no es integración interna, sesión activa con permiso `USR_READ` | |
| Secuencia normal | Paso | Descripción |
| | 1 | El cliente o servicio interno envía `GET /users/by-email/{email}` |
| | 2 | El sistema identifica si viene `X-App-Token` de ms-autenticación |
| | 3 | Si es ms-autenticación retorna usuario con hash; en caso contrario valida sesión/permiso y retorna datos públicos |
| Secuencia alterna | Paso | Descripción |
| | 3.1 | Si no existe usuario para el email, el sistema responde `404 Usuario no encontrado` |
| Postcondición | La consulta por email queda disponible según el nivel de acceso | |
| Comentarios | El hash de contraseña solo se expone en integración interna autorizada | |

#### 2.2.4 REQ4 — Actualizar datos básicos de usuario
| Código | REQ4 | |
|---|---|---|
| Nombre | Actualizar datos básicos de usuario | |
| Actores | Administrador | |
| Descripción | Permite actualizar `username`, `email` y/o `rol_id` de un usuario existente | |
| Precondición | Sesión activa con permiso `USR_UPDATE`; usuario objetivo existente; al menos un campo a actualizar | |
| Secuencia normal | Paso | Descripción |
| | 1 | El administrador envía `PUT /users/{usuario_id}` con campos a modificar |
| | 2 | El sistema valida sesión, permiso, existencia del usuario y colisiones de `username`/`email` |
| | 3 | Si se envía `rol_id`, el sistema valida el rol en servicio externo |
| | 4 | El sistema persiste cambios y responde con el usuario actualizado |
| Secuencia alterna | Paso | Descripción |
| | 2.1 | Si no se envían campos, el sistema rechaza la solicitud |
| | 2.2 | Si hay duplicidad o el rol es inválido, el sistema rechaza la actualización |
| Postcondición | Datos básicos del usuario quedan actualizados en persistencia | |
| Comentarios | Mantiene respuesta pública sin información sensible | |

#### 2.2.5 REQ5 — Cambiar estado de usuario
| Código | REQ5 | |
|---|---|---|
| Nombre | Cambiar estado de usuario | |
| Actores | Administrador | |
| Descripción | Permite cambiar el estado del usuario a `activo`, `inactivo` o `suspendido` con motivo | |
| Precondición | Sesión activa con permiso `USR_CHANGE_STATE`; usuario existente; estado nuevo válido; motivo diligenciado | |
| Secuencia normal | Paso | Descripción |
| | 1 | El administrador envía `PATCH /users/{usuario_id}/state` con `estado_nuevo` y `motivo` |
| | 2 | El sistema valida sesión, permiso y estado destino permitido |
| | 3 | El sistema actualiza estado y registra historial en una transacción atómica |
| | 4 | El sistema notifica cambio de estado y responde éxito |
| Secuencia alterna | Paso | Descripción |
| | 2.1 | Si el estado es inválido, igual al actual o no hay motivo, el sistema rechaza la solicitud |
| | 2.2 | Si el usuario no existe, el sistema responde `404` |
| Postcondición | Estado actualizado con historial y auditoría | |
| Comentarios | Estados válidos definidos en servicio: `activo`, `inactivo`, `suspendido` | |

#### 2.2.6 REQ6 — Desactivar y reactivar usuario
| Código | REQ6 | |
|---|---|---|
| Nombre | Desactivar y reactivar usuario | |
| Actores | Administrador | |
| Descripción | Permite desactivación lógica (`inactivo`) y reactivación (`activo`) con motivo y trazabilidad | |
| Precondición | Sesión activa con permisos `USR_DELETE` (desactivar) o `USR_REACTIVATE` (reactivar); usuario existente; motivo diligenciado | |
| Secuencia normal | Paso | Descripción |
| | 1 | Para desactivar, el administrador invoca `DELETE /users/{usuario_id}` con motivo |
| | 2 | Para reactivar, el administrador invoca `POST /users/{usuario_id}/reactivate` con motivo |
| | 3 | El sistema cambia el estado mediante flujo transaccional de historial |
| | 4 | El sistema genera notificación de cambio de estado y auditoría |
| Secuencia alterna | Paso | Descripción |
| | 3.1 | Si el usuario no existe o no aplica el cambio de estado, el sistema rechaza la operación |
| | 3.2 | Si falta motivo, el sistema responde error de validación |
| Postcondición | Usuario queda desactivado o reactivado con trazabilidad completa | |
| Comentarios | No elimina físicamente el usuario (soft delete) | |

#### 2.2.7 REQ7 — Gestionar contraseña
| Código | REQ7 | |
|---|---|---|
| Nombre | Gestionar contraseña | |
| Actores | Usuario autenticado | |
| Descripción | Permite al usuario cambiar su contraseña enviando contraseña actual y nueva en formato cifrado | |
| Precondición | Sesión activa; el usuario solo puede cambiar su propia contraseña; campos cifrados requeridos | |
| Secuencia normal | Paso | Descripción |
| | 1 | El usuario invoca `PATCH /users/{usuario_id}/password` con `password_actual_encrypted` y `password_nueva_encrypted` |
| | 2 | El sistema valida que `usuario_id` coincida con la sesión autenticada |
| | 3 | El sistema descifra, valida contraseña actual y verifica política de seguridad de la nueva contraseña |
| | 4 | El sistema guarda nuevo `password_hash` y registra alerta de seguridad |
| Secuencia alterna | Paso | Descripción |
| | 2.1 | Si intenta cambiar contraseña de otro usuario, el sistema responde `403` |
| | 3.1 | Si falla el descifrado o la contraseña actual es incorrecta, el sistema rechaza la solicitud |
| | 3.2 | Si la nueva contraseña no cumple política (8+ caracteres, mayúscula, minúscula y número), el sistema rechaza la solicitud |
| Postcondición | Contraseña actualizada de forma segura en hash bcrypt | |
| Comentarios | Nunca se persiste ni retorna contraseña en texto plano | |

#### 2.2.8 REQ8 — Gestionar perfil extendido
| Código | REQ8 | |
|---|---|---|
| Nombre | Gestionar perfil extendido | |
| Actores | Usuario autorizado, administrador, ms-notificaciones (solo consulta con token interno) | |
| Descripción | Permite consultar y crear/actualizar el perfil extendido asociado a un usuario | |
| Precondición | Usuario objetivo existente; para consulta/edición externa se requiere sesión y permiso (`USR_PROFILE_READ` o `USR_PROFILE_UPDATE`) | |
| Secuencia normal | Paso | Descripción |
| | 1 | Para consulta, se invoca `GET /users/{usuario_id}/profile` |
| | 2 | Para edición, se invoca `PUT /users/{usuario_id}/profile` con datos completos del perfil |
| | 3 | El sistema valida existencia del usuario, tipo de documento activo y unicidad de número de documento |
| | 4 | El sistema retorna perfil obtenido o actualizado (creado si no existía) |
| Secuencia alterna | Paso | Descripción |
| | 3.1 | Si usuario/perfil no existe para consulta, el sistema responde `404` |
| | 3.2 | Si tipo de documento es inválido o número ya registrado, el sistema rechaza la operación |
| Postcondición | Perfil extendido queda asociado al usuario con integridad de datos | |
| Comentarios | La operación `PUT` crea o actualiza según exista perfil previo | |

#### 2.2.9 REQ9 — Gestionar preferencias de notificación
| Código | REQ9 | |
|---|---|---|
| Nombre | Gestionar preferencias de notificación | |
| Actores | Usuario autorizado, ms-notificaciones (solo consulta con token interno) | |
| Descripción | Permite consultar y actualizar preferencias de notificación y horarios de no molestar | |
| Precondición | Usuario existente; para consumo externo se requiere sesión y permiso (`USR_PREFERENCES_READ` o `USR_PREFERENCES_UPDATE`) | |
| Secuencia normal | Paso | Descripción |
| | 1 | Para consulta se invoca `GET /users/{usuario_id}/notification-preferences` |
| | 2 | Si no hay configuración previa, el sistema retorna preferencias por defecto |
| | 3 | Para actualización se invoca `PUT /users/{usuario_id}/notification-preferences` con campos parciales |
| | 4 | El sistema valida consistencia de horarios y persiste configuración |
| Secuencia alterna | Paso | Descripción |
| | 1.1 | Si el usuario no existe, el sistema responde `404` |
| | 4.1 | Si horarios son inválidos (inicio/fin incompletos o inicio >= fin), el sistema rechaza la actualización |
| Postcondición | Preferencias de notificación quedan disponibles y actualizadas | |
| Comentarios | Soporta `notif_email`, `notif_sms`, `notif_push`, `canal_preferido` y ventana de no molestar | |

#### 2.2.10 REQ10 — Consultar historial de estados
| Código | REQ10 | |
|---|---|---|
| Nombre | Consultar historial de estados | |
| Actores | Administrador | |
| Descripción | Permite consultar el historial de cambios de estado de un usuario | |
| Precondición | Sesión activa con permiso `USR_HISTORY_READ` | |
| Secuencia normal | Paso | Descripción |
| | 1 | El administrador envía `GET /users/{usuario_id}/state-history` |
| | 2 | El sistema valida sesión y permiso |
| | 3 | El sistema consulta y retorna historial del usuario |
| Secuencia alterna | Paso | Descripción |
| | 3.1 | Si el usuario no existe o no tiene historial, el sistema retorna lista vacía con mensaje informativo |
| Postcondición | Historial queda disponible para trazabilidad y auditoría | |
| Comentarios | El historial se alimenta por cambios de estado transaccionales | |

#### 2.2.11 REQ11 — Consultar catálogo de tipos de documento
| Código | REQ11 | |
|---|---|---|
| Nombre | Consultar catálogo de tipos de documento | |
| Actores | Cliente autorizado, administrador | |
| Descripción | Permite consultar tipos de documento activos del sistema | |
| Precondición | Sesión activa con permiso `USR_READ` | |
| Secuencia normal | Paso | Descripción |
| | 1 | El cliente envía `GET /document-types` |
| | 2 | El sistema valida sesión y permiso |
| | 3 | El sistema consulta y retorna tipos de documento activos |
| Secuencia alterna | Paso | Descripción |
| | 3.1 | Si no hay tipos activos, el sistema retorna lista vacía |
| Postcondición | Catálogo de referencia queda disponible para formularios de perfil | |
| Comentarios | Solo retorna tipos activos | |

#### 2.2.12 REQ12 — Búsqueda avanzada y paginación
| Código | REQ12 | |
|---|---|---|
| Nombre | Búsqueda avanzada y paginación | |
| Actores | Administrador | |
| Descripción | Permite buscar usuarios por filtros (`nombre`, `numero_documento`, `email`, `estado`, `ciudad`) con paginación | |
| Precondición | Sesión activa con permiso `USR_SEARCH`; parámetros de paginación válidos | |
| Secuencia normal | Paso | Descripción |
| | 1 | El administrador envía `GET /users` con filtros opcionales y paginación |
| | 2 | El sistema valida sesión, permiso, `pagina >= 1` y rango de `items_por_pagina` |
| | 3 | El sistema ejecuta consulta filtrada y retorna resultados paginados con metadatos |
| Secuencia alterna | Paso | Descripción |
| | 2.1 | Si `pagina` o `items_por_pagina` son inválidos, el sistema responde `400` |
| Postcondición | Resultado de búsqueda queda disponible con `total_registros`, `total_paginas`, `pagina_actual` e `items_por_pagina` | |
| Comentarios | El límite máximo de `items_por_pagina` lo define la configuración del servicio | |

#### 2.2.13 REQ13 — Estadísticas por estado
| Código | REQ13 | |
|---|---|---|
| Nombre | Estadísticas por estado | |
| Actores | Administrador | |
| Descripción | Entrega métricas agregadas de usuarios por estado | |
| Precondición | Sesión activa con permiso `USR_STATS_READ` | |
| Secuencia normal | Paso | Descripción |
| | 1 | El administrador envía `GET /users/stats/by-state` |
| | 2 | El sistema valida sesión y permiso |
| | 3 | El sistema calcula y retorna estadísticas por estado |
| Secuencia alterna | Paso | Descripción |
| | 3.1 | Si no existen usuarios, el sistema retorna métricas en cero |
| Postcondición | Métricas agregadas quedan disponibles para análisis | |
| Comentarios | No expone datos individuales ni sensibles | |

#### 2.2.14 REQ14 — Listar usuarios por rol
| Código | REQ14 | |
|---|---|---|
| Nombre | Listar usuarios por rol | |
| Actores | Administrador | |
| Descripción | Permite listar usuarios por `rol_id`, con filtro opcional por estado y paginación | |
| Precondición | Sesión activa con permiso `USR_LIST_BY_ROLE`; `rol_id` válido | |
| Secuencia normal | Paso | Descripción |
| | 1 | El administrador envía `GET /users/by-role/{rol_id}` con `estado` opcional y paginación |
| | 2 | El sistema valida sesión, permiso y parámetros |
| | 3 | El sistema consulta usuarios por rol y retorna resultados paginados |
| Secuencia alterna | Paso | Descripción |
| | 3.1 | Si no hay coincidencias, el sistema retorna listado vacío |
| Postcondición | Listado por rol queda disponible para gestión administrativa | |
| Comentarios | Retorna metadatos de paginación junto con resultados | |

#### 2.2.15 REQ15 — Validación interna de existencia y credenciales
| Código | REQ15 | |
|---|---|---|
| Nombre | Validación interna de existencia y credenciales | |
| Actores | ms-programas, ms-autenticación | |
| Descripción | Provee validaciones internas para existencia de usuario y verificación de credenciales | |
| Precondición | Solicitud desde flujo interno entre microservicios | |
| Secuencia normal | Paso | Descripción |
| | 1 | Para existencia, se invoca `GET /users/{usuario_id}/validate` |
| | 2 | El sistema responde si existe e incluye `estado`, `user_id` y `username` cuando aplica |
| | 3 | Para credenciales, se invoca `POST /internal/users/credentials/verify` con `username` y `encrypted_password` |
| | 4 | El sistema verifica hash de contraseña y retorna estado interno (`ACTIVE` o `BLOCKED`) |
| Secuencia alterna | Paso | Descripción |
| | 3.1 | Si credenciales son inválidas, el sistema responde `401` |
| | 3.2 | Si el usuario está inactivo/suspendido/eliminado, el sistema responde `423` |
| Postcondición | Resultado de validación interna queda disponible para autenticación e integración | |
| Comentarios | Endpoints orientados a integración interna, no a cliente final | |

## 3. Cualidades del Sistema

### 3.1 Usabilidad

- El microservicio debe exponer documentación interactiva de API en `/docs` (Swagger UI) y `/redoc`, con contratos de entrada/salida alineados a los modelos Pydantic.
- Todas las respuestas deben seguir un formato uniforme (`request_id`, `status`, `statusCode`, `data`, `message`) para facilitar aprendizaje y consumo por clientes.
- Los mensajes funcionales y de error deben mantenerse en español técnico consistente para reducir ambigüedad operativa.
- El sistema debe aceptar `X-Request-ID` y autogenerarlo cuando no esté presente, permitiendo trazabilidad simple para equipos de soporte e integración.

### 3.2 Confiabilidad

- El servicio debe exponer endpoints de salud `GET /` y `GET /api/v1/health` con estado `ok` para verificación de disponibilidad.
- El cambio de estado de usuario debe ejecutarse en transacción atómica (actualización de usuario + registro en historial), con `rollback` ante fallo.
- Las integraciones críticas con ms-autenticación y ms-roles deben fallar de forma controlada con códigos HTTP de error (`401`, `403`, `503`) sin dejar datos inconsistentes.
- El registro de auditoría debe operar en modo resiliente: si ms-auditoría no está disponible, se debe guardar respaldo local JSONL.
- El envío de notificaciones debe ser asíncrono y no bloquear la operación principal del usuario (fire-and-forget).

### 3.3 Rendimiento

- Las operaciones de lectura y escritura del dominio de usuarios deben responder en tiempo acotado por configuración de timeouts de servicios externos (`TIMEOUT_AUTH`, `TIMEOUT_ROL`, `TIMEOUT_NOT`, `TIMEOUT_AUD`).
- Las operaciones de notificación y auditoría deben ejecutarse en hilos asíncronos para no aumentar la latencia percibida del endpoint principal.
- La búsqueda de usuarios debe soportar paginación obligatoria con valores por defecto (`pagina=1`, `items_por_pagina=10`) y límite máximo (`items_por_pagina<=100`).
- El servicio debe ser apto para ejecución continua en contenedores con política de reinicio `unless-stopped`.

### 3.4 Soporteabilidad

- La configuración operacional debe ser externalizada por variables de entorno (`.env`) para despliegue en diferentes ambientes sin cambios de código.
- El servicio debe ser desplegable por contenedores Docker (app + PostgreSQL) y red compartida de microservicios.
- La arquitectura debe mantenerse por capas (`routes`, `services`, `repository`, `models`, `utils`) para facilitar mantenimiento y evolución.
- Los contratos de integración (headers, permisos, endpoints y ejemplos) deben permanecer documentados en `documentacion/rutas_y_endpoints.md`.
- Las reglas de seguridad y cifrado (AES-256 y bcrypt) deben permanecer centralizadas en utilidades reutilizables para simplificar soporte y auditoría técnica.

## 4. Interfaces del Sistema

### 4.1 Interfaces de Usuario

El microservicio no implementa interfaz gráfica propia para usuario final. La interacción principal es API REST y su interfaz de consulta técnica (Swagger/ReDoc).

#### 4.1.1 Aspecto y Sensación

- Para consumidores técnicos, la experiencia de interfaz se provee mediante Swagger UI y ReDoc con estructura estándar OpenAPI.
- El diseño visual para usuarios finales queda delegado al cliente consumidor (frontend o aplicación externa), fuera del alcance de este microservicio.

#### 4.1.2 Requisitos de Diseño y Navegación

- La navegación funcional debe organizarse por recursos REST (`/users`, `/document-types`, `/internal/users`).
- Las operaciones deben agruparse por dominios de negocio: usuarios, perfiles, historial, preferencias, tipos de documento y autenticación interna.
- El versionado de rutas debe mantenerse bajo prefijo `/api/v1` para compatibilidad evolutiva.

#### 4.1.3 Consistencia

- Todas las rutas públicas deben usar JSON sobre HTTP y mantener códigos de estado consistentes (`200`, `201`, `400`, `401`, `403`, `404`, `409`, `500`, `503` según caso).
- Debe usarse terminología uniforme en payloads y mensajes (`usuario_id`, `rol_id`, `estado`, `motivo`, `request_id`).
- Los headers de integración deben mantenerse consistentes: `Authorization`, `X-Request-ID` y `X-App-Token` (según el tipo de endpoint).

#### 4.1.4 Requisitos de personalización del usuario

- El sistema debe permitir personalización del usuario mediante:
  - Perfil extendido (`/users/{usuario_id}/profile`).
  - Preferencias de notificación (`/users/{usuario_id}/notification-preferences`), incluyendo canal preferido y horario de no molestar.
- La entrega de datos personalizados debe restringirse por sesión/permisos o por token interno válido cuando aplique integración inter-servicio.

### 4.2 Interfaces con Sistemas o Dispositivos Externos

El microservicio se integra con otros microservicios y con PostgreSQL; no requiere interfaces directas con dispositivos físicos.

#### 4.2.1 Interfaces de Software

- **Interfaz REST pública (clientes/autenticados):**
  - Protocolo: HTTP/1.1
  - Formato: JSON UTF-8
  - Base path: `/api/v1`
  - Puerto de exposición del servicio: `8000` (contenedor app)
- **Interfaz interna de autenticación de credenciales:**
  - Endpoint: `POST /internal/users/credentials/verify`
  - Propósito: validación interna para ms-autenticación
- **Dependencias externas requeridas:**
  - ms-autenticación: validación de sesión.
  - ms-roles: validación de permisos y rol.
  - ms-notificaciones: envío de notificaciones.
  - ms-auditoría: registro de logs de auditoría.
- **Headers y seguridad de integración:**
  - `Authorization: Bearer <token>` para autenticación de usuario.
  - `X-App-Token` para llamadas entre microservicios (token cifrado AES-256 con prefijo `AES256:`).
  - `X-Request-ID` para correlación de trazas.

#### 4.2.2 Interfaces de Hardware

- No se definen interfaces de hardware específicas para este microservicio.
- La ejecución objetivo es infraestructura virtualizada/contenedorizada compatible con Docker.

#### 4.2.3 Interfaces de Comunicaciones

- Comunicación de red síncrona mediante HTTP entre microservicios dentro de la red Docker `microservicios-network`.
- Comunicación con base de datos PostgreSQL vía TCP (`DB_HOST`, `DB_PORT`, por defecto 5432).
- Configuración de endpoints remotos por variables de entorno:
  - `AUTH_SERVICE_URL`
  - `ROL_SERVICE_URL`
  - `NOT_SERVICE_URL`
  - `AUD_SERVICE_URL`
- Los tiempos máximos de espera de comunicación deben controlarse por configuración (`TIMEOUT_AUTH`, `TIMEOUT_ROL`, `TIMEOUT_NOT`, `TIMEOUT_AUD`).
