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
| Campo | Paso | Detalle |
|---|---|---|
| Código | REQ1 | Crear usuario |
| Actores | - | Cliente, administrador, ms-usuarios, ms-roles |
| Descripción | - | Permite registrar un usuario nuevo con credenciales y rol asignado. |
| Precondición | - | El `username` y `email` no existen previamente y el `rol_id` es válido. |
| Secuencia normal | 1 | El sistema recibe `username`, `email`, contraseña y `rol_id`. |
| Secuencia normal | 2 | El sistema valida formato, unicidad y rol. |
| Secuencia normal | 3 | El sistema crea el usuario con estado inicial `activo`. |
| Secuencia alterna | 2A | Si `username` o `email` ya existen, rechaza la creación. |
| Secuencia alterna | 2B | Si el rol no es válido, rechaza la creación. |
| Postcondición | - | Usuario registrado y disponible para uso del sistema. |
| Comentarios | - | La contraseña debe almacenarse con hash seguro. |

#### 2.2.2 REQ2 — Consultar usuario por ID
| Campo | Paso | Detalle |
|---|---|---|
| Código | REQ2 | Consultar usuario por ID |
| Actores | - | Cliente, administrador, ms-usuarios |
| Descripción | - | Permite recuperar datos públicos de un usuario por identificador. |
| Precondición | - | Existe un `user_id` válido y consultable. |
| Secuencia normal | 1 | El sistema recibe el identificador del usuario. |
| Secuencia normal | 2 | El sistema consulta el registro en persistencia. |
| Secuencia normal | 3 | El sistema retorna los datos públicos del usuario. |
| Secuencia alterna | 2A | Si el usuario no existe, retorna error de no encontrado. |
| Postcondición | - | Datos del usuario consultado disponibles en respuesta. |
| Comentarios | - | No se expone información sensible. |

#### 2.2.3 REQ3 — Consultar usuario por email
| Campo | Paso | Detalle |
|---|---|---|
| Código | REQ3 | Consultar usuario por email |
| Actores | - | Cliente, ms-autenticación, ms-usuarios |
| Descripción | - | Permite consultar usuario por correo electrónico. |
| Precondición | - | El correo recibido cumple formato válido. |
| Secuencia normal | 1 | El sistema recibe el `email` de consulta. |
| Secuencia normal | 2 | El sistema valida formato y consulta por correo. |
| Secuencia normal | 3 | El sistema retorna datos del usuario asociado. |
| Secuencia alterna | 2A | Si no existe el correo, retorna resultado vacío o error. |
| Postcondición | - | Usuario consultado por email con datos consistentes. |
| Comentarios | - | Para integración interna puede incluir `password_hash`. |

#### 2.2.4 REQ4 — Actualizar datos básicos de usuario
| Campo | Paso | Detalle |
|---|---|---|
| Código | REQ4 | Actualizar datos básicos de usuario |
| Actores | - | Administrador, ms-usuarios, ms-roles |
| Descripción | - | Permite modificar `username`, `email` y/o `rol_id`. |
| Precondición | - | El usuario objetivo existe y los campos enviados son válidos. |
| Secuencia normal | 1 | El sistema recibe usuario objetivo y datos de actualización. |
| Secuencia normal | 2 | El sistema valida reglas de unicidad y consistencia de rol. |
| Secuencia normal | 3 | El sistema aplica cambios y retorna datos actualizados. |
| Secuencia alterna | 2A | Si hay colisiones o rol inválido, rechaza la actualización. |
| Postcondición | - | Datos básicos persistidos de forma consistente. |
| Comentarios | - | Debe mantener trazabilidad de cambios. |

#### 2.2.5 REQ5 — Cambiar estado de usuario
| Campo | Paso | Detalle |
|---|---|---|
| Código | REQ5 | Cambiar estado de usuario |
| Actores | - | Administrador, ms-usuarios |
| Descripción | - | Permite cambiar el estado funcional del usuario. |
| Precondición | - | El usuario existe y el estado destino está permitido. |
| Secuencia normal | 1 | El sistema recibe estado destino y motivo. |
| Secuencia normal | 2 | El sistema valida transición de estado. |
| Secuencia normal | 3 | El sistema actualiza estado y registra historial. |
| Secuencia alterna | 2A | Si la transición no es válida, rechaza el cambio. |
| Postcondición | - | Estado actualizado con registro de auditoría e historial. |
| Comentarios | - | Estados válidos: `activo`, `inactivo`, `suspendido`. |

