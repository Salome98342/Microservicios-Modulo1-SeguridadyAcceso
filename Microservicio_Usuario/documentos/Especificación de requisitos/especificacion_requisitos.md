# Especificación de Requisitos

## 1. Introducción

Este documento consolida requisitos funcionales del **Microservicio de Usuarios** basados en el código actual del servicio (`ms_usuario`), sus rutas, servicios y persistencia.  
El alcance se limita a funcionalidades implementadas para gestión de usuarios, perfiles, preferencias de notificación, historial de estado, tipos de documento y validaciones internas para autenticación.

## 2. Requisitos Funcionales a Nivel del Sistema

Declaración de requisitos funcionales del sistema (no como casos de uso), tomando únicamente comportamiento verificable en el código del microservicio.

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
| Descripción | El cliente crea el usuario | |
| Precondición | Que el usuario no este previamente registrado | |
| Secuencia normal | Paso | Descripción |
| | 1 | El administrador abre la aplicación |
| | 2 | Da clic en el botón de registrar usuario |
| Secuencia alterna | Paso | Descripción |
| | 1.1.1 | Como la aplicación no abre contacta con el administrador de la aplicación |
| | 1.1.2 | El administrador arregla el problema al cliente y pide que intente de nuevo |
| | 2.1.1 | |
| Postcondición | El usuario queda registrado y puede usar el sistema | |
| Comentarios | | |

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
| | 4 | El sistema verifica hash de contraseña y estado del usuario (`ACTIVE` o `BLOCKED`) |
| Secuencia alterna | Paso | Descripción |
| | 3.1 | Si credenciales son inválidas, el sistema responde `401` |
| | 3.2 | Si el usuario está inactivo/suspendido/eliminado, el sistema responde `423` |
| Postcondición | Resultado de validación interna queda disponible para autenticación e integración | |
| Comentarios | Endpoints orientados a integración interna, no a cliente final | |
