# Microservicio: ms-usuarios [USR]

## Documento de Requisitos Funcionales Detallados

| Campo | Detalle |
|-------|---------|
| **Microservicio** | ms-usuarios [USR] |
| **Módulo** | Módulo 1 — Seguridad y Acceso |
| **Versión** | 1.0 |
| **Fecha** | Marzo 2026 |
| **Documento origen** | ms-usuarios_requisitos.md v1.0 |

---

## Tabla de Contenido

### Categoría 1: Requisitos Transversales

- [USR-RF-001](#usr-rf-001) - Validación de sesión de usuario
- [USR-RF-002](#usr-rf-002) - Validación de permisos por funcionalidad
- [USR-RF-003](#usr-rf-003) - Generación de identificador de rastreo (Request ID)
- [USR-RF-004](#usr-rf-004) - Registro de auditoría y logs en formato JSON
- [USR-RF-005](#usr-rf-005) - Estructura de respuesta estándar del sistema

### Categoría 2: Requisitos Funcionales por Entidad

#### Entidad: Usuarios

- [USR-RF-006](#usr-rf-006) - Crear nuevo usuario en el sistema
- [USR-RF-007](#usr-rf-007) - Consultar usuario por identificador
- [USR-RF-008](#usr-rf-008) - Consultar usuario por correo electrónico
- [USR-RF-009](#usr-rf-009) - Consultar usuario por número de documento
- [USR-RF-010](#usr-rf-010) - Actualizar datos básicos del usuario
- [USR-RF-011](#usr-rf-011) - Desactivar usuario del sistema
- [USR-RF-012](#usr-rf-012) - Búsqueda avanzada de usuarios con filtros

#### Entidad: Perfiles

- [USR-RF-013](#usr-rf-013) - Consultar perfil extendido de usuario
- [USR-RF-014](#usr-rf-014) - Actualizar perfil extendido de usuario

#### Entidad: Historial de Estados

- [USR-RF-015](#usr-rf-015) - Cambiar estado de usuario
- [USR-RF-016](#usr-rf-016) - Consultar historial de cambios de estado

#### Entidad: Tipos de Documento

- [USR-RF-017](#usr-rf-017) - Consultar catálogo de tipos de documento

#### Entidad: Preferencias de Notificación

- [USR-RF-018](#usr-rf-018) - Consultar preferencias de notificación del usuario
- [USR-RF-019](#usr-rf-019) - Actualizar preferencias de notificación del usuario

### Categoría 3: Requisitos Sugeridos

- [USR-RF-020](#usr-rf-020) - Reactivar usuario suspendido o inactivo
- [USR-RF-021](#usr-rf-021) - Validar existencia de usuario (servicio interno)
- [USR-RF-022](#usr-rf-022) - Actualizar contraseña de usuario
- [USR-RF-023](#usr-rf-023) - Listar usuarios por rol
- [USR-RF-024](#usr-rf-024) - Obtener estadísticas de usuarios por estado

---

# Categoría 1: Requisitos Transversales

---

## USR-RF-001

| | | |
|---|---|---|
| **Código** | USR-RF-001 | |
| **Nombre** | Validación de sesión de usuario | |
| **Descripción** | Toda operación del microservicio debe validar que el usuario posee una sesión activa antes de procesar la petición. | |
| **Actores** | Usuario del sistema, ms-usuarios, ms-autenticacion | |
| | | |
| **Precondición** | El usuario envía un token de sesión en las cabeceras de la petición HTTP. | |
| | El microservicio ms-autenticacion está disponible para validación. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | El sistema recibe una petición HTTP con un token de sesión en las cabeceras. |
| | 2 | El sistema extrae el token de las cabeceras de la petición. |
| | 3 | El sistema invoca al microservicio ms-autenticacion [AUTH] para validar el token. |
| | 4 | ms-autenticacion responde confirmando que la sesión es válida y está activa. |
| | 5 | El sistema extrae del token validado el identificador del usuario y su rol. |
| | 6 | El sistema continúa con el procesamiento de la petición. |
| | | |
| **Secuencia alterna** | 4A | Si ms-autenticacion responde que la sesión no es válida o está inactiva, el sistema rechaza la petición sin procesarla. |
| | 4B | El sistema retorna un código de respuesta 401 (No autorizado) con un mensaje descriptivo: "Sesión no válida o expirada". |
| | 4C | El sistema ejecuta [USR-RF-004] para registrar el evento fallido en auditoría. |
| | 4D | El sistema finaliza el procesamiento de la petición. |
| | | |
| **Excepciones** | E1 | Si ms-autenticacion no responde o retorna un error técnico, el sistema rechaza la petición por seguridad con código 503 (Servicio no disponible). |
| | E2 | Si el token no está presente en las cabeceras, el sistema rechaza la petición con código 400 (Solicitud incorrecta). |
| | | |
| **Postcondición** | La sesión del usuario ha sido validada exitosamente y se ha confirmado su identidad. | |
| | El sistema tiene disponible el identificador del usuario y su rol para continuar el procesamiento. | |
| | | |
| **Comentarios** | Este requisito implementa la regla transversal de "Validación de Sesión Obligatoria" del sistema. Se invoca antes de ejecutar cualquier lógica de negocio en todos los endpoints del microservicio. | |

---

## USR-RF-002

| | | |
|---|---|---|
| **Código** | USR-RF-002 | |
| **Nombre** | Validación de permisos por funcionalidad | |
| **Descripción** | Después de validar la sesión, el sistema debe verificar que el rol del usuario tiene autorización para ejecutar la funcionalidad solicitada. | |
| **Actores** | Usuario del sistema, ms-usuarios, ms-roles | |
| | | |
| **Precondición** | Se ha ejecutado exitosamente [USR-RF-001] (Validación de sesión). | |
| | Se conoce el identificador del rol del usuario. | |
| | Cada funcionalidad del microservicio tiene un código de permiso único definido. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | El sistema identifica el código de permiso requerido para la funcionalidad solicitada. |
| | 2 | El sistema invoca al microservicio ms-roles [ROL] proporcionando el rol del usuario y el código de permiso. |
| | 3 | ms-roles verifica si el rol tiene asignado el permiso solicitado. |
| | 4 | ms-roles responde confirmando que el rol tiene autorización para ejecutar la funcionalidad. |
| | 5 | El sistema continúa con la ejecución de la lógica de negocio. |
| | | |
| **Secuencia alterna** | 4A | Si ms-roles responde que el rol no tiene el permiso requerido, el sistema rechaza la petición. |
| | 4B | El sistema retorna un código de respuesta 403 (Prohibido) con un mensaje descriptivo: "No tiene permisos para ejecutar esta operación". |
| | 4C | El sistema ejecuta [USR-RF-004] para registrar el intento de acceso no autorizado en auditoría. |
| | 4D | El sistema finaliza el procesamiento de la petición. |
| | | |
| **Excepciones** | E1 | Si ms-roles no responde o retorna un error técnico, el sistema rechaza la petición por seguridad con código 503 (Servicio no disponible). |
| | E2 | Si el código de permiso de la funcionalidad no está definido en el sistema, se registra un error crítico en los logs y se rechaza la petición con código 500 (Error interno). |
| | | |
| **Postcondición** | Se ha validado que el usuario tiene autorización para ejecutar la funcionalidad solicitada. | |
| | El evento de validación de permisos ha sido registrado. | |
| | | |
| **Comentarios** | Este requisito implementa la regla transversal de "Validación de Permisos por Funcionalidad" del sistema. Se invoca inmediatamente después de [USR-RF-001] en todos los endpoints que requieren autorización. | |

---

## USR-RF-003

| | | |
|---|---|---|
| **Código** | USR-RF-003 | |
| **Nombre** | Generación de identificador de rastreo (Request ID) | |
| **Descripción** | Cada petición debe tener un identificador único de rastreo que se propaga a todos los servicios involucrados y se incluye en todas las respuestas. | |
| **Actores** | ms-usuarios, Microservicios consumidores | |
| | | |
| **Precondición** | El sistema recibe una petición HTTP (puede provenir de un usuario o de otro microservicio). | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | El sistema verifica si la petición entrante ya incluye un identificador de rastreo en las cabeceras HTTP. |
| | 2 | Si no existe un identificador en las cabeceras, el sistema genera uno nuevo con el formato: `USR-{timestamp}-{aleatorio8}`. |
| | 3 | El timestamp se genera en formato Unix (segundos desde epoch). |
| | 4 | El identificador aleatorio se genera con 8 caracteres alfanuméricos. |
| | 5 | El sistema almacena el identificador para su uso durante todo el procesamiento de la petición. |
| | 6 | El sistema incluye el identificador en todas las llamadas a otros microservicios. |
| | 7 | El sistema incluye el identificador en la respuesta final tanto en las cabeceras como en el cuerpo JSON. |
| | | |
| **Secuencia alterna** | 2A | Si ya existe un identificador de rastreo en las cabeceras (la petición proviene de otro microservicio), el sistema reutiliza ese identificador sin generar uno nuevo. |
| | 2B | El sistema continúa con el paso 5, usando el identificador recibido. |
| | | |
| **Excepciones** | E1 | Si falla la generación del identificador aleatorio, el sistema genera un identificador simplificado usando solo el timestamp y un contador secuencial. |
| | | |
| **Postcondición** | Existe un identificador único de rastreo asociado a la petición. | |
| | El identificador está disponible para ser incluido en logs, respuestas y llamadas a otros servicios. | |
| | | |
| **Comentarios** | Este requisito implementa la regla transversal de "Trazabilidad Distribuida (Request ID)" del sistema. El identificador permite rastrear una petición completa a través de múltiples microservicios para propósitos de debugging y auditoría. Ejemplo de identificador: `USR-1709856234-a3f8b2c1`. | |

---

## USR-RF-004

| | | |
|---|---|---|
| **Código** | USR-RF-004 | |
| **Nombre** | Registro de auditoría y logs en formato JSON | |
| **Descripción** | Cada operación del microservicio debe generar un registro de log en formato JSON que se envía de forma asíncrona al servicio de auditoría. | |
| **Actores** | ms-usuarios, ms-auditoria | |
| | | |
| **Precondición** | Se ha completado el procesamiento de una petición (exitosa o fallida). | |
| | Se ha ejecutado [USR-RF-003] y existe un identificador de rastreo. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | El sistema recopila la información de la operación ejecutada. |
| | 2 | El sistema construye un objeto JSON con los siguientes campos: timestamp (fecha y hora ISO 8601), request_id (identificador de rastreo), microservicio ("ms-usuarios"), funcionalidad (nombre de la operación ejecutada), metodo (GET, POST, PUT, DELETE), codigo_respuesta (código HTTP), duracion_ms (duración en milisegundos), usuario_id (identificador del usuario que realizó la operación), detalle (descripción de la operación). |
| | 3 | El sistema envía el objeto JSON al microservicio ms-auditoria [AUD] de forma asíncrona (sin esperar respuesta). |
| | 4 | El sistema continúa con el flujo normal independientemente del resultado del envío. |
| | | |
| **Secuencia alterna** | 3A | Si el envío a ms-auditoria falla por cualquier motivo (servicio no disponible, timeout, error de red), el sistema registra el error localmente en un log de respaldo. |
| | 3B | El sistema NO detiene ni reintenta el envío. |
| | 3C | El sistema continúa operando normalmente. |
| | | |
| **Excepciones** | E1 | Si falla la construcción del objeto JSON por datos faltantes, el sistema construye un objeto parcial con los campos disponibles y lo marca como "incompleto". |
| | | |
| **Postcondición** | Se ha generado y enviado un registro de log completo a ms-auditoria. | |
| | El registro está disponible para trazabilidad, análisis y auditoría. | |
| | La operación continúa su flujo normal sin interrupciones por el proceso de auditoría. | |
| | | |
| **Comentarios** | Este requisito implementa la regla transversal de "Auditoría y Logs en Formato JSON" del sistema. El envío asíncrono garantiza que el proceso de auditoría no afecte el rendimiento ni la disponibilidad del servicio. Los logs de respaldo locales deben rotarse periódicamente para evitar consumo excesivo de disco. | |

---

## USR-RF-005

| | | |
|---|---|---|
| **Código** | USR-RF-005 | |
| **Nombre** | Estructura de respuesta estándar del sistema | |
| **Descripción** | Todas las respuestas del microservicio deben seguir una estructura JSON uniforme que incluya identificador de rastreo, indicador de éxito, datos, mensaje y timestamp. | |
| **Actores** | ms-usuarios, Usuario del sistema, Microservicios consumidores | |
| | | |
| **Precondición** | Se ha completado el procesamiento de una petición (exitosa o fallida). | |
| | Se ha ejecutado [USR-RF-003] y existe un identificador de rastreo. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | El sistema construye un objeto JSON de respuesta estándar con los siguientes campos obligatorios: request_id (identificador de rastreo), success (boolean: true si la operación fue exitosa, false si falló), data (objeto o array con los datos resultantes, null si no aplica), message (string descriptivo del resultado de la operación), timestamp (fecha y hora ISO 8601 de la respuesta). |
| | 2 | Si la operación fue exitosa, el sistema establece success=true y popula el campo data con el resultado. |
| | 3 | Si la operación falló, el sistema establece success=false, data=null y un mensaje descriptivo del error. |
| | 4 | El sistema establece el código de respuesta HTTP apropiado (200, 201, 400, 401, 403, 404, 500, 503). |
| | 5 | El sistema incluye el identificador de rastreo también en las cabeceras HTTP (X-Request-ID). |
| | 6 | El sistema serializa el objeto JSON y lo envía como cuerpo de la respuesta HTTP. |
| | | |
| **Secuencia alterna** | No aplica | |
| | | |
| **Excepciones** | E1 | Si falla la serialización del objeto data por contener datos no serializables, el sistema convierte el objeto a string y lo incluye en el campo message con un mensaje de advertencia. |
| | E2 | Si falla la generación del timestamp, el sistema usa null y registra el error en logs. |
| | | |
| **Postcondición** | El sistema ha retornado una respuesta con estructura estándar y consistente. | |
| | El usuario o servicio consumidor puede interpretar la respuesta de forma uniforme. | |
| | | |
| **Comentarios** | Este requisito implementa la regla transversal de "Estructura de Respuesta Estándar" del sistema. Ejemplo de respuesta exitosa: `{"request_id": "USR-1709856234-a3f8b2c1", "success": true, "data": {"id": 1, "username": "jdoe"}, "message": "Usuario creado exitosamente", "timestamp": "2026-03-02T10:30:45Z"}`. Ejemplo de respuesta fallida: `{"request_id": "USR-1709856234-a3f8b2c1", "success": false, "data": null, "message": "El correo electrónico ya está registrado", "timestamp": "2026-03-02T10:30:45Z"}`. | |

---

# Categoría 2: Requisitos Funcionales por Entidad

---

## Entidad: Usuarios

---

## USR-RF-006

| | | |
|---|---|---|
| **Código** | USR-RF-006 | |
| **Nombre** | Crear nuevo usuario en el sistema | |
| **Descripción** | Permite registrar un nuevo usuario en el sistema con sus credenciales de acceso y asignación de rol. | |
| **Actores** | Administrador del sistema, ms-usuarios, ms-roles, ms-auditoria, ms-notificaciones | |
| | | |
| **Precondición** | Ejecutar [USR-RF-001] (Validación de sesión). | |
| | Ejecutar [USR-RF-002] (Validación de permisos con código: USR_CREATE). | |
| | Ejecutar [USR-RF-003] (Generación de Request ID). | |
| | Los datos requeridos del usuario están disponibles: username, email, password (cifrada), rol_id. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | El sistema recibe los datos del nuevo usuario: username, email, password_encrypted, rol_id. |
| | 2 | El sistema valida que el username no esté vacío y tenga al menos 3 caracteres. |
| | 3 | El sistema valida que el email tenga formato válido de correo electrónico. |
| | 4 | El sistema consulta la base de datos para verificar que el username no esté duplicado. |
| | 5 | El sistema consulta la base de datos para verificar que el email no esté duplicado. |
| | 6 | El sistema invoca a ms-roles [ROL] con el rol_id para verificar que el rol existe y está activo. |
| | 7 | ms-roles confirma que el rol existe. |
| | 8 | El sistema descifra la contraseña recibida utilizando AES-256. |
| | 9 | El sistema genera un hash de la contraseña descifrada utilizando bcrypt con factor de costo 12. |
| | 10 | El sistema crea un registro en la tabla usr_usuarios con: username, email, password_hash, estado='activo', rol_id, created_at=timestamp actual, updated_at=timestamp actual. |
| | 11 | El sistema confirma la inserción y obtiene el ID del usuario creado. |
| | 12 | El sistema invoca a ms-notificaciones [NOT] para enviar una notificación de bienvenida al usuario (de forma asíncrona). |
| | 13 | El sistema ejecuta [USR-RF-004] para registrar la operación en auditoría. |
| | 14 | El sistema ejecuta [USR-RF-005] para retornar la respuesta estándar con los datos del usuario creado (sin incluir password_hash) y código HTTP 201 (Creado). |
| | | |
| **Secuencia alterna** | 4A | Si el username ya existe en la base de datos, el sistema rechaza la creación. |
| | 4B | El sistema ejecuta [USR-RF-004] para registrar el intento fallido. |
| | 4C | El sistema ejecuta [USR-RF-005] retornando success=false, message="El nombre de usuario ya está registrado", código HTTP 400. |
| | | |
| | 5A | Si el email ya existe en la base de datos, el sistema rechaza la creación. |
| | 5B | El sistema ejecuta [USR-RF-004] para registrar el intento fallido. |
| | 5C | El sistema ejecuta [USR-RF-005] retornando success=false, message="El correo electrónico ya está registrado", código HTTP 400. |
| | | |
| | 7A | Si ms-roles responde que el rol no existe o está inactivo, el sistema rechaza la creación. |
| | 7B | El sistema ejecuta [USR-RF-004] para registrar el intento fallido. |
| | 7C | El sistema ejecuta [USR-RF-005] retornando success=false, message="El rol especificado no es válido", código HTTP 400. |
| | | |
| **Excepciones** | E1 | Si el descifrado de la contraseña falla, el sistema rechaza la creación con código 400 y message="Error al procesar la contraseña". |
| | E2 | Si la generación del hash bcrypt falla, el sistema registra un error crítico en logs y rechaza la creación con código 500. |
| | E3 | Si la inserción en la base de datos falla por error de conexión o constraint, el sistema ejecuta rollback de la transacción y rechaza con código 500. |
| | E4 | Si ms-roles no responde, el sistema rechaza la creación por seguridad con código 503 (Servicio no disponible). |
| | E5 | Si el envío de notificación falla, el sistema continúa normalmente (la notificación no es crítica). |
| | | |
| **Postcondición** | El usuario ha sido creado exitosamente en la base de datos con estado 'activo'. | |
| | La contraseña está almacenada de forma segura como hash bcrypt. | |
| | Se ha enviado una notificación de bienvenida al usuario. | |
| | La operación ha sido registrada en auditoría. | |
| | | |
| **Comentarios** | La contraseña se recibe cifrada con AES-256 en formato Base64 desde el cliente, se descifra en el servidor y se almacena como hash bcrypt. El campo rol_id es una referencia externa a ms-roles y no existe FK real en base de datos, por eso se valida su existencia mediante invocación al servicio. El perfil extendido del usuario se crea posteriormente mediante [USR-RF-014]. El código de permiso requerido para esta funcionalidad es USR_CREATE. | |

---

## USR-RF-007

| | | |
|---|---|---|
| **Código** | USR-RF-007 | |
| **Nombre** | Consultar usuario por identificador | |
| **Descripción** | Permite obtener los datos completos de un usuario específico mediante su identificador único. | |
| **Actores** | Usuario del sistema, ms-usuarios, ms-auditoria | |
| | | |
| **Precondición** | Ejecutar [USR-RF-001] (Validación de sesión). | |
| | Ejecutar [USR-RF-002] (Validación de permisos con código: USR_READ). | |
| | Ejecutar [USR-RF-003] (Generación de Request ID). | |
| | Se conoce el identificador (ID) del usuario a consultar. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | El sistema recibe el identificador (ID) del usuario a consultar. |
| | 2 | El sistema valida que el ID sea un número entero positivo. |
| | 3 | El sistema consulta la tabla usr_usuarios filtrando por id = ID recibido. |
| | 4 | El sistema verifica que el registro exista. |
| | 5 | El sistema obtiene todos los campos del usuario excepto password_hash. |
| | 6 | El sistema ejecuta [USR-RF-004] para registrar la consulta en auditoría. |
| | 7 | El sistema ejecuta [USR-RF-005] para retornar la respuesta estándar con los datos del usuario y código HTTP 200. |
| | | |
| **Secuencia alterna** | 4A | Si no existe un usuario con el ID especificado, el sistema retorna un resultado vacío. |
| | 4B | El sistema ejecuta [USR-RF-004] para registrar la consulta fallida. |
| | 4C | El sistema ejecuta [USR-RF-005] retornando success=false, data=null, message="Usuario no encontrado", código HTTP 404. |
| | | |
| **Excepciones** | E1 | Si el ID no es un número entero válido, el sistema rechaza la consulta con código 400 y message="Identificador de usuario inválido". |
| | E2 | Si la consulta a la base de datos falla por error de conexión, el sistema retorna código 500 (Error interno). |
| | | |
| **Postcondición** | Se han retornado los datos del usuario solicitado (sin incluir password_hash). | |
| | La consulta ha sido registrada en auditoría. | |
| | | |
| **Comentarios** | Por seguridad, el campo password_hash NUNCA debe ser incluido en las respuestas del servicio. Esta funcionalidad es consumida principalmente por otros microservicios que necesitan validar la existencia y obtener datos de usuarios. El código de permiso requerido es USR_READ. | |

---

## USR-RF-008

| | | |
|---|---|---|
| **Código** | USR-RF-008 | |
| **Nombre** | Consultar usuario por correo electrónico | |
| **Descripción** | Permite obtener los datos completos de un usuario mediante su correo electrónico. Funcionalidad crítica utilizada por ms-autenticacion durante el inicio de sesión. | |
| **Actores** | ms-autenticacion, ms-usuarios, ms-auditoria | |
| | | |
| **Precondición** | Si la petición proviene de un usuario: Ejecutar [USR-RF-001] y [USR-RF-002] con código USR_READ. | |
| | Si la petición proviene de ms-autenticacion: Validar token de aplicación. | |
| | Ejecutar [USR-RF-003] (Generación de Request ID). | |
| | Se conoce el correo electrónico del usuario a consultar. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | El sistema recibe el correo electrónico del usuario a consultar. |
| | 2 | El sistema valida que el email tenga formato válido de correo electrónico. |
| | 3 | El sistema consulta la tabla usr_usuarios filtrando por email = email recibido. |
| | 4 | El sistema verifica que el registro exista. |
| | 5 | El sistema obtiene todos los campos del usuario. |
| | 6 | Si la petición proviene de ms-autenticacion (validación de credenciales), el sistema INCLUYE el campo password_hash en la respuesta. |
| | 7 | Si la petición proviene de cualquier otro origen, el sistema EXCLUYE el campo password_hash de la respuesta. |
| | 8 | El sistema ejecuta [USR-RF-004] para registrar la consulta en auditoría. |
| | 9 | El sistema ejecuta [USR-RF-005] para retornar la respuesta estándar con los datos del usuario y código HTTP 200. |
| | | |
| **Secuencia alterna** | 4A | Si no existe un usuario con el email especificado, el sistema retorna un resultado vacío. |
| | 4B | El sistema ejecuta [USR-RF-004] para registrar la consulta fallida. |
| | 4C | El sistema ejecuta [USR-RF-005] retornando success=false, data=null, message="Usuario no encontrado", código HTTP 404. |
| | | |
| **Excepciones** | E1 | Si el email no tiene formato válido, el sistema rechaza la consulta con código 400 y message="Formato de correo electrónico inválido". |
| | E2 | Si la consulta a la base de datos falla por error de conexión, el sistema retorna código 500 (Error interno). |
| | | |
| **Postcondición** | Se han retornado los datos del usuario solicitado. | |
| | Si el solicitante es ms-autenticacion, se incluye el password_hash para validación de credenciales. | |
| | La consulta ha sido registrada en auditoría. | |
| | | |
| **Comentarios** | Esta es una funcionalidad crítica del sistema consumida principalmente por ms-autenticacion durante el flujo de inicio de sesión. La inclusión del password_hash en la respuesta está restringida únicamente a peticiones autenticadas mediante token de aplicación de ms-autenticacion. El índice en el campo email garantiza consultas rápidas. | |

---

## USR-RF-009

| | | |
|---|---|---|
| **Código** | USR-RF-009 | |
| **Nombre** | Consultar usuario por número de documento | |
| **Descripción** | Permite obtener los datos de un usuario mediante su número de documento de identidad. | |
| **Actores** | Usuario del sistema, ms-usuarios, ms-auditoria | |
| | | |
| **Precondición** | Ejecutar [USR-RF-001] (Validación de sesión). | |
| | Ejecutar [USR-RF-002] (Validación de permisos con código: USR_READ). | |
| | Ejecutar [USR-RF-003] (Generación de Request ID). | |
| | Se conoce el número de documento del usuario a consultar. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | El sistema recibe el número de documento del usuario a consultar. |
| | 2 | El sistema valida que el número de documento no esté vacío. |
| | 3 | El sistema consulta la tabla usr_perfiles filtrando por numero_documento = número recibido. |
| | 4 | El sistema verifica que el registro del perfil exista. |
| | 5 | El sistema obtiene el usuario_id del perfil encontrado. |
| | 6 | El sistema consulta la tabla usr_usuarios usando el usuario_id obtenido. |
| | 7 | El sistema combina los datos de usr_usuarios y usr_perfiles en una sola respuesta, excluyendo password_hash. |
| | 8 | El sistema ejecuta [USR-RF-004] para registrar la consulta en auditoría. |
| | 9 | El sistema ejecuta [USR-RF-005] para retornar la respuesta estándar con los datos combinados y código HTTP 200. |
| | | |
| **Secuencia alterna** | 4A | Si no existe un perfil con el número de documento especificado, el sistema retorna un resultado vacío. |
| | 4B | El sistema ejecuta [USR-RF-004] para registrar la consulta fallida. |
| | 4C | El sistema ejecuta [USR-RF-005] retornando success=false, data=null, message="Usuario con ese número de documento no encontrado", código HTTP 404. |
| | | |
| **Excepciones** | E1 | Si el número de documento está vacío o contiene solo espacios en blanco, el sistema rechaza la consulta con código 400 y message="Número de documento inválido". |
| | E2 | Si la consulta a la base de datos falla por error de conexión, el sistema retorna código 500 (Error interno). |
| | | |
| **Postcondición** | Se han retornado los datos combinados del usuario y su perfil (sin incluir password_hash). | |
| | La consulta ha sido registrada en auditoría. | |
| | | |
| **Comentarios** | Esta funcionalidad requiere realizar un JOIN lógico entre usr_usuarios y usr_perfiles. El índice en numero_documento garantiza consultas rápidas. El código de permiso requerido es USR_READ. | |

---

## USR-RF-010

| | | |
|---|---|---|
| **Código** | USR-RF-010 | |
| **Nombre** | Actualizar datos básicos del usuario | |
| **Descripción** | Permite modificar los datos básicos de un usuario existente: username, email y rol_id. | |
| **Actores** | Administrador del sistema, ms-usuarios, ms-roles, ms-auditoria | |
| | | |
| **Precondición** | Ejecutar [USR-RF-001] (Validación de sesión). | |
| | Ejecutar [USR-RF-002] (Validación de permisos con código: USR_UPDATE). | |
| | Ejecutar [USR-RF-003] (Generación de Request ID). | |
| | El usuario a actualizar existe en el sistema. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | El sistema recibe el ID del usuario a actualizar y los nuevos datos: username (opcional), email (opcional), rol_id (opcional). |
| | 2 | El sistema valida que al menos un campo a actualizar esté presente. |
| | 3 | El sistema consulta la tabla usr_usuarios para verificar que el usuario existe. |
| | 4 | Si se proporciona username, el sistema valida que no esté vacío y tenga al menos 3 caracteres. |
| | 5 | Si se proporciona email, el sistema valida que tenga formato válido de correo electrónico. |
| | 6 | Si se proporciona username diferente al actual, el sistema verifica que no exista otro usuario con ese username. |
| | 7 | Si se proporciona email diferente al actual, el sistema verifica que no exista otro usuario con ese email. |
| | 8 | Si se proporciona rol_id, el sistema invoca a ms-roles [ROL] para verificar que el rol existe y está activo. |
| | 9 | El sistema actualiza el registro en usr_usuarios con los nuevos valores proporcionados. |
| | 10 | El sistema actualiza el campo updated_at con el timestamp actual. |
| | 11 | El sistema confirma la actualización. |
| | 12 | El sistema ejecuta [USR-RF-004] para registrar la actualización en auditoría. |
| | 13 | El sistema ejecuta [USR-RF-005] para retornar la respuesta estándar con los datos actualizados del usuario y código HTTP 200. |
| | | |
| **Secuencia alterna** | 3A | Si el usuario no existe en la base de datos, el sistema rechaza la actualización. |
| | 3B | El sistema ejecuta [USR-RF-004] para registrar el intento fallido. |
| | 3C | El sistema ejecuta [USR-RF-005] retornando success=false, message="Usuario no encontrado", código HTTP 404. |
| | | |
| | 6A | Si el nuevo username ya está siendo utilizado por otro usuario, el sistema rechaza la actualización. |
| | 6B | El sistema ejecuta [USR-RF-004] para registrar el intento fallido. |
| | 6C | El sistema ejecuta [USR-RF-005] retornando success=false, message="El nombre de usuario ya está registrado", código HTTP 400. |
| | | |
| | 7A | Si el nuevo email ya está siendo utilizado por otro usuario, el sistema rechaza la actualización. |
| | 7B | El sistema ejecuta [USR-RF-004] para registrar el intento fallido. |
| | 7C | El sistema ejecuta [USR-RF-005] retornando success=false, message="El correo electrónico ya está registrado", código HTTP 400. |
| | | |
| | 8A | Si ms-roles responde que el nuevo rol no existe o está inactivo, el sistema rechaza la actualización. |
| | 8B | El sistema ejecuta [USR-RF-004] para registrar el intento fallido. |
| | 8C | El sistema ejecuta [USR-RF-005] retornando success=false, message="El rol especificado no es válido", código HTTP 400. |
| | | |
| **Excepciones** | E1 | Si no se proporciona ningún campo a actualizar, el sistema rechaza con código 400 y message="Debe proporcionar al menos un campo a actualizar". |
| | E2 | Si la actualización en la base de datos falla por error de conexión o constraint, el sistema ejecuta rollback y rechaza con código 500. |
| | E3 | Si ms-roles no responde, el sistema rechaza la actualización por seguridad con código 503 (Servicio no disponible). |
| | | |
| **Postcondición** | Los datos básicos del usuario han sido actualizados exitosamente. | |
| | El campo updated_at refleja el timestamp de la última actualización. | |
| | La operación ha sido registrada en auditoría. | |
| | | |
| **Comentarios** | Esta funcionalidad NO permite actualizar la contraseña (para eso existe [USR-RF-022]). Los datos del perfil extendido se actualizan mediante [USR-RF-014]. El código de permiso requerido es USR_UPDATE. Solo se actualizan los campos que se proporcionen en la petición (actualización parcial). | |

---

## USR-RF-011

| | | |
|---|---|---|
| **Código** | USR-RF-011 | |
| **Nombre** | Desactivar usuario del sistema | |
| **Descripción** | Permite desactivar lógicamente un usuario, cambiando su estado a 'inactivo' sin eliminar el registro de la base de datos. | |
| **Actores** | Administrador del sistema, ms-usuarios, ms-auditoria, ms-notificaciones | |
| | | |
| **Precondición** | Ejecutar [USR-RF-001] (Validación de sesión). | |
| | Ejecutar [USR-RF-002] (Validación de permisos con código: USR_DELETE). | |
| | Ejecutar [USR-RF-003] (Generación de Request ID). | |
| | El usuario a desactivar existe en el sistema. | |
| | Se proporciona un motivo obligatorio para la desactivación. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | El sistema recibe el ID del usuario a desactivar y el motivo de la desactivación. |
| | 2 | El sistema valida que el motivo no esté vacío. |
| | 3 | El sistema consulta la tabla usr_usuarios para verificar que el usuario existe. |
| | 4 | El sistema verifica que el usuario no esté ya en estado 'inactivo'. |
| | 5 | El sistema almacena el estado actual del usuario (para el historial). |
| | 6 | El sistema actualiza el registro en usr_usuarios cambiando estado='inactivo'. |
| | 7 | El sistema actualiza el campo updated_at con el timestamp actual. |
| | 8 | El sistema ejecuta [USR-RF-015] para registrar el cambio de estado en el historial con el motivo proporcionado. |
| | 9 | El sistema invoca a ms-notificaciones [NOT] para enviar una notificación de desactivación al usuario (de forma asíncrona). |
| | 10 | El sistema ejecuta [USR-RF-004] para registrar la desactivación en auditoría. |
| | 11 | El sistema ejecuta [USR-RF-005] para retornar la respuesta estándar con mensaje de confirmación y código HTTP 200. |
| | | |
| **Secuencia alterna** | 3A | Si el usuario no existe en la base de datos, el sistema rechaza la desactivación. |
| | 3B | El sistema ejecuta [USR-RF-004] para registrar el intento fallido. |
| | 3C | El sistema ejecuta [USR-RF-005] retornando success=false, message="Usuario no encontrado", código HTTP 404. |
| | | |
| | 4A | Si el usuario ya está en estado 'inactivo', el sistema rechaza la desactivación. |
| | 4B | El sistema ejecuta [USR-RF-004] para registrar el intento. |
| | 4C | El sistema ejecuta [USR-RF-005] retornando success=false, message="El usuario ya se encuentra inactivo", código HTTP 400. |
| | | |
| **Excepciones** | E1 | Si el motivo está vacío o contiene solo espacios en blanco, el sistema rechaza con código 400 y message="Debe proporcionar un motivo para la desactivación". |
| | E2 | Si la actualización en la base de datos falla, el sistema ejecuta rollback y rechaza con código 500. |
| | E3 | Si falla el registro en el historial de estados, el sistema ejecuta rollback de toda la transacción y rechaza con código 500. |
| | E4 | Si el envío de notificación falla, el sistema continúa normalmente (la notificación no es crítica). |
| | | |
| **Postcondición** | El usuario ha sido desactivado (estado='inactivo'). | |
| | Se ha registrado el cambio de estado en el historial con el motivo proporcionado. | |
| | Se ha enviado una notificación al usuario informando la desactivación. | |
| | La operación ha sido registrada en auditoría. | |
| | | |
| **Comentarios** | La desactivación es lógica (soft delete): el registro NO se elimina de la base de datos, solo cambia su estado. Un usuario desactivado no puede iniciar sesión en el sistema. El motivo es obligatorio para mantener trazabilidad y cumplir con requisitos de auditoría. El código de permiso requerido es USR_DELETE. Para reactivar un usuario usar [USR-RF-020]. | |

---

## USR-RF-012

| | | |
|---|---|---|
| **Código** | USR-RF-012 | |
| **Nombre** | Búsqueda avanzada de usuarios con filtros | |
| **Descripción** | Permite buscar usuarios aplicando múltiples filtros simultáneamente, con paginación de resultados. | |
| **Actores** | Usuario del sistema, ms-usuarios, ms-auditoria | |
| | | |
| **Precondición** | Ejecutar [USR-RF-001] (Validación de sesión). | |
| | Ejecutar [USR-RF-002] (Validación de permisos con código: USR_SEARCH). | |
| | Ejecutar [USR-RF-003] (Generación de Request ID). | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | El sistema recibe los parámetros de búsqueda opcionales: nombre (busca en primer_nombre y primer_apellido), numero_documento, email, estado, ciudad, pagina (número de página, default=1), items_por_pagina (cantidad de resultados por página, default=10). |
| | 2 | El sistema valida que items_por_pagina sea un valor entre 1 y 100. |
| | 3 | El sistema valida que pagina sea un número entero positivo mayor o igual a 1. |
| | 4 | El sistema construye una consulta SQL que realiza JOIN entre usr_usuarios y usr_perfiles. |
| | 5 | El sistema aplica los filtros proporcionados: si se proporciona nombre, filtra donde primer_nombre LIKE %nombre% OR primer_apellido LIKE %nombre%; si se proporciona numero_documento, filtra por numero_documento exacto; si se proporciona email, filtra por email LIKE %email%; si se proporciona estado, filtra por estado exacto; si se proporciona ciudad, filtra por ciudad LIKE %ciudad%. |
| | 6 | El sistema cuenta el total de registros que coinciden con los filtros (sin aplicar paginación). |
| | 7 | El sistema calcula el total de páginas: CEIL(total_registros / items_por_pagina). |
| | 8 | El sistema aplica paginación: OFFSET=(pagina-1)*items_por_pagina, LIMIT=items_por_pagina. |
| | 9 | El sistema ejecuta la consulta y obtiene los resultados de la página actual, excluyendo password_hash. |
| | 10 | El sistema construye la respuesta con: resultados (array de usuarios), total_registros, total_paginas, pagina_actual, items_por_pagina. |
| | 11 | El sistema ejecuta [USR-RF-004] para registrar la búsqueda en auditoría. |
| | 12 | El sistema ejecuta [USR-RF-005] para retornar la respuesta estándar con los resultados paginados y código HTTP 200. |
| | | |
| **Secuencia alterna** | 6A | Si no existen registros que coincidan con los filtros, el sistema retorna un array vacío. |
| | 6B | El sistema incluye en la respuesta: resultados=[], total_registros=0, total_paginas=0, pagina_actual=pagina solicitada, items_por_pagina. |
| | 6C | El sistema ejecuta [USR-RF-004] para registrar la búsqueda sin resultados. |
| | 6D | El sistema ejecuta [USR-RF-005] retornando success=true, data con la estructura vacía, código HTTP 200. |
| | | |
| **Excepciones** | E1 | Si items_por_pagina es menor a 1 o mayor a 100, el sistema rechaza con código 400 y message="items_por_pagina debe estar entre 1 y 100". |
| | E2 | Si pagina es menor a 1, el sistema rechaza con código 400 y message="El número de página debe ser mayor o igual a 1". |
| | E3 | Si la consulta a la base de datos falla por error de conexión, el sistema retorna código 500 (Error interno). |
| | | |
| **Postcondición** | Se han retornado los usuarios que coinciden con los filtros de búsqueda. | |
| | La respuesta incluye información de paginación completa (total de registros, total de páginas, página actual). | |
| | La búsqueda ha sido registrada en auditoría. | |
| | | |
| **Comentarios** | Todos los filtros son opcionales y se pueden combinar libremente. Si no se proporciona ningún filtro, se retornan todos los usuarios paginados. Los campos nombre, email y ciudad usan búsqueda parcial (LIKE con wildcards), mientras que numero_documento y estado usan búsqueda exacta. El password_hash NUNCA se incluye en los resultados. Los índices en los campos de búsqueda garantizan consultas eficientes. El código de permiso requerido es USR_SEARCH. | |

---

## Entidad: Perfiles

---

## USR-RF-013

| | | |
|---|---|---|
| **Código** | USR-RF-013 | |
| **Nombre** | Consultar perfil extendido de usuario | |
| **Descripción** | Permite obtener toda la información personal y de contacto extendida de un usuario específico. | |
| **Actores** | Usuario del sistema, ms-usuarios, ms-auditoria | |
| | | |
| **Precondición** | Ejecutar [USR-RF-001] (Validación de sesión). | |
| | Ejecutar [USR-RF-002] (Validación de permisos con código: USR_PROFILE_READ). | |
| | Ejecutar [USR-RF-003] (Generación de Request ID). | |
| | El usuario para el cual se consulta el perfil existe en el sistema. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | El sistema recibe el ID del usuario cuyo perfil se desea consultar. |
| | 2 | El sistema valida que el ID sea un número entero positivo. |
| | 3 | El sistema consulta la tabla usr_perfiles filtrando por usuario_id = ID recibido. |
| | 4 | El sistema verifica que exista un registro de perfil para ese usuario. |
| | 5 | El sistema obtiene todos los campos del perfil. |
| | 6 | El sistema consulta la tabla usr_tipos_documento para obtener el nombre completo del tipo de documento. |
| | 7 | El sistema combina los datos del perfil con la información del tipo de documento. |
| | 8 | El sistema ejecuta [USR-RF-004] para registrar la consulta en auditoría. |
| | 9 | El sistema ejecuta [USR-RF-005] para retornar la respuesta estándar con los datos del perfil y código HTTP 200. |
| | | |
| **Secuencia alterna** | 4A | Si no existe un perfil para el usuario especificado, el sistema retorna un resultado vacío. |
| | 4B | El sistema ejecuta [USR-RF-004] para registrar la consulta fallida. |
| | 4C | El sistema ejecuta [USR-RF-005] retornando success=false, data=null, message="Perfil no encontrado para el usuario especificado", código HTTP 404. |
| | | |
| **Excepciones** | E1 | Si el ID no es un número entero válido, el sistema rechaza la consulta con código 400 y message="Identificador de usuario inválido". |
| | E2 | Si la consulta a la base de datos falla por error de conexión, el sistema retorna código 500 (Error interno). |
| | | |
| **Postcondición** | Se han retornado todos los datos del perfil extendido del usuario. | |
| | La consulta ha sido registrada en auditoría. | |
| | | |
| **Comentarios** | El perfil extendido contiene información personal detallada del usuario: datos del documento de identidad, nombres completos, fecha de nacimiento, género, dirección, teléfonos, contacto de emergencia y biografía. Esta información es consultada por ms-notificaciones para obtener datos de contacto. El código de permiso requerido es USR_PROFILE_READ. | |

---

## USR-RF-014

| | | |
|---|---|---|
| **Código** | USR-RF-014 | |
| **Nombre** | Actualizar perfil extendido de usuario | |
| **Descripción** | Permite crear o modificar la información personal y de contacto extendida de un usuario. | |
| **Actores** | Usuario del sistema, ms-usuarios, ms-auditoria | |
| | | |
| **Precondición** | Ejecutar [USR-RF-001] (Validación de sesión). | |
| | Ejecutar [USR-RF-002] (Validación de permisos con código: USR_PROFILE_UPDATE). | |
| | Ejecutar [USR-RF-003] (Generación de Request ID). | |
| | El usuario para el cual se actualiza el perfil existe en el sistema. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | El sistema recibe el ID del usuario y los datos del perfil: tipo_documento_id, numero_documento, primer_nombre, segundo_nombre (opcional), primer_apellido, segundo_apellido (opcional), fecha_nacimiento, genero, direccion_residencia, ciudad, departamento, telefono_fijo (opcional), telefono_movil, contacto_emergencia_nombre, contacto_emergencia_telefono, biografia (opcional). |
| | 2 | El sistema valida que los campos obligatorios no estén vacíos. |
| | 3 | El sistema valida que fecha_nacimiento sea una fecha válida y que el usuario tenga al menos 14 años. |
| | 4 | El sistema valida que genero esté dentro de los valores permitidos: masculino, femenino, otro, prefiero_no_decir. |
| | 5 | El sistema consulta si ya existe un perfil para el usuario_id. |
| | 6 | Si existe un perfil, el sistema verifica si el numero_documento cambió. Si cambió, valida que el nuevo número no esté duplicado en otro perfil. |
| | 7 | Si NO existe un perfil, el sistema valida que el numero_documento no esté duplicado. |
| | 8 | El sistema consulta la tabla usr_tipos_documento para verificar que el tipo_documento_id existe y está activo. |
| | 9 | Si existe perfil, el sistema actualiza el registro en usr_perfiles con los nuevos datos y updated_at=timestamp actual. |
| | 10 | Si NO existe perfil, el sistema crea un nuevo registro en usr_perfiles con created_at=timestamp actual y updated_at=timestamp actual. |
| | 11 | El sistema confirma la operación. |
| | 12 | El sistema ejecuta [USR-RF-004] para registrar la actualización en auditoría. |
| | 13 | El sistema ejecuta [USR-RF-005] para retornar la respuesta estándar con los datos del perfil actualizado y código HTTP 200 (si actualización) o 201 (si creación). |
| | | |
| **Secuencia alterna** | 6A | Si el nuevo numero_documento ya existe en otro perfil, el sistema rechaza la actualización. |
| | 6B | El sistema ejecuta [USR-RF-004] para registrar el intento fallido. |
| | 6C | El sistema ejecuta [USR-RF-005] retornando success=false, message="El número de documento ya está registrado", código HTTP 400. |
| | | |
| | 8A | Si el tipo_documento_id no existe o está inactivo, el sistema rechaza la operación. |
| | 8B | El sistema ejecuta [USR-RF-004] para registrar el intento fallido. |
| | 8C | El sistema ejecuta [USR-RF-005] retornando success=false, message="Tipo de documento inválido", código HTTP 400. |
| | | |
| **Excepciones** | E1 | Si algún campo obligatorio está vacío, el sistema rechaza con código 400 y message="Faltan campos obligatorios: [lista de campos]". |
| | E2 | Si la fecha de nacimiento es inválida o el usuario es menor de 14 años, el sistema rechaza con código 400 y message="Fecha de nacimiento inválida o usuario menor de 14 años". |
| | E3 | Si el género no está en los valores permitidos, el sistema rechaza con código 400 y message="Género inválido. Valores permitidos: masculino, femenino, otro, prefiero_no_decir". |
| | E4 | Si la operación en la base de datos falla, el sistema ejecuta rollback y rechaza con código 500. |
| | | |
| **Postcondición** | El perfil extendido del usuario ha sido creado o actualizado exitosamente. | |
| | El campo numero_documento es único en el sistema. | |
| | La operación ha sido registrada en auditoría. | |
| | | |
| **Comentarios** | Esta funcionalidad tiene doble propósito: crear el perfil si no existe (típicamente después de [USR-RF-006]) o actualizar un perfil existente. El numero_documento debe ser único en todo el sistema y se valida mediante índice UNIQUE en base de datos. El código de permiso requerido es USR_PROFILE_UPDATE. Los campos opcionales pueden enviarse como null o no enviarse. | |

---

## Entidad: Historial de Estados

---

## USR-RF-015

| | | |
|---|---|---|
| **Código** | USR-RF-015 | |
| **Nombre** | Cambiar estado de usuario | |
| **Descripción** | Permite cambiar el estado de un usuario (activo, inactivo, suspendido) registrando el cambio en el historial con el motivo correspondiente. | |
| **Actores** | Administrador del sistema, ms-usuarios, ms-notificaciones, ms-auditoria | |
| | | |
| **Precondición** | Ejecutar [USR-RF-001] (Validación de sesión). | |
| | Ejecutar [USR-RF-002] (Validación de permisos con código: USR_CHANGE_STATE). | |
| | Ejecutar [USR-RF-003] (Generación de Request ID). | |
| | El usuario cuyo estado se va a cambiar existe en el sistema. | |
| | Se proporciona un motivo obligatorio para el cambio. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | El sistema recibe el ID del usuario, el nuevo estado a asignar y el motivo del cambio. |
| | 2 | El sistema valida que el nuevo estado esté dentro de los valores permitidos: activo, inactivo, suspendido. |
| | 3 | El sistema valida que el motivo no esté vacío. |
| | 4 | El sistema consulta la tabla usr_usuarios para obtener el estado actual del usuario. |
| | 5 | El sistema verifica que el usuario existe. |
| | 6 | El sistema verifica que el nuevo estado sea diferente al estado actual. |
| | 7 | El sistema obtiene el ID del usuario que está realizando el cambio (del token de sesión). |
| | 8 | El sistema actualiza el estado del usuario en usr_usuarios con estado=nuevo_estado. |
| | 9 | El sistema actualiza el campo updated_at con el timestamp actual. |
| | 10 | El sistema crea un registro en usr_historial_estados con: usuario_id, estado_anterior, estado_nuevo=nuevo_estado, motivo, usuario_modificador_id=ID del usuario que realiza el cambio, created_at=timestamp actual. |
| | 11 | El sistema confirma ambas operaciones en una transacción atómica. |
| | 12 | Si el nuevo estado es 'suspendido' o 'inactivo', el sistema invoca a ms-notificaciones [NOT] para enviar una notificación al usuario (de forma asíncrona). |
| | 13 | Si el nuevo estado es 'activo' y el anterior era 'inactivo' o 'suspendido', el sistema invoca a ms-notificaciones [NOT] para enviar una notificación de reactivación (de forma asíncrona). |
| | 14 | El sistema ejecuta [USR-RF-004] para registrar el cambio de estado en auditoría. |
| | 15 | El sistema ejecuta [USR-RF-005] para retornar la respuesta estándar con mensaje de confirmación y código HTTP 200. |
| | | |
| **Secuencia alterna** | 5A | Si el usuario no existe, el sistema rechaza el cambio. |
| | 5B | El sistema ejecuta [USR-RF-004] para registrar el intento fallido. |
| | 5C | El sistema ejecuta [USR-RF-005] retornando success=false, message="Usuario no encontrado", código HTTP 404. |
| | | |
| | 6A | Si el nuevo estado es igual al estado actual, el sistema rechaza el cambio. |
| | 6B | El sistema ejecuta [USR-RF-004] para registrar el intento. |
| | 6C | El sistema ejecuta [USR-RF-005] retornando success=false, message="El usuario ya se encuentra en el estado especificado", código HTTP 400. |
| | | |
| **Excepciones** | E1 | Si el nuevo estado no es un valor válido, el sistema rechaza con código 400 y message="Estado inválido. Valores permitidos: activo, inactivo, suspendido". |
| | E2 | Si el motivo está vacío, el sistema rechaza con código 400 y message="Debe proporcionar un motivo para el cambio de estado". |
| | E3 | Si alguna operación en la base de datos falla, el sistema ejecuta rollback de la transacción completa y rechaza con código 500. |
| | E4 | Si el envío de notificación falla, el sistema continúa normalmente (la notificación no es crítica). |
| | | |
| **Postcondición** | El estado del usuario ha sido actualizado en usr_usuarios. | |
| | Se ha creado un registro en usr_historial_estados con el cambio realizado. | |
| | Se ha enviado una notificación al usuario si corresponde. | |
| | La operación ha sido registrada en auditoría. | |
| | | |
| **Comentarios** | Esta funcionalidad es utilizada internamente por [USR-RF-011] (Desactivar usuario) y por [USR-RF-020] (Reactivar usuario). El historial de estados proporciona trazabilidad completa de todos los cambios realizados, incluyendo quién los realizó y por qué. Los tres estados posibles son: activo (puede iniciar sesión), inactivo (no puede iniciar sesión, desactivación lógica), suspendido (no puede iniciar sesión, suspensión temporal por razones administrativas). El código de permiso requerido es USR_CHANGE_STATE. | |

---

## USR-RF-016

| | | |
|---|---|---|
| **Código** | USR-RF-016 | |
| **Nombre** | Consultar historial de cambios de estado | |
| **Descripción** | Permite obtener el historial completo de cambios de estado de un usuario específico para auditoría y trazabilidad. | |
| **Actores** | Usuario del sistema, ms-usuarios, ms-auditoria | |
| | | |
| **Precondición** | Ejecutar [USR-RF-001] (Validación de sesión). | |
| | Ejecutar [USR-RF-002] (Validación de permisos con código: USR_HISTORY_READ). | |
| | Ejecutar [USR-RF-003] (Generación de Request ID). | |
| | El usuario cuyo historial se desea consultar existe en el sistema. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | El sistema recibe el ID del usuario cuyo historial se desea consultar. |
| | 2 | El sistema valida que el ID sea un número entero positivo. |
| | 3 | El sistema consulta la tabla usr_historial_estados filtrando por usuario_id = ID recibido. |
| | 4 | El sistema ordena los registros por created_at DESC (más recientes primero). |
| | 5 | Para cada registro del historial, el sistema obtiene los datos del usuario que realizó el cambio (usuario_modificador_id) consultando usr_usuarios. |
| | 6 | El sistema construye una lista con todos los cambios de estado, incluyendo: id del registro, estado_anterior, estado_nuevo, motivo, fecha y hora del cambio, datos del usuario modificador (nombre completo). |
| | 7 | El sistema ejecuta [USR-RF-004] para registrar la consulta en auditoría. |
| | 8 | El sistema ejecuta [USR-RF-005] para retornar la respuesta estándar con el historial completo y código HTTP 200. |
| | | |
| **Secuencia alterna** | 3A | Si no existen registros de cambios de estado para el usuario, el sistema retorna un array vacío. |
| | 3B | El sistema ejecuta [USR-RF-004] para registrar la consulta sin resultados. |
| | 3C | El sistema ejecuta [USR-RF-005] retornando success=true, data=[] (array vacío), message="No hay historial de cambios para este usuario", código HTTP 200. |
| | | |
| **Excepciones** | E1 | Si el ID no es un número entero válido, el sistema rechaza la consulta con código 400 y message="Identificador de usuario inválido". |
| | E2 | Si la consulta a la base de datos falla por error de conexión, el sistema retorna código 500 (Error interno). |
| | | |
| **Postcondición** | Se ha retornado el historial completo de cambios de estado del usuario. | |
| | Los registros están ordenados cronológicamente del más reciente al más antiguo. | |
| | La consulta ha sido registrada en auditoría. | |
| | | |
| **Comentarios** | El historial de estados es crítico para auditoría y cumplimiento de políticas de seguridad. Permite rastrear quién realizó cada cambio de estado, cuándo y por qué motivo. Esta información puede ser requerida para investigaciones internas o cumplimiento normativo. El código de permiso requerido es USR_HISTORY_READ. Si un usuario nunca ha cambiado de estado, el array estará vacío. | |

---

## Entidad: Tipos de Documento

---

## USR-RF-017

| | | |
|---|---|---|
| **Código** | USR-RF-017 | |
| **Nombre** | Consultar catálogo de tipos de documento | |
| **Descripción** | Permite obtener la lista completa de tipos de documento de identidad disponibles en el sistema. | |
| **Actores** | Usuario del sistema, ms-usuarios, ms-auditoria | |
| | | |
| **Precondición** | Ejecutar [USR-RF-001] (Validación de sesión). | |
| | Ejecutar [USR-RF-002] (Validación de permisos con código: USR_READ). | |
| | Ejecutar [USR-RF-003] (Generación de Request ID). | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | El sistema recibe la petición de consulta del catálogo de tipos de documento. |
| | 2 | El sistema consulta la tabla usr_tipos_documento filtrando por activo=true. |
| | 3 | El sistema ordena los registros por nombre ASC (orden alfabético). |
| | 4 | El sistema obtiene todos los campos de cada tipo de documento: id, codigo, nombre, descripcion. |
| | 5 | El sistema ejecuta [USR-RF-004] para registrar la consulta en auditoría. |
| | 6 | El sistema ejecuta [USR-RF-005] para retornar la respuesta estándar con la lista de tipos de documento y código HTTP 200. |
| | | |
| **Secuencia alterna** | 2A | Si no existen tipos de documento activos, el sistema retorna un array vacío. |
| | 2B | El sistema ejecuta [USR-RF-004] para registrar la consulta sin resultados. |
| | 2C | El sistema ejecuta [USR-RF-005] retornando success=true, data=[], message="No hay tipos de documento disponibles", código HTTP 200. |
| | | |
| **Excepciones** | E1 | Si la consulta a la base de datos falla por error de conexión, el sistema retorna código 500 (Error interno). |
| | | |
| **Postcondición** | Se ha retornado la lista completa de tipos de documento activos en el sistema. | |
| | La lista está ordenada alfabéticamente. | |
| | La consulta ha sido registrada en auditoría. | |
| | | |
| **Comentarios** | Este es un endpoint de catálogo utilizado principalmente por interfaces gráficas para mostrar las opciones disponibles al usuario cuando completa su perfil. Los tipos de documento típicos incluyen: CC (Cédula de Ciudadanía), TI (Tarjeta de Identidad), CE (Cédula de Extranjería), Pasaporte, etc. Solo se retornan tipos de documento con activo=true. El código de permiso requerido es USR_READ. | |

---

## Entidad: Preferencias de Notificación

---

## USR-RF-018

| | | |
|---|---|---|
| **Código** | USR-RF-018 | |
| **Nombre** | Consultar preferencias de notificación del usuario | |
| **Descripción** | Permite obtener las preferencias de notificación configuradas para un usuario específico. Funcionalidad consumida por ms-notificaciones. | |
| **Actores** | Usuario del sistema, ms-notificaciones, ms-usuarios, ms-auditoria | |
| | | |
| **Precondición** | Si la petición proviene de un usuario: Ejecutar [USR-RF-001] y [USR-RF-002] con código USR_PREFERENCES_READ. | |
| | Si la petición proviene de ms-notificaciones: Validar token de aplicación. | |
| | Ejecutar [USR-RF-003] (Generación de Request ID). | |
| | El usuario cuyas preferencias se desean consultar existe en el sistema. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | El sistema recibe el ID del usuario cuyas preferencias se desean consultar. |
| | 2 | El sistema valida que el ID sea un número entero positivo. |
| | 3 | El sistema consulta la tabla usr_preferencias_notificacion filtrando por usuario_id = ID recibido. |
| | 4 | El sistema verifica que exista un registro de preferencias para ese usuario. |
| | 5 | El sistema obtiene todos los campos de preferencias: notif_email, notif_sms, notif_push, canal_preferido, horario_no_molestar_inicio, horario_no_molestar_fin. |
| | 6 | El sistema ejecuta [USR-RF-004] para registrar la consulta en auditoría. |
| | 7 | El sistema ejecuta [USR-RF-005] para retornar la respuesta estándar con las preferencias y código HTTP 200. |
| | | |
| **Secuencia alterna** | 4A | Si no existen preferencias configuradas para el usuario, el sistema retorna preferencias por defecto. |
| | 4B | El sistema construye un objeto con valores por defecto: notif_email=true, notif_sms=false, notif_push=true, canal_preferido='email', horario_no_molestar_inicio=null, horario_no_molestar_fin=null. |
| | 4C | El sistema ejecuta [USR-RF-004] para registrar la consulta con resultado por defecto. |
| | 4D | El sistema ejecuta [USR-RF-005] retornando success=true, data con las preferencias por defecto, código HTTP 200. |
| | | |
| **Excepciones** | E1 | Si el ID no es un número entero válido, el sistema rechaza la consulta con código 400 y message="Identificador de usuario inválido". |
| | E2 | Si la consulta a la base de datos falla por error de conexión, el sistema retorna código 500 (Error interno). |
| | | |
| **Postcondición** | Se han retornado las preferencias de notificación del usuario (configuradas o por defecto). | |
| | La consulta ha sido registrada en auditoría. | |
| | | |
| **Comentarios** | Esta funcionalidad es crítica para ms-notificaciones, que la consulta antes de enviar cualquier notificación para respetar las preferencias del usuario. Si un usuario no ha configurado preferencias, se retornan valores por defecto razonables. El horario de no molestar define un rango de tiempo donde no se deben enviar notificaciones no urgentes. El código de permiso requerido es USR_PREFERENCES_READ. | |

---

## USR-RF-019

| | | |
|---|---|---|
| **Código** | USR-RF-019 | |
| **Nombre** | Actualizar preferencias de notificación del usuario | |
| **Descripción** | Permite crear o modificar las preferencias de notificación de un usuario. | |
| **Actores** | Usuario del sistema, ms-usuarios, ms-auditoria | |
| | | |
| **Precondición** | Ejecutar [USR-RF-001] (Validación de sesión). | |
| | Ejecutar [USR-RF-002] (Validación de permisos con código: USR_PREFERENCES_UPDATE). | |
| | Ejecutar [USR-RF-003] (Generación de Request ID). | |
| | El usuario cuyas preferencias se van a actualizar existe en el sistema. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | El sistema recibe el ID del usuario y las nuevas preferencias: notif_email (boolean), notif_sms (boolean), notif_push (boolean), canal_preferido (string), horario_no_molestar_inicio (time, opcional), horario_no_molestar_fin (time, opcional). |
| | 2 | El sistema valida que al menos un campo a actualizar esté presente. |
| | 3 | El sistema valida que canal_preferido esté dentro de los valores permitidos: email, sms, push. |
| | 4 | Si se proporcionan horarios de no molestar, el sistema valida que ambos (inicio y fin) sean proporcionados. |
| | 5 | El sistema valida que horario_no_molestar_inicio sea anterior a horario_no_molestar_fin. |
| | 6 | El sistema consulta si ya existen preferencias para el usuario_id. |
| | 7 | Si existen preferencias, el sistema actualiza el registro en usr_preferencias_notificacion con los nuevos valores y updated_at=timestamp actual. |
| | 8 | Si NO existen preferencias, el sistema crea un nuevo registro con los valores proporcionados (usando defaults para campos no proporcionados) y created_at=timestamp actual. |
| | 9 | El sistema confirma la operación. |
| | 10 | El sistema ejecuta [USR-RF-004] para registrar la actualización en auditoría. |
| | 11 | El sistema ejecuta [USR-RF-005] para retornar la respuesta estándar con las preferencias actualizadas y código HTTP 200 (si actualización) o 201 (si creación). |
| | | |
| **Secuencia alterna** | 4A | Si se proporciona solo horario_no_molestar_inicio o solo horario_no_molestar_fin (no ambos), el sistema rechaza la actualización. |
| | 4B | El sistema ejecuta [USR-RF-004] para registrar el intento fallido. |
| | 4C | El sistema ejecuta [USR-RF-005] retornando success=false, message="Debe proporcionar ambos horarios de no molestar o ninguno", código HTTP 400. |
| | | |
| | 5A | Si horario_no_molestar_inicio es posterior o igual a horario_no_molestar_fin, el sistema rechaza la actualización. |
| | 5B | El sistema ejecuta [USR-RF-004] para registrar el intento fallido. |
| | 5C | El sistema ejecuta [USR-RF-005] retornando success=false, message="El horario de inicio debe ser anterior al horario de fin", código HTTP 400. |
| | | |
| **Excepciones** | E1 | Si canal_preferido no es un valor válido, el sistema rechaza con código 400 y message="Canal preferido inválido. Valores permitidos: email, sms, push". |
| | E2 | Si no se proporciona ningún campo a actualizar, el sistema rechaza con código 400 y message="Debe proporcionar al menos un campo a actualizar". |
| | E3 | Si la operación en la base de datos falla, el sistema ejecuta rollback y rechaza con código 500. |
| | | |
| **Postcondición** | Las preferencias de notificación del usuario han sido creadas o actualizadas exitosamente. | |
| | ms-notificaciones respetará estas preferencias al enviar notificaciones al usuario. | |
| | La operación ha sido registrada en auditoría. | |
| | | |
| **Comentarios** | Esta funcionalidad tiene doble propósito: crear preferencias si no existen o actualizar las existentes. Los usuarios pueden desactivar completamente ciertos canales de notificación estableciendo los campos booleanos en false. El horario de no molestar es opcional y define un rango de tiempo donde el usuario no desea recibir notificaciones no urgentes. El código de permiso requerido es USR_PREFERENCES_UPDATE. | |

---

# Categoría 3: Requisitos Sugeridos

---

## USR-RF-020

**Justificación:** Aunque el documento original menciona la desactivación de usuarios, no incluye explícitamente la funcionalidad inversa (reactivación). Para ofrecer un ciclo de vida completo de gestión de usuarios y evitar la necesidad de crear usuarios duplicados cuando alguien regresa a la institución, se sugiere implementar una funcionalidad de reactivación.

| | | |
|---|---|---|
| **Código** | USR-RF-020 | |
| **Nombre** | Reactivar usuario suspendido o inactivo | |
| **Descripción** | Permite cambiar el estado de un usuario de 'suspendido' o 'inactivo' a 'activo', restaurando su acceso al sistema. | |
| **Actores** | Administrador del sistema, ms-usuarios, ms-notificaciones, ms-auditoria | |
| | | |
| **Precondición** | Ejecutar [USR-RF-001] (Validación de sesión). | |
| | Ejecutar [USR-RF-002] (Validación de permisos con código: USR_REACTIVATE). | |
| | Ejecutar [USR-RF-003] (Generación de Request ID). | |
| | El usuario a reactivar existe en el sistema. | |
| | El usuario está en estado 'inactivo' o 'suspendido'. | |
| | Se proporciona un motivo obligatorio para la reactivación. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | El sistema recibe el ID del usuario a reactivar y el motivo de la reactivación. |
| | 2 | El sistema valida que el motivo no esté vacío. |
| | 3 | El sistema consulta la tabla usr_usuarios para obtener el estado actual del usuario. |
| | 4 | El sistema verifica que el usuario existe. |
| | 5 | El sistema verifica que el usuario esté en estado 'inactivo' o 'suspendido'. |
| | 6 | El sistema ejecuta [USR-RF-015] (Cambiar estado de usuario) para cambiar el estado a 'activo'. |
| | 7 | El sistema invoca a ms-notificaciones [NOT] para enviar una notificación de reactivación al usuario (de forma asíncrona). |
| | 8 | El sistema ejecuta [USR-RF-004] para registrar la reactivación en auditoría. |
| | 9 | El sistema ejecuta [USR-RF-005] para retornar la respuesta estándar con mensaje de confirmación y código HTTP 200. |
| | | |
| **Secuencia alterna** | 4A | Si el usuario no existe en la base de datos, el sistema rechaza la reactivación. |
| | 4B | El sistema ejecuta [USR-RF-004] para registrar el intento fallido. |
| | 4C | El sistema ejecuta [USR-RF-005] retornando success=false, message="Usuario no encontrado", código HTTP 404. |
| | | |
| | 5A | Si el usuario ya está en estado 'activo', el sistema rechaza la reactivación. |
| | 5B | El sistema ejecuta [USR-RF-004] para registrar el intento. |
| | 5C | El sistema ejecuta [USR-RF-005] retornando success=false, message="El usuario ya se encuentra activo", código HTTP 400. |
| | | |
| **Excepciones** | E1 | Si el motivo está vacío, el sistema rechaza con código 400 y message="Debe proporcionar un motivo para la reactivación". |
| | E2 | Si falla [USR-RF-015] al cambiar el estado, el sistema propaga el error. |
| | E3 | Si el envío de notificación falla, el sistema continúa normalmente (la notificación no es crítica). |
| | | |
| **Postcondición** | El usuario ha sido reactivado (estado='activo'). | |
| | Se ha registrado el cambio de estado en el historial con el motivo proporcionado. | |
| | Se ha enviado una notificación al usuario informando la reactivación. | |
| | El usuario puede volver a iniciar sesión en el sistema. | |
| | | |
| **Comentarios** | Esta funcionalidad es el proceso inverso a [USR-RF-011] (Desactivar usuario). Internamente utiliza [USR-RF-015] para realizar el cambio de estado, garantizando que se mantenga el historial de trazabilidad. El código de permiso sugerido es USR_REACTIVATE. | |

---

## USR-RF-021

**Justificación:** El documento menciona que ms-usuarios es consultado por múltiples servicios para "validar la existencia de usuarios". Aunque esta validación puede realizarse mediante [USR-RF-007], se sugiere un endpoint específico y ligero que solo retorne un booleano indicando si el usuario existe, optimizando las consultas desde otros microservicios.

| | | |
|---|---|---|
| **Código** | USR-RF-021 | |
| **Nombre** | Validar existencia de usuario (servicio interno) | |
| **Descripción** | Endpoint ligero que verifica si un usuario existe en el sistema sin retornar sus datos completos. Optimizado para consumo interno por otros microservicios. | |
| **Actores** | Microservicios del sistema, ms-usuarios, ms-auditoria | |
| | | |
| **Precondición** | Validar token de aplicación del microservicio solicitante. | |
| | Ejecutar [USR-RF-003] (Generación de Request ID). | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | El sistema recibe el ID del usuario cuya existencia se desea validar. |
| | 2 | El sistema valida que el ID sea un número entero positivo. |
| | 3 | El sistema ejecuta una consulta COUNT en la tabla usr_usuarios filtrando por id = ID recibido. |
| | 4 | El sistema verifica si el contador es mayor a 0. |
| | 5 | El sistema construye una respuesta simple con: existe (boolean), estado (string, solo si existe), username (string, solo si existe). |
| | 6 | El sistema ejecuta [USR-RF-004] para registrar la validación en auditoría. |
| | 7 | El sistema ejecuta [USR-RF-005] para retornar la respuesta estándar con los datos de validación y código HTTP 200. |
| | | |
| **Secuencia alterna** | 4A | Si el contador es 0 (el usuario no existe), el sistema retorna existe=false. |
| | 4B | El sistema ejecuta [USR-RF-004] para registrar la validación negativa. |
| | 4C | El sistema ejecuta [USR-RF-005] retornando success=true, data={existe: false}, código HTTP 200. |
| | | |
| **Excepciones** | E1 | Si el ID no es un número entero válido, el sistema rechaza con código 400 y message="Identificador de usuario inválido". |
| | E2 | Si la consulta a la base de datos falla, el sistema retorna código 500 (Error interno). |
| | | |
| **Postcondición** | Se ha retornado información de existencia del usuario. | |
| | La validación ha sido registrada en auditoría. | |
| | | |
| **Comentarios** | Este endpoint está optimizado para consultas de validación desde otros microservicios. Utiliza COUNT en lugar de SELECT completo para mejor rendimiento. Solo retorna información mínima necesaria: si existe, su estado (para verificar si está activo) y su username. No requiere validación de permisos ya que solo está disponible para comunicación entre servicios mediante tokens de aplicación. | |

---

## USR-RF-022

**Justificación:** El documento menciona que las contraseñas se almacenan de forma segura y se reciben cifradas, pero no especifica cómo un usuario puede cambiar su contraseña después del registro inicial. Esta es una funcionalidad estándar de seguridad en cualquier sistema de gestión de usuarios.

| | | |
|---|---|---|
| **Código** | USR-RF-022 | |
| **Nombre** | Actualizar contraseña de usuario | |
| **Descripción** | Permite a un usuario cambiar su contraseña proporcionando la contraseña actual y la nueva contraseña. | |
| **Actores** | Usuario del sistema, ms-usuarios, ms-notificaciones, ms-auditoria | |
| | | |
| **Precondición** | Ejecutar [USR-RF-001] (Validación de sesión). | |
| | El usuario debe estar cambiando su propia contraseña (no se permite cambiar la de otros usuarios). | |
| | Ejecutar [USR-RF-003] (Generación de Request ID). | |
| | Se proporciona la contraseña actual y la nueva contraseña (ambas cifradas). | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | El sistema recibe del usuario autenticado: password_actual_encrypted (contraseña actual cifrada con AES-256), password_nueva_encrypted (nueva contraseña cifrada con AES-256). |
| | 2 | El sistema obtiene el ID del usuario desde el token de sesión validado en [USR-RF-001]. |
| | 3 | El sistema consulta la tabla usr_usuarios para obtener el password_hash actual del usuario. |
| | 4 | El sistema descifra password_actual_encrypted utilizando AES-256. |
| | 5 | El sistema verifica el hash bcrypt de la contraseña actual descifrada contra el password_hash almacenado. |
| | 6 | El sistema confirma que la contraseña actual es correcta. |
| | 7 | El sistema descifra password_nueva_encrypted utilizando AES-256. |
| | 8 | El sistema valida que la nueva contraseña cumpla con las políticas de seguridad (mínimo 8 caracteres, al menos 1 mayúscula, 1 minúscula, 1 número). |
| | 9 | El sistema genera un hash bcrypt de la nueva contraseña con factor de costo 12. |
| | 10 | El sistema actualiza el campo password_hash en usr_usuarios con el nuevo hash. |
| | 11 | El sistema actualiza el campo updated_at con el timestamp actual. |
| | 12 | El sistema confirma la actualización. |
| | 13 | El sistema invoca a ms-notificaciones [NOT] para enviar una notificación de confirmación de cambio de contraseña (de forma asíncrona). |
| | 14 | El sistema ejecuta [USR-RF-004] para registrar el cambio de contraseña en auditoría (sin incluir las contraseñas). |
| | 15 | El sistema ejecuta [USR-RF-005] para retornar la respuesta estándar con mensaje de confirmación y código HTTP 200. |
| | | |
| **Secuencia alterna** | 6A | Si la contraseña actual no es correcta (el hash no coincide), el sistema rechaza el cambio. |
| | 6B | El sistema ejecuta [USR-RF-004] para registrar el intento fallido de cambio de contraseña. |
| | 6C | El sistema ejecuta [USR-RF-005] retornando success=false, message="Contraseña actual incorrecta", código HTTP 401. |
| | | |
| | 8A | Si la nueva contraseña no cumple con las políticas de seguridad, el sistema rechaza el cambio. |
| | 8B | El sistema ejecuta [USR-RF-004] para registrar el intento fallido. |
| | 8C | El sistema ejecuta [USR-RF-005] retornando success=false, message="La nueva contraseña no cumple con las políticas de seguridad: mínimo 8 caracteres, al menos 1 mayúscula, 1 minúscula, 1 número", código HTTP 400. |
| | | |
| **Excepciones** | E1 | Si el descifrado de alguna contraseña falla, el sistema rechaza con código 400 y message="Error al procesar las contraseñas". |
| | E2 | Si la generación del nuevo hash bcrypt falla, el sistema rechaza con código 500 (Error interno). |
| | E3 | Si la actualización en la base de datos falla, el sistema ejecuta rollback y rechaza con código 500. |
| | E4 | Si el envío de notificación falla, el sistema continúa normalmente (la notificación no es crítica). |
| | | |
| **Postcondición** | La contraseña del usuario ha sido actualizada exitosamente. | |
| | El nuevo password_hash está almacenado de forma segura en la base de datos. | |
| | Se ha enviado una notificación de confirmación al usuario. | |
| | El cambio ha sido registrado en auditoría. | |
| | | |
| **Comentarios** | Esta funcionalidad implementa un cambio de contraseña autenticado (el usuario debe conocer su contraseña actual). Para recuperación de contraseña olvidada se requeriría un flujo diferente con verificación por email (fuera del alcance actual). Las contraseñas nunca se almacenan ni se transmiten en texto plano. La notificación de cambio de contraseña es una medida de seguridad importante para alertar al usuario en caso de cambios no autorizados. No se requiere código de permiso específico ya que los usuarios siempre tienen derecho a cambiar su propia contraseña. | |

---

## USR-RF-023

**Justificación:** Aunque el documento menciona que los usuarios tienen roles asignados y que ms-usuarios debe consultar a ms-roles para validar existencia, no especifica una funcionalidad para listar usuarios filtrados por rol. Esta consulta es útil para administradores que necesitan gestionar usuarios con roles específicos (ej: listar todos los docentes).

| | | |
|---|---|---|
| **Código** | USR-RF-023 | |
| **Nombre** | Listar usuarios por rol | |
| **Descripción** | Permite obtener la lista de usuarios que tienen un rol específico asignado, con paginación. | |
| **Actores** | Usuario del sistema, ms-usuarios, ms-auditoria | |
| | | |
| **Precondición** | Ejecutar [USR-RF-001] (Validación de sesión). | |
| | Ejecutar [USR-RF-002] (Validación de permisos con código: USR_LIST_BY_ROLE). | |
| | Ejecutar [USR-RF-003] (Generación de Request ID). | |
| | Se conoce el ID del rol por el cual filtrar. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | El sistema recibe los parámetros: rol_id (obligatorio), estado (opcional: activo, inactivo, suspendido, o 'todos'), pagina (número de página, default=1), items_por_pagina (cantidad de resultados por página, default=10). |
| | 2 | El sistema valida que rol_id sea un número entero positivo. |
| | 3 | El sistema valida que items_por_pagina esté entre 1 y 100. |
| | 4 | El sistema valida que pagina sea mayor o igual a 1. |
| | 5 | El sistema construye una consulta filtrando por rol_id en usr_usuarios. |
| | 6 | Si se proporciona estado y es diferente de 'todos', el sistema añade filtro por estado. |
| | 7 | El sistema cuenta el total de registros que coinciden con los filtros. |
| | 8 | El sistema calcula el total de páginas. |
| | 9 | El sistema aplica paginación y ejecuta la consulta. |
| | 10 | El sistema obtiene los datos básicos de cada usuario (sin password_hash). |
| | 11 | El sistema construye la respuesta con: resultados, total_registros, total_paginas, pagina_actual, items_por_pagina. |
| | 12 | El sistema ejecuta [USR-RF-004] para registrar la consulta en auditoría. |
| | 13 | El sistema ejecuta [USR-RF-005] para retornar la respuesta estándar con los resultados paginados y código HTTP 200. |
| | | |
| **Secuencia alterna** | 7A | Si no existen usuarios con el rol especificado, el sistema retorna un array vacío. |
| | 7B | El sistema incluye en la respuesta: resultados=[], total_registros=0, total_paginas=0, pagina_actual, items_por_pagina. |
| | 7C | El sistema ejecuta [USR-RF-004] para registrar la consulta sin resultados. |
| | 7D | El sistema ejecuta [USR-RF-005] retornando success=true con la estructura vacía, código HTTP 200. |
| | | |
| **Excepciones** | E1 | Si rol_id no es un número entero positivo, el sistema rechaza con código 400 y message="ID de rol inválido". |
| | E2 | Si items_por_pagina está fuera del rango permitido, el sistema rechaza con código 400. |
| | E3 | Si la consulta a la base de datos falla, el sistema retorna código 500 (Error interno). |
| | | |
| **Postcondición** | Se ha retornado la lista paginada de usuarios con el rol especificado. | |
| | La consulta ha sido registrada en auditoría. | |
| | | |
| **Comentarios** | Esta funcionalidad es útil para administradores que necesitan gestionar grupos de usuarios por rol (ej: gestionar todos los docentes, estudiantes, etc.). El índice en rol_id garantiza consultas eficientes. El código de permiso sugerido es USR_LIST_BY_ROLE. | |

---

## USR-RF-024

**Justificación:** Para propósitos de monitoreo, reportes y toma de decisiones administrativas, es útil tener estadísticas agregadas sobre los usuarios del sistema (cuántos están activos, inactivos, suspendidos). Esta información puede ser consumida por un dashboard administrativo o por ms-reportes.

| | | |
|---|---|---|
| **Código** | USR-RF-024 | |
| **Nombre** | Obtener estadísticas de usuarios por estado | |
| **Descripción** | Retorna estadísticas agregadas sobre la cantidad de usuarios en cada estado del sistema. | |
| **Actores** | Administrador del sistema, ms-reportes, ms-usuarios, ms-auditoria | |
| | | |
| **Precondición** | Si la petición proviene de un usuario: Ejecutar [USR-RF-001] y [USR-RF-002] con código USR_STATS_READ. | |
| | Si la petición proviene de ms-reportes: Validar token de aplicación. | |
| | Ejecutar [USR-RF-003] (Generación de Request ID). | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | El sistema recibe la petición de estadísticas de usuarios. |
| | 2 | El sistema ejecuta una consulta agregada (GROUP BY estado, COUNT) en la tabla usr_usuarios. |
| | 3 | El sistema cuenta la cantidad de usuarios en cada estado: activo, inactivo, suspendido. |
| | 4 | El sistema calcula el total de usuarios sumando todos los estados. |
| | 5 | El sistema calcula el porcentaje que representa cada estado sobre el total. |
| | 6 | El sistema construye un objeto con las estadísticas: total_usuarios, usuarios_activos (count y porcentaje), usuarios_inactivos (count y porcentaje), usuarios_suspendidos (count y porcentaje), fecha_calculo (timestamp de la consulta). |
| | 7 | El sistema ejecuta [USR-RF-004] para registrar la consulta en auditoría. |
| | 8 | El sistema ejecuta [USR-RF-005] para retornar la respuesta estándar con las estadísticas y código HTTP 200. |
| | | |
| **Secuencia alterna** | 2A | Si no existen usuarios en el sistema, el sistema retorna estadísticas en cero. |
| | 2B | El sistema construye la respuesta con: total_usuarios=0, usuarios_activos={count:0, porcentaje:0}, usuarios_inactivos={count:0, porcentaje:0}, usuarios_suspendidos={count:0, porcentaje:0}. |
| | 2C | El sistema ejecuta [USR-RF-004] para registrar la consulta. |
| | 2D | El sistema ejecuta [USR-RF-005] retornando success=true con las estadísticas en cero, código HTTP 200. |
| | | |
| **Excepciones** | E1 | Si la consulta a la base de datos falla, el sistema retorna código 500 (Error interno). |
| | | |
| **Postcondición** | Se han retornado las estadísticas agregadas de usuarios por estado. | |
| | La consulta ha sido registrada en auditoría. | |
| | | |
| **Comentarios** | Esta funcionalidad es útil para dashboards administrativos y reportes del sistema. La consulta es ligera ya que solo realiza agregaciones sin retornar datos individuales. Los porcentajes se calculan con precisión de 2 decimales. Puede ser consumida por ms-reportes para generar reportes periódicos automáticos. El código de permiso sugerido es USR_STATS_READ. | |

---

**Fin del documento de requisitos funcionales detallados**