#### 2.2.6 REQ6 — Desactivar y reactivar usuario
| Campo | Paso | Detalle |
|---|---|---|
| Código | REQ6 | Desactivar y reactivar usuario |
| Actores | - | Administrador, ms-usuarios, ms-notificaciones |
| Descripción | - | Permite desactivación lógica y posterior reactivación. |
| Precondición | - | El usuario existe y la acción solicitada es coherente con su estado. |
| Secuencia normal | 1 | El sistema recibe acción de desactivar o reactivar. |
| Secuencia normal | 2 | El sistema valida estado actual del usuario. |
| Secuencia normal | 3 | El sistema aplica la acción y registra trazabilidad. |
| Secuencia alterna | 2A | Si la acción no aplica al estado actual, rechaza la operación. |
| Postcondición | - | Usuario desactivado o reactivado correctamente. |
| Comentarios | - | Puede generar notificación de cambio de estado. |

#### 2.2.7 REQ7 — Gestionar contraseña
| Campo | Paso | Detalle |
|---|---|---|
| Código | REQ7 | Gestionar contraseña |
| Actores | - | Usuario autenticado, ms-usuarios |
| Descripción | - | Permite al usuario actualizar su contraseña. |
| Precondición | - | El usuario está autenticado y conoce su contraseña actual. |
| Secuencia normal | 1 | El sistema recibe contraseña actual y nueva contraseña. |
| Secuencia normal | 2 | El sistema valida contraseña actual y política de seguridad. |
| Secuencia normal | 3 | El sistema almacena el nuevo hash de contraseña. |
| Secuencia alterna | 2A | Si la contraseña actual no coincide, rechaza la solicitud. |
| Secuencia alterna | 2B | Si la nueva contraseña no cumple política, rechaza la solicitud. |
| Postcondición | - | Contraseña actualizada de forma segura. |
| Comentarios | - | Nunca se devuelve ni persiste contraseña en texto plano. |

#### 2.2.8 REQ8 — Gestionar perfil extendido
| Campo | Paso | Detalle |
|---|---|---|
| Código | REQ8 | Gestionar perfil extendido |
| Actores | - | Usuario, administrador, ms-usuarios |
| Descripción | - | Permite crear, consultar y actualizar información de perfil extendido. |
| Precondición | - | Existe un usuario asociado al perfil. |
| Secuencia normal | 1 | El sistema recibe datos de perfil del usuario. |
| Secuencia normal | 2 | El sistema valida integridad y consistencia de campos. |
| Secuencia normal | 3 | El sistema crea/actualiza y retorna el perfil extendido. |
| Secuencia alterna | 2A | Si faltan datos obligatorios, rechaza la operación. |
| Postcondición | - | Perfil extendido persistido y asociado correctamente. |
| Comentarios | - | Mantiene relación 1:1 con usuario. |

#### 2.2.9 REQ9 — Gestionar preferencias de notificación
| Campo | Paso | Detalle |
|---|---|---|
| Código | REQ9 | Gestionar preferencias de notificación |
| Actores | - | Usuario, ms-usuarios |
| Descripción | - | Permite consultar y actualizar preferencias de notificación del usuario. |
| Precondición | - | El usuario existe y está autorizado para gestionar sus preferencias. |
| Secuencia normal | 1 | El sistema recibe preferencias y configuración de horarios. |
| Secuencia normal | 2 | El sistema valida formato y coherencia de la configuración. |
| Secuencia normal | 3 | El sistema guarda y retorna las preferencias actualizadas. |
| Secuencia alterna | 2A | Si los horarios son inválidos, rechaza la actualización. |
| Postcondición | - | Preferencias de notificación actualizadas para el usuario. |
| Comentarios | - | Incluye soporte para ventana de no molestar. |

#### 2.2.10 REQ10 — Consultar historial de estados
| Campo | Paso | Detalle |
|---|---|---|
| Código | REQ10 | Consultar historial de estados |
| Actores | - | Administrador, ms-usuarios |
| Descripción | - | Permite consultar la trazabilidad de estados de un usuario. |
| Precondición | - | El usuario existe y tiene historial de cambios disponible. |
| Secuencia normal | 1 | El sistema recibe identificador de usuario. |
| Secuencia normal | 2 | El sistema consulta historial de cambios de estado. |
| Secuencia normal | 3 | El sistema retorna historial en orden cronológico. |
| Secuencia alterna | 2A | Si no hay historial, retorna lista vacía. |
| Postcondición | - | Historial de estado disponible para análisis y auditoría. |
| Comentarios | - | Información usada para trazabilidad operativa. |

#### 2.2.11 REQ11 — Consultar catálogo de tipos de documento
| Campo | Paso | Detalle |
|---|---|---|
| Código | REQ11 | Consultar catálogo de tipos de documento |
| Actores | - | Cliente, ms-usuarios |
| Descripción | - | Expone catálogo de tipos de documento habilitados. |
| Precondición | - | El catálogo se encuentra cargado y disponible en el servicio. |
| Secuencia normal | 1 | El sistema recibe solicitud de catálogo. |
| Secuencia normal | 2 | El sistema filtra tipos de documento activos. |
| Secuencia normal | 3 | El sistema retorna lista de tipos disponibles. |
| Secuencia alterna | 2A | Si no hay tipos activos, retorna lista vacía. |
| Postcondición | - | Catálogo accesible para formularios de perfil. |
| Comentarios | - | Se usa como dato de referencia. |

#### 2.2.12 REQ12 — Búsqueda avanzada y paginación
| Campo | Paso | Detalle |
|---|---|---|
| Código | REQ12 | Búsqueda avanzada y paginación |
| Actores | - | Administrador, ms-usuarios |
| Descripción | - | Permite consultar usuarios aplicando filtros y paginación. |
| Precondición | - | Se reciben criterios de búsqueda y parámetros de página válidos. |
| Secuencia normal | 1 | El sistema recibe filtros (`nombre`, `documento`, `email`, `estado`, `ciudad`). |
| Secuencia normal | 2 | El sistema valida filtros y arma consulta paginada. |
| Secuencia normal | 3 | El sistema retorna resultados y metadatos de paginación. |
| Secuencia alterna | 2A | Si hay filtros inválidos, rechaza la consulta. |
| Postcondición | - | Resultado filtrado y paginado disponible para consumo. |
| Comentarios | - | Debe mantener desempeño en volúmenes altos. |

#### 2.2.13 REQ13 — Estadísticas por estado
| Campo | Paso | Detalle |
|---|---|---|
| Código | REQ13 | Estadísticas por estado |
| Actores | - | Administrador, ms-usuarios |
| Descripción | - | Entrega métricas agregadas de usuarios por estado. |
| Precondición | - | Existen datos de usuarios en el sistema. |
| Secuencia normal | 1 | El sistema recibe solicitud de estadísticas. |
| Secuencia normal | 2 | El sistema calcula total y distribución por estado. |
| Secuencia normal | 3 | El sistema retorna resumen agregado. |
| Secuencia alterna | 2A | Si no hay usuarios, retorna estadísticas en cero. |
| Postcondición | - | Métricas disponibles para monitoreo funcional. |
| Comentarios | - | No expone datos individuales sensibles. |

#### 2.2.14 REQ14 — Listar usuarios por rol
| Campo | Paso | Detalle |
|---|---|---|
| Código | REQ14 | Listar usuarios por rol |
| Actores | - | Administrador, ms-usuarios |
| Descripción | - | Permite consultar usuarios asignados a un rol. |
| Precondición | - | El `rol_id` es válido; `estado` puede ser opcional. |
| Secuencia normal | 1 | El sistema recibe `rol_id` y estado opcional. |
| Secuencia normal | 2 | El sistema valida parámetros y consulta usuarios del rol. |
| Secuencia normal | 3 | El sistema retorna listado de usuarios coincidentes. |
| Secuencia alterna | 2A | Si el rol no existe, rechaza la consulta. |
| Postcondición | - | Listado por rol disponible para gestión administrativa. |
| Comentarios | - | Puede combinarse con filtros de estado. |

#### 2.2.15 REQ15 — Validación interna de existencia y credenciales
| Campo | Paso | Detalle |
|---|---|---|
| Código | REQ15 | Validación interna de existencia y credenciales |
| Actores | - | ms-autenticación, ms-usuarios |
| Descripción | - | Provee validación interna de usuario y credenciales para integración. |
| Precondición | - | La solicitud proviene de un flujo interno autorizado. |
| Secuencia normal | 1 | El sistema recibe identificador de usuario y/o credenciales. |
| Secuencia normal | 2 | El sistema verifica existencia del usuario y validez de credenciales. |
| Secuencia normal | 3 | El sistema retorna confirmación o rechazo para consumo interno. |
| Secuencia alterna | 2A | Si el usuario no existe o credenciales fallan, retorna rechazo. |
| Postcondición | - | Resultado de validación disponible para autenticación interna. |
| Comentarios | - | Endpoint de uso interno, no orientado a cliente final. |
