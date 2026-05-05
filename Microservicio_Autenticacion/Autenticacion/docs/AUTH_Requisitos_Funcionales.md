# Requisitos Funcionales — MS-AUTENTICACION [AUTH]

> **Microservicio:** ms-autenticacion
> **Código:** AUTH
> **Módulo:** Módulo 1 — Seguridad y Acceso
> **Stack:** FastAPI + Python + PostgreSQL
> **Documento fuente:** Propuesta de Arquitectura y Requisitos Funcionales — ERP Universitario v1.0
> **Fecha de generación:** Febrero 2026

---

## Tabla de Contenido

### Categoría 1 — Requisitos Transversales

| ID | Nombre |
|---|---|
| AUTH-RT-001 | Generación y propagación de Request ID |
| AUTH-RT-002 | Auditoría asíncrona de operaciones |
| AUTH-RT-003 | Estructura de respuesta estándar |
| AUTH-RT-004 | Validación de sesión activa en endpoints propios |
| AUTH-RT-005 | Cifrado y protección de credenciales |

### Categoría 2 — Requisitos Funcionales por Entidad

#### Entidad: Sesión de Usuario

| ID | Nombre |
|---|---|
| AUTH-RF-001 | Inicio de sesión con credenciales cifradas |
| AUTH-RF-002 | Cierre de sesión por el usuario |
| AUTH-RF-003 | Validación de sesión para servicios externos |
| AUTH-RF-004 | Listado de sesiones activas (administrador) |
| AUTH-RF-005 | Cierre forzado de sesión (administrador) |

#### Entidad: Bloqueo de Cuenta

| ID | Nombre |
|---|---|
| AUTH-RF-006 | Bloqueo de cuenta por intentos fallidos |

#### Entidad: Token de Aplicación

| ID | Nombre |
|---|---|
| AUTH-RF-007 | Creación de token de aplicación |
| AUTH-RF-008 | Consulta de token de aplicación |
| AUTH-RF-009 | Actualización de token de aplicación |
| AUTH-RF-010 | Desactivación de token de aplicación |

#### Entidad: Historial de Accesos

| ID | Nombre |
|---|---|
| AUTH-RF-011 | Consulta de historial de accesos |

### Categoría 3 — Requisitos Sugeridos

| ID | Nombre |
|---|---|
| AUTH-RS-001 | Desbloqueo manual de cuenta bloqueada |
| AUTH-RS-002 | Listado de tokens de aplicación |
| AUTH-RS-003 | Consulta de sesiones cerradas por usuario |
| AUTH-RS-004 | Health check del servicio de autenticación |

---
---

## Categoría 1 — Requisitos Transversales

> Los siguientes requisitos aplican de forma transversal a **todas** las operaciones del microservicio. Los demás requisitos los referencian en su secuencia normal en lugar de repetir sus pasos completos.

---

| | | |
|---|---|---|
| **Código** | AUTH-RT-001 | |
| **Nombre** | Generación y propagación de Request ID | |
| **Descripción** | Toda petición que ingrese a ms-autenticacion debe recibir un identificador único de rastreo. Si la petición ya trae un Request ID externo, debe reutilizarse. Si no, se genera uno nuevo con el formato `AUTH-<timestamp_unix>-<id_corto>`. El Request ID debe incluirse en cabeceras y cuerpo de toda respuesta. | |
| **Actores** | ms-autenticacion, cualquier cliente o microservicio invocante | |
| | | |
| **Precondición** | La petición ha llegado al servicio ms-autenticacion | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Inspeccionar las cabeceras HTTP de la petición entrante en busca de un Request ID existente. |
| | 2 | Si no existe Request ID, generar uno nuevo con el formato `AUTH-<timestamp_unix>-<id_corto_aleatorio>` (ej: `AUTH-1740000000-a3f8b2`). |
| | 3 | Almacenar el Request ID en el contexto de ejecución de la petición para su uso durante todo el procesamiento. |
| | 4 | Incluir el Request ID en las cabeceras de la respuesta (ej: `X-Request-ID`). |
| | 5 | Incluir el Request ID en el cuerpo de la respuesta según AUTH-RT-003. |
| | | |
| **Secuencia alterna** | 2A | Si la petición ya trae un Request ID (proviene de otro microservicio), reutilizarlo sin generar uno nuevo. Continuar en el paso 3. |
| | | |
| **Excepciones** | E1 | Si falla la generación del identificador aleatorio, reintentar una vez. Si el segundo intento falla, asignar un UUID estándar como fallback. |
| | | |
| **Postcondición** | El Request ID queda asociado a toda la traza de la petición | |
| | El Request ID se retorna al cliente en cabeceras y cuerpo de la respuesta | |
| | | |
| **Comentarios** | Este requisito se ejecuta como primer paso en todos los demás requisitos del microservicio. | |

---

| | | |
|---|---|---|
| **Código** | AUTH-RT-002 | |
| **Nombre** | Auditoría asíncrona de operaciones | |
| **Descripción** | Al finalizar cada operación, ms-autenticacion debe generar un registro de log en formato JSON y enviarlo de forma asíncrona a ms-auditoria. El envío no debe bloquear ni demorar la respuesta al cliente. Si el envío falla, el servicio debe continuar operando normalmente (patrón fire-and-forget). | |
| **Actores** | ms-autenticacion, ms-auditoria [AUD] | |
| | | |
| **Precondición** | La operación ha finalizado (exitosa o con error controlado) | |
| | El Request ID está disponible en el contexto (AUTH-RT-001) | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Construir el objeto JSON de auditoría con los campos: fecha y hora de la operación, Request ID, nombre del microservicio (`ms-autenticacion`), funcionalidad ejecutada, método HTTP, código de respuesta HTTP, duración en milisegundos, identificador del usuario que realizó la operación y detalle descriptivo. |
| | 2 | Invocar de forma asíncrona (no bloqueante) el endpoint de recepción de logs de **ms-auditoria [AUD]**, enviando el objeto JSON construido. |
| | 3 | Retornar la respuesta al cliente sin esperar confirmación del servicio de auditoría. |
| | | |
| **Secuencia alterna** | — | No aplica. El envío es siempre fire-and-forget. |
| | | |
| **Excepciones** | E1 | Si ms-auditoria no responde o retorna error, registrar la falla en el log interno del servicio y continuar sin relanzar el error al cliente. |
| | E2 | Para operaciones de inicio de sesión fallido, el campo "identificador de usuario" del log puede corresponder al nombre de usuario proporcionado (aún no autenticado). |
| | | |
| **Postcondición** | El registro de auditoría fue enviado a ms-auditoria o, en caso de fallo, registrado en el log interno | |
| | La respuesta al cliente no se vio afectada por el resultado del envío de auditoría | |
| | | |
| **Comentarios** | Ninguna credencial (contraseña, token) debe aparecer en texto plano en el registro JSON enviado a auditoría (regla AUTH-RT-005). | |

---

| | | |
|---|---|---|
| **Código** | AUTH-RT-003 | |
| **Nombre** | Estructura de respuesta estándar | |
| **Descripción** | Toda respuesta emitida por ms-autenticacion, sea exitosa o de error, debe seguir una estructura JSON uniforme que incluya: Request ID, indicador de éxito/error, datos del resultado, mensaje descriptivo y fecha/hora de la respuesta. | |
| **Actores** | ms-autenticacion, cualquier cliente o microservicio invocante | |
| | | |
| **Precondición** | El procesamiento de la operación ha concluido | |
| | El Request ID está disponible en el contexto (AUTH-RT-001) | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Construir el objeto de respuesta con la siguiente estructura: `{ "request_id": "<valor>", "success": true/false, "data": <objeto_resultado>, "message": "<mensaje_descriptivo>", "timestamp": "<fecha_hora_ISO>" }`. |
| | 2 | Serializar el objeto como JSON y retornarlo con el código HTTP correspondiente a la operación. |
| | | |
| **Secuencia alterna** | 1A | En caso de error técnico inesperado, el campo `data` puede ser `null` y el campo `message` debe describir el error de forma genérica sin exponer detalles internos del sistema. |
| | | |
| **Excepciones** | E1 | Si la serialización del objeto de respuesta falla, retornar HTTP 500 con un mensaje de error mínimo que incluya al menos el Request ID. |
| | | |
| **Postcondición** | El cliente recibe una respuesta con estructura uniforme, independientemente del resultado de la operación | |
| | | |
| **Comentarios** | Esta estructura aplica a todas las respuestas, incluidas las del endpoint de validación de sesión (AUTH-RF-003), consumido por múltiples microservicios. | |

---

| | | |
|---|---|---|
| **Código** | AUTH-RT-004 | |
| **Nombre** | Validación de sesión activa en endpoints propios | |
| **Descripción** | Todos los endpoints de ms-autenticacion, a excepción del de inicio de sesión y del health check, deben verificar que la petición entrante provenga de un usuario con sesión activa antes de ejecutar cualquier lógica de negocio. | |
| **Actores** | ms-autenticacion, usuario autenticado o microservicio invocante | |
| | | |
| **Precondición** | La petición ha llegado a cualquier endpoint de ms-autenticacion distinto al de inicio de sesión | |
| | La petición incluye un token de sesión en las cabeceras | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Extraer el token de sesión de las cabeceras de la petición (ej: `Authorization: Bearer <token>`). |
| | 2 | Consultar en la base de datos interna si existe un registro de sesión para ese token con estado `activa`. |
| | 3 | Si la sesión es válida y activa, permitir la continuación del procesamiento hacia la lógica de negocio del endpoint invocado. |
| | | |
| **Secuencia alterna** | 3A | Si la petición proviene de ms-roles [ROL] en el contexto de confianza mutua, la validación puede resolverse mediante el reconocimiento del token de aplicación de ms-roles, sin consultar sesión de usuario. |
| | | |
| **Excepciones** | E1 | Si el token no está presente en las cabeceras, rechazar la petición con HTTP 401 y mensaje "Token de sesión no proporcionado". |
| | E2 | Si la sesión no existe en base de datos o su estado es `cerrada`, rechazar la petición con HTTP 401 y mensaje "Sesión inválida o expirada". |
| | E3 | Si ocurre un error al consultar la base de datos, rechazar la petición con HTTP 500. |
| | | |
| **Postcondición** | Solo peticiones con sesión activa válida alcanzan la lógica de negocio del endpoint | |
| | | |
| **Comentarios** | El endpoint de inicio de sesión (AUTH-RF-001) está explícitamente excluido, ya que es el mecanismo de creación de sesión. El endpoint de health check (AUTH-RS-004) también se excluye por su naturaleza operativa. | |

---

| | | |
|---|---|---|
| **Código** | AUTH-RT-005 | |
| **Nombre** | Cifrado y protección de credenciales | |
| **Descripción** | Las contraseñas de usuarios y los tokens de aplicación nunca se almacenan ni transmiten en texto plano. Las contraseñas se almacenan como hash bcrypt (costo mínimo 12) y se reciben cifradas con AES-256 + Base64. Los tokens de aplicación se almacenan y transmiten cifrados con AES-256. Ninguna credencial puede aparecer en logs, respuestas ni configuraciones. | |
| **Actores** | ms-autenticacion | |
| | | |
| **Precondición** | El sistema va a almacenar, recibir o transmitir una credencial (contraseña o token de aplicación) | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | **Para contraseñas recibidas desde el cliente:** descifrar el valor AES-256 + Base64 recibido para obtener la contraseña en texto plano, exclusivamente en memoria. |
| | 2 | Utilizar la contraseña en texto plano únicamente para la comparación con el hash bcrypt almacenado. Descartar inmediatamente tras el uso. |
| | 3 | **Para almacenamiento de contraseña nueva:** aplicar hash bcrypt con factor de costo mínimo 12 antes de persistir en base de datos. |
| | 4 | **Para tokens de aplicación:** almacenar siempre el valor cifrado con AES-256 en base de datos; transmitir siempre cifrado entre servicios. |
| | 5 | Verificar antes de generar logs, respuestas o registros de configuración que ningún campo contenga credenciales en texto plano. |
| | | |
| **Secuencia alterna** | — | No aplica. El cifrado es obligatorio sin excepciones. |
| | | |
| **Excepciones** | E1 | Si el descifrado AES-256 falla (datos corruptos o clave incorrecta), rechazar la operación con HTTP 400 y mensaje "Formato de credenciales inválido". |
| | E2 | Si el proceso de hashing bcrypt falla, rechazar la operación con HTTP 500 sin exponer detalles internos. |
| | | |
| **Postcondición** | Ninguna credencial persiste o se transmite en texto plano en ningún componente del sistema | |
| | | |
| **Comentarios** | Este requisito aplica tanto a operaciones de autenticación de usuarios como a la gestión de tokens de aplicación (AUTH-RF-007, AUTH-RF-009). | |

---
---

## Categoría 2 — Requisitos Funcionales por Entidad

---

### Entidad: Sesión de Usuario

---

| | | |
|---|---|---|
| **Código** | AUTH-RF-001 | |
| **Nombre** | Inicio de sesión con credenciales cifradas | |
| **Descripción** | Permite a un usuario autenticarse en el sistema proporcionando sus credenciales cifradas. Si la autenticación es exitosa, genera un token JWT con el identificador del usuario, su rol y permisos, y crea un registro de sesión activa. | |
| **Actores** | Usuario final, ms-autenticacion, ms-usuarios [USR], ms-roles [ROL], ms-auditoria [AUD] | |
| | | |
| **Precondición** | El usuario envía credenciales (nombre de usuario y contraseña) cifradas con AES-256 + Base64 | |
| | El usuario no tiene su cuenta en estado `bloqueada` | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar **AUTH-RT-001** (Generación de Request ID). |
| | 2 | Descifrar la contraseña recibida según **AUTH-RT-005** (Cifrado y protección de credenciales). |
| | 3 | Consultar a **ms-usuarios [USR]** — operación: obtener datos del usuario por nombre de usuario. Respuesta esperada: identificador del usuario, estado de la cuenta (activo/bloqueado), hash de contraseña almacenado y contador de intentos fallidos. |
| | 4 | Verificar que el estado de la cuenta sea `activo`. Si está bloqueada, ejecutar secuencia alterna 4A. |
| | 5 | Comparar la contraseña descifrada en memoria contra el hash bcrypt almacenado (factor de costo mínimo 12). |
| | 6 | Si las credenciales son correctas, consultar a **ms-roles [ROL]** — operación: obtener rol y lista de permisos del usuario por identificador de usuario. Respuesta esperada: nombre del rol y arreglo de permisos asociados. |
| | 7 | Generar un token JWT firmado que contenga: identificador del usuario, rol y permisos obtenidos de ms-roles [ROL]. |
| | 8 | Crear un registro de sesión activa en base de datos con: identificador del usuario, token JWT generado, dirección IP del cliente, información del navegador/cliente (User-Agent), fecha y hora de creación, fecha y hora de última actividad (igual a la de creación) y estado `activa`. |
| | 9 | Registrar el evento en el historial de accesos: tipo de evento `inicio de sesión`, usuario, IP, cliente, fecha/hora y Request ID. |
| | 10 | Notificar a **ms-usuarios [USR]** para reiniciar el contador de intentos fallidos del usuario. |
| | 11 | Construir la respuesta con el token JWT según **AUTH-RT-003**. |
| | 12 | Ejecutar **AUTH-RT-002** (Auditoría asíncrona). |
| | | |
| **Secuencia alterna** | 3A | Si ms-usuarios [USR] no encuentra al usuario: retornar HTTP 401 con mensaje "Credenciales inválidas" (sin especificar si el usuario existe). Ejecutar AUTH-RT-002. Fin del flujo. |
| | 4A | Si la cuenta del usuario está bloqueada: registrar el intento en el historial de accesos con tipo `intento fallido`. Retornar HTTP 403 con mensaje "Cuenta bloqueada. Contacte al administrador." Ejecutar AUTH-RT-002. Fin del flujo. |
| | 5A | Si la contraseña no coincide: incrementar el contador de intentos fallidos en ms-usuarios [USR]. Si el contador alcanza 5, ejecutar **AUTH-RF-006** (Bloqueo de cuenta). Registrar el evento en el historial de accesos con tipo `intento fallido`. Retornar HTTP 401 con mensaje "Credenciales inválidas". Ejecutar AUTH-RT-002. Fin del flujo. |
| | | |
| **Excepciones** | E1 | Si ms-usuarios [USR] no responde o retorna error técnico, retornar HTTP 503 con mensaje "Servicio temporalmente no disponible". Ejecutar AUTH-RT-002. |
| | E2 | Si ms-roles [ROL] no responde o retorna error técnico, retornar HTTP 503. El token JWT no debe generarse sin los permisos del usuario. Ejecutar AUTH-RT-002. |
| | E3 | Si falla la creación del registro de sesión en base de datos, retornar HTTP 500. El token no debe entregarse al cliente si la sesión no pudo persistirse. |
| | | |
| **Postcondición** | Se ha generado un token JWT válido con identidad, rol y permisos del usuario | |
| | Existe un registro de sesión activa en base de datos asociado al token | |
| | El evento de inicio de sesión quedó registrado en el historial de accesos | |
| | El contador de intentos fallidos del usuario fue reiniciado a 0 | |
| | | |
| **Comentarios** | Este es el único endpoint de ms-autenticacion excluido de AUTH-RT-004, ya que es el mecanismo de creación de sesión. Las sesiones no tienen expiración por tiempo (regla de negocio 11 del documento fuente). | |

---

| | | |
|---|---|---|
| **Código** | AUTH-RF-002 | |
| **Nombre** | Cierre de sesión por el usuario | |
| **Descripción** | Permite a un usuario autenticado cerrar su sesión activa. El token JWT queda invalidado y el registro de sesión es marcado como cerrado en base de datos. | |
| **Actores** | Usuario autenticado, ms-autenticacion, ms-auditoria [AUD] | |
| | | |
| **Precondición** | El usuario tiene una sesión activa en el sistema | |
| | La petición incluye el token JWT válido en las cabeceras | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar **AUTH-RT-001** (Generación de Request ID). |
| | 2 | Ejecutar **AUTH-RT-004** (Validación de sesión activa en endpoints propios). |
| | 3 | Localizar el registro de sesión en base de datos correspondiente al token recibido. |
| | 4 | Actualizar el registro de sesión: cambiar el estado a `cerrada` y registrar la fecha y hora de modificación. |
| | 5 | Registrar el evento en el historial de accesos: tipo de evento `cierre de sesión`, usuario, IP, cliente, fecha/hora y Request ID. |
| | 6 | Construir la respuesta de éxito según **AUTH-RT-003** con mensaje "Sesión cerrada correctamente". |
| | 7 | Ejecutar **AUTH-RT-002** (Auditoría asíncrona). |
| | | |
| **Secuencia alterna** | — | No aplica para este flujo. |
| | | |
| **Excepciones** | E1 | Si no se encuentra el registro de sesión para el token proporcionado, retornar HTTP 404 con mensaje "Sesión no encontrada". |
| | E2 | Si falla la actualización del estado de la sesión en base de datos, retornar HTTP 500. |
| | | |
| **Postcondición** | El registro de sesión tiene estado `cerrada` en base de datos | |
| | El token JWT ya no puede ser utilizado para operaciones posteriores | |
| | El evento de cierre de sesión quedó registrado en el historial de accesos | |
| | | |
| **Comentarios** | Las sesiones no expiran por tiempo; el cierre explícito por el usuario y el cierre forzado por administrador (AUTH-RF-005) son los únicos mecanismos de invalidación. | |

---

| | | |
|---|---|---|
| **Código** | AUTH-RF-003 | |
| **Nombre** | Validación de sesión para servicios externos | |
| **Descripción** | Expone un endpoint que, dado un token JWT, verifica que la sesión existe en base de datos y que se encuentra activa. Es el servicio más crítico del sistema: todos los demás microservicios lo consumen antes de ejecutar cualquier operación. | |
| **Actores** | Cualquier microservicio del sistema (consumidor), ms-autenticacion | |
| | | |
| **Precondición** | El microservicio invocante envía un token JWT en la petición | |
| | El microservicio invocante posee un token de aplicación activo para identificarse ante ms-autenticacion | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar **AUTH-RT-001** (Generación/propagación de Request ID — reutilizar el Request ID entrante si ya existe). |
| | 2 | Verificar que el token de aplicación del microservicio invocante sea válido y esté activo (comparar contra los registros de tokens de aplicación en base de datos). |
| | 3 | Extraer el token JWT del cuerpo o cabecera de la petición. |
| | 4 | Consultar en base de datos si existe un registro de sesión para ese token con estado `activa`. |
| | 5 | Construir la respuesta de éxito según **AUTH-RT-003** indicando `"success": true` y los datos básicos de la sesión (identificador de usuario, estado). |
| | 6 | Ejecutar **AUTH-RT-002** (Auditoría asíncrona). |
| | | |
| **Secuencia alterna** | 4A | Si la sesión no existe o su estado es `cerrada`: construir respuesta con `"success": false` y mensaje "Sesión inválida o inexistente". Retornar HTTP 401. Ejecutar AUTH-RT-002. |
| | | |
| **Excepciones** | E1 | Si el token de aplicación del invocante es inválido o está inactivo, rechazar la petición con HTTP 403 y mensaje "Token de aplicación no autorizado". |
| | E2 | Si ocurre un error al consultar la base de datos, retornar HTTP 500. |
| | | |
| **Postcondición** | El microservicio invocante recibe una respuesta clara sobre la validez de la sesión | |
| | La respuesta incluye el Request ID para trazabilidad distribuida | |
| | | |
| **Comentarios** | Este endpoint está excluido de AUTH-RT-004 (la autenticación del invocante se realiza mediante token de aplicación, no sesión de usuario). Es el endpoint con mayor volumen de llamadas de todo el sistema; se recomienda evaluar estrategias de alta disponibilidad y caché. | |

---

| | | |
|---|---|---|
| **Código** | AUTH-RF-004 | |
| **Nombre** | Listado de sesiones activas (administrador) | |
| **Descripción** | Permite a un administrador consultar todas las sesiones activas del sistema, con la posibilidad de filtrar los resultados por usuario específico. | |
| **Actores** | Administrador, ms-autenticacion, ms-auditoria [AUD] | |
| | | |
| **Precondición** | El administrador tiene una sesión activa en el sistema | |
| | El administrador posee permisos para administrar sesiones | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar **AUTH-RT-001** (Generación de Request ID). |
| | 2 | Ejecutar **AUTH-RT-004** (Validación de sesión activa en endpoints propios). |
| | 3 | Verificar que el usuario autenticado posee permisos de administración de sesiones ([Por definir] — validación embebida en JWT o consulta a ms-roles [ROL]). |
| | 4 | Recibir los parámetros de filtrado opcionales: identificador o nombre de usuario. |
| | 5 | Consultar en base de datos los registros de sesión con estado `activa`, aplicando el filtro por usuario si fue proporcionado. |
| | 6 | Construir la respuesta con la lista de sesiones según **AUTH-RT-003**. Cada sesión incluye: identificador de sesión, usuario, IP, información del cliente, fecha de creación y fecha de última actividad. El valor del token no se incluye en la respuesta. |
| | 7 | Ejecutar **AUTH-RT-002** (Auditoría asíncrona). |
| | | |
| **Secuencia alterna** | 5A | Si no existen sesiones activas que coincidan con el filtro, retornar lista vacía con HTTP 200. |
| | | |
| **Excepciones** | E1 | Si el usuario autenticado no posee permisos de administración, retornar HTTP 403 con mensaje "Permisos insuficientes". |
| | E2 | Si ocurre un error al consultar la base de datos, retornar HTTP 500. |
| | | |
| **Postcondición** | El administrador recibe la lista de sesiones activas, filtrada o completa | |
| | | |
| **Comentarios** | El valor del token JWT nunca debe exponerse en respuestas de consulta. Solo deben retornarse metadatos de la sesión. | |

---

| | | |
|---|---|---|
| **Código** | AUTH-RF-005 | |
| **Nombre** | Cierre forzado de sesión (administrador) | |
| **Descripción** | Permite a un administrador forzar el cierre de una sesión activa específica, independientemente de la voluntad del usuario propietario de esa sesión. | |
| **Actores** | Administrador, ms-autenticacion, ms-auditoria [AUD] | |
| | | |
| **Precondición** | El administrador tiene una sesión activa en el sistema | |
| | El administrador posee permisos para forzar el cierre de sesiones | |
| | La sesión objetivo existe y tiene estado `activa` | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar **AUTH-RT-001** (Generación de Request ID). |
| | 2 | Ejecutar **AUTH-RT-004** (Validación de sesión activa en endpoints propios). |
| | 3 | Verificar que el usuario autenticado posee permisos de administración de sesiones. |
| | 4 | Recibir el identificador de la sesión a cerrar. |
| | 5 | Localizar el registro de sesión en base de datos y verificar que su estado sea `activa`. |
| | 6 | Actualizar el registro de sesión: cambiar estado a `cerrada` y registrar la fecha y hora de modificación. |
| | 7 | Registrar el evento en el historial de accesos: tipo de evento `cierre de sesión` (forzado por administrador), usuario afectado, IP, fecha/hora y Request ID. |
| | 8 | Construir la respuesta de éxito según **AUTH-RT-003** con mensaje "Sesión cerrada forzosamente". |
| | 9 | Ejecutar **AUTH-RT-002** (Auditoría asíncrona). |
| | | |
| **Secuencia alterna** | 5A | Si la sesión ya tiene estado `cerrada`, retornar HTTP 409 con mensaje "La sesión ya se encuentra cerrada". |
| | | |
| **Excepciones** | E1 | Si no se encuentra el registro de sesión con el identificador proporcionado, retornar HTTP 404. |
| | E2 | Si el administrador no posee permisos suficientes, retornar HTTP 403. |
| | E3 | Si falla la actualización en base de datos, retornar HTTP 500. |
| | | |
| **Postcondición** | El registro de sesión objetivo tiene estado `cerrada` en base de datos | |
| | El usuario afectado ya no puede operar con ese token | |
| | El evento de cierre forzado quedó registrado en el historial de accesos | |
| | | |
| **Comentarios** | Se recomienda evaluar si debe notificarse al usuario afectado a través de ms-notificaciones [NOT] cuando su sesión es cerrada forzosamente [Por definir]. | |

---

### Entidad: Bloqueo de Cuenta

---

| | | |
|---|---|---|
| **Código** | AUTH-RF-006 | |
| **Nombre** | Bloqueo de cuenta por intentos fallidos | |
| **Descripción** | Cuando un usuario acumula 5 intentos consecutivos fallidos de inicio de sesión, su cuenta es bloqueada automáticamente, impidiendo nuevos intentos de acceso hasta que un administrador la desbloquee manualmente. | |
| **Actores** | ms-autenticacion, ms-usuarios [USR], ms-auditoria [AUD] | |
| | | |
| **Precondición** | El contador de intentos fallidos del usuario ha alcanzado el valor 5 (verificado durante AUTH-RF-001) | |
| | La cuenta del usuario no está previamente bloqueada | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | (Este requisito es invocado desde AUTH-RF-001, secuencia alterna 5A.) Confirmar que el contador de intentos fallidos ha alcanzado exactamente 5. |
| | 2 | Enviar instrucción a **ms-usuarios [USR]** — operación: bloquear cuenta del usuario por identificador de usuario. Respuesta esperada: confirmación de que el estado de la cuenta fue actualizado a `bloqueada`. |
| | 3 | Registrar el evento en el historial de accesos: tipo de evento `bloqueo de cuenta`, usuario, IP, cliente, fecha/hora y Request ID. |
| | 4 | Retornar al flujo invocante (AUTH-RF-001) para que construya la respuesta HTTP 401 correspondiente. |
| | | |
| **Secuencia alterna** | 2A | Si ms-usuarios [USR] no puede aplicar el bloqueo, registrar la inconsistencia en el log interno y continuar. |
| | | |
| **Excepciones** | E1 | Si ms-usuarios [USR] no responde, registrar el intento de bloqueo fallido en log interno y notificar al administrador [Por definir el mecanismo de notificación]. |
| | | |
| **Postcondición** | La cuenta del usuario tiene estado `bloqueada` en ms-usuarios [USR] | |
| | El evento de bloqueo quedó registrado en el historial de accesos | |
| | El usuario no podrá iniciar sesión hasta que su cuenta sea desbloqueada manualmente (ver AUTH-RS-001) | |
| | | |
| **Comentarios** | El contador de intentos fallidos se reinicia únicamente al iniciar sesión exitosamente (AUTH-RF-001, paso 10). El umbral de 5 intentos es fijo según el documento fuente. | |

---

### Entidad: Token de Aplicación

---

| | | |
|---|---|---|
| **Código** | AUTH-RF-007 | |
| **Nombre** | Creación de token de aplicación | |
| **Descripción** | Permite a un administrador registrar un nuevo token de aplicación para un microservicio. El token se genera y almacena cifrado con AES-256, queda en estado activo y no tiene fecha de expiración. | |
| **Actores** | Administrador, ms-autenticacion, ms-auditoria [AUD] | |
| | | |
| **Precondición** | El administrador tiene una sesión activa en el sistema | |
| | El administrador posee permisos para gestionar tokens de aplicación | |
| | No existe un token activo para el mismo nombre de servicio ([Por definir] si se permiten múltiples tokens por servicio) | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar **AUTH-RT-001** (Generación de Request ID). |
| | 2 | Ejecutar **AUTH-RT-004** (Validación de sesión activa en endpoints propios). |
| | 3 | Recibir los datos del nuevo token: nombre del servicio y descripción del servicio. |
| | 4 | Generar el valor del token (cadena aleatoria de alta entropía — [Por definir el algoritmo de generación]). |
| | 5 | Cifrar el valor del token con AES-256 según **AUTH-RT-005**. |
| | 6 | Persistir el registro en base de datos con: nombre del servicio, valor del token cifrado, descripción, estado `activo`, fecha de creación, identificador del administrador como responsable de la última actualización, y fecha de creación como fecha de última actualización. |
| | 7 | Construir la respuesta según **AUTH-RT-003**, incluyendo el valor del token en texto plano **únicamente en esta respuesta**, ya que es la única oportunidad de entregarlo al administrador. |
| | 8 | Ejecutar **AUTH-RT-002** (Auditoría asíncrona). |
| | | |
| **Secuencia alterna** | 3A | Si ya existe un token activo para el mismo nombre de servicio, retornar HTTP 409 con mensaje "Ya existe un token activo para este servicio". |
| | | |
| **Excepciones** | E1 | Si el administrador no posee permisos suficientes, retornar HTTP 403. |
| | E2 | Si falla la persistencia en base de datos, retornar HTTP 500. |
| | | |
| **Postcondición** | El token queda registrado en base de datos en estado `activo` y cifrado | |
| | El administrador recibió el valor del token en texto plano para su distribución al microservicio correspondiente | |
| | | |
| **Comentarios** | El valor del token en texto plano solo se retorna en la creación y actualización. Las consultas posteriores (AUTH-RF-008) nunca exponen el valor. Los tokens no tienen fecha de expiración; solo se desactivan o actualizan manualmente. | |

---

| | | |
|---|---|---|
| **Código** | AUTH-RF-008 | |
| **Nombre** | Consulta de token de aplicación | |
| **Descripción** | Permite a un administrador consultar los metadatos de un token de aplicación registrado por nombre de servicio o identificador, sin exponer el valor del token en ningún formato. | |
| **Actores** | Administrador, ms-autenticacion, ms-auditoria [AUD] | |
| | | |
| **Precondición** | El administrador tiene una sesión activa en el sistema | |
| | El administrador posee permisos para consultar tokens de aplicación | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar **AUTH-RT-001** (Generación de Request ID). |
| | 2 | Ejecutar **AUTH-RT-004** (Validación de sesión activa en endpoints propios). |
| | 3 | Recibir el identificador o nombre del servicio a consultar. |
| | 4 | Consultar en base de datos el registro del token de aplicación correspondiente. |
| | 5 | Construir la respuesta según **AUTH-RT-003** con los metadatos del token: nombre del servicio, descripción, estado, fecha de creación, responsable de última actualización y fecha de última actualización. El campo del valor del token **no** debe incluirse en la respuesta. |
| | 6 | Ejecutar **AUTH-RT-002** (Auditoría asíncrona). |
| | | |
| **Secuencia alterna** | — | No aplica. |
| | | |
| **Excepciones** | E1 | Si no se encuentra el token para el identificador o nombre de servicio proporcionado, retornar HTTP 404. |
| | E2 | Si el administrador no posee permisos suficientes, retornar HTTP 403. |
| | | |
| **Postcondición** | El administrador recibe los metadatos del token sin que el valor cifrado sea expuesto | |
| | | |
| **Comentarios** | El listado de todos los tokens se contempla en AUTH-RS-002 (requisito sugerido). | |

---

| | | |
|---|---|---|
| **Código** | AUTH-RF-009 | |
| **Nombre** | Actualización de token de aplicación | |
| **Descripción** | Permite a un administrador actualizar el valor de un token de aplicación existente. Se genera un nuevo valor de token, se cifra y reemplaza al anterior. Solo puede realizarse de forma manual. | |
| **Actores** | Administrador, ms-autenticacion, ms-auditoria [AUD] | |
| | | |
| **Precondición** | El administrador tiene una sesión activa en el sistema | |
| | El administrador posee permisos para gestionar tokens de aplicación | |
| | El token de aplicación a actualizar existe y tiene estado `activo` | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar **AUTH-RT-001** (Generación de Request ID). |
| | 2 | Ejecutar **AUTH-RT-004** (Validación de sesión activa en endpoints propios). |
| | 3 | Recibir el identificador del token a actualizar y los nuevos datos (descripción; [Por definir] si el nombre del servicio también puede modificarse). |
| | 4 | Localizar el registro del token en base de datos. |
| | 5 | Generar un nuevo valor de token y cifrarlo con AES-256 según **AUTH-RT-005**. |
| | 6 | Actualizar el registro en base de datos: nuevo valor cifrado, descripción si fue modificada, identificador del administrador como responsable de la actualización y fecha de actualización. |
| | 7 | Construir la respuesta según **AUTH-RT-003**, incluyendo el nuevo valor del token en texto plano **únicamente en esta respuesta**. |
| | 8 | Ejecutar **AUTH-RT-002** (Auditoría asíncrona). |
| | | |
| **Secuencia alterna** | 4A | Si el token tiene estado `inactivo`, retornar HTTP 409 con mensaje "No se puede actualizar un token desactivado". |
| | | |
| **Excepciones** | E1 | Si no se encuentra el token para el identificador proporcionado, retornar HTTP 404. |
| | E2 | Si el administrador no posee permisos suficientes, retornar HTTP 403. |
| | E3 | Si falla la actualización en base de datos, retornar HTTP 500. |
| | | |
| **Postcondición** | El token de aplicación tiene un nuevo valor cifrado en base de datos | |
| | El administrador recibió el nuevo valor en texto plano para su distribución al microservicio afectado | |
| | | |
| **Comentarios** | La actualización es exclusivamente manual. No existe mecanismo de renovación automática. El microservicio propietario del token deberá ser reconfigurado con el nuevo valor; este proceso operativo queda [Por definir]. | |

---

| | | |
|---|---|---|
| **Código** | AUTH-RF-010 | |
| **Nombre** | Desactivación de token de aplicación | |
| **Descripción** | Permite a un administrador desactivar un token de aplicación, cambiando su estado a `inactivo`. Un token inactivo ya no es aceptado por el sistema para comunicación entre microservicios. | |
| **Actores** | Administrador, ms-autenticacion, ms-auditoria [AUD] | |
| | | |
| **Precondición** | El administrador tiene una sesión activa en el sistema | |
| | El administrador posee permisos para gestionar tokens de aplicación | |
| | El token a desactivar existe y tiene estado `activo` | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar **AUTH-RT-001** (Generación de Request ID). |
| | 2 | Ejecutar **AUTH-RT-004** (Validación de sesión activa en endpoints propios). |
| | 3 | Recibir el identificador del token a desactivar. |
| | 4 | Localizar el registro del token en base de datos y verificar que su estado sea `activo`. |
| | 5 | Actualizar el estado del registro a `inactivo`, registrar el identificador del administrador y la fecha de la acción como última actualización. |
| | 6 | Construir la respuesta de éxito según **AUTH-RT-003** con mensaje "Token desactivado correctamente". |
| | 7 | Ejecutar **AUTH-RT-002** (Auditoría asíncrona). |
| | | |
| **Secuencia alterna** | 4A | Si el token ya tiene estado `inactivo`, retornar HTTP 409 con mensaje "El token ya se encuentra inactivo". |
| | | |
| **Excepciones** | E1 | Si no se encuentra el token para el identificador proporcionado, retornar HTTP 404. |
| | E2 | Si el administrador no posee permisos suficientes, retornar HTTP 403. |
| | E3 | Si falla la actualización en base de datos, retornar HTTP 500. |
| | | |
| **Postcondición** | El token tiene estado `inactivo` en base de datos | |
| | El microservicio propietario del token ya no puede comunicarse con otros servicios | |
| | | |
| **Comentarios** | La desactivación impacta directamente la operación del microservicio propietario. Debe ejecutarse con precaución. No existe en el documento fuente un endpoint de reactivación; se recomienda definir si es necesario [Por definir]. | |

---

### Entidad: Historial de Accesos

---

| | | |
|---|---|---|
| **Código** | AUTH-RF-011 | |
| **Nombre** | Consulta de historial de accesos | |
| **Descripción** | Permite a un administrador consultar el historial de eventos de acceso al sistema con filtros por usuario, tipo de evento y rango de fechas. | |
| **Actores** | Administrador, ms-autenticacion, ms-auditoria [AUD] | |
| | | |
| **Precondición** | El administrador tiene una sesión activa en el sistema | |
| | El administrador posee permisos para consultar el historial de accesos | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar **AUTH-RT-001** (Generación de Request ID). |
| | 2 | Ejecutar **AUTH-RT-004** (Validación de sesión activa en endpoints propios). |
| | 3 | Recibir los parámetros de filtrado opcionales: identificador o nombre de usuario, tipo de evento (`inicio de sesión` / `cierre de sesión` / `intento fallido` / `bloqueo de cuenta`) y rango de fechas (fecha inicio y fecha fin). |
| | 4 | Consultar en base de datos el historial de accesos aplicando los filtros proporcionados. Si no se proporciona ningún filtro, retornar todos los registros con paginación ([Por definir] — tamaño de página y parámetros de paginación). |
| | 5 | Construir la respuesta según **AUTH-RT-003** con la lista de eventos. Cada evento incluye: usuario, tipo de evento, IP, información del cliente, fecha/hora del evento y Request ID. |
| | 6 | Ejecutar **AUTH-RT-002** (Auditoría asíncrona). |
| | | |
| **Secuencia alterna** | 4A | Si no existen registros que coincidan con los filtros proporcionados, retornar lista vacía con HTTP 200. |
| | | |
| **Excepciones** | E1 | Si el administrador no posee permisos suficientes, retornar HTTP 403. |
| | E2 | Si el rango de fechas es inválido (fecha fin anterior a fecha inicio), retornar HTTP 400 con mensaje "Rango de fechas inválido". |
| | E3 | Si ocurre un error al consultar la base de datos, retornar HTTP 500. |
| | | |
| **Postcondición** | El administrador recibe la lista de eventos de acceso filtrada según los criterios proporcionados | |
| | | |
| **Comentarios** | Los registros del historial son de solo lectura; no existe operación de eliminación o modificación. Se recomienda definir una política de retención de datos [Por definir]. | |

---
---

## Categoría 3 — Requisitos Sugeridos

> Los siguientes requisitos no están escritos explícitamente en el documento de referencia, pero se deducen del contexto, las entidades, las dependencias o las buenas prácticas del sistema. Cada uno incluye una justificación de por qué se considera necesario.

---

**Justificación AUTH-RS-001:** El documento establece que las cuentas se bloquean automáticamente tras 5 intentos fallidos (AUTH-RF-006), pero no describe ningún mecanismo para desbloquearlas. Sin este requisito, una cuenta bloqueada permanecería inutilizable indefinidamente, constituyendo una brecha operativa crítica.

| | | |
|---|---|---|
| **Código** | AUTH-RS-001 | |
| **Nombre** | Desbloqueo manual de cuenta bloqueada | |
| **Descripción** | Permite a un administrador desbloquear manualmente la cuenta de un usuario que fue bloqueada por acumulación de intentos fallidos, restaurando su capacidad de acceder al sistema y reiniciando el contador de intentos. | |
| **Actores** | Administrador, ms-autenticacion, ms-usuarios [USR], ms-auditoria [AUD] | |
| | | |
| **Precondición** | El administrador tiene una sesión activa en el sistema | |
| | El administrador posee permisos para gestionar cuentas de usuario | |
| | La cuenta del usuario objetivo tiene estado `bloqueada` en ms-usuarios [USR] | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar **AUTH-RT-001** (Generación de Request ID). |
| | 2 | Ejecutar **AUTH-RT-004** (Validación de sesión activa en endpoints propios). |
| | 3 | Recibir el identificador del usuario a desbloquear. |
| | 4 | Enviar instrucción a **ms-usuarios [USR]** — operación: desbloquear cuenta y reiniciar contador de intentos fallidos a 0. Respuesta esperada: confirmación de que el estado de la cuenta fue actualizado a `activo`. |
| | 5 | Registrar el evento en el historial de accesos: tipo de evento `desbloqueo de cuenta` ([Por definir] si este tipo de evento debe agregarse al catálogo), usuario afectado, identificador del administrador, fecha/hora y Request ID. |
| | 6 | Construir la respuesta de éxito según **AUTH-RT-003** con mensaje "Cuenta desbloqueada correctamente". |
| | 7 | Ejecutar **AUTH-RT-002** (Auditoría asíncrona). |
| | | |
| **Secuencia alterna** | 4A | Si la cuenta del usuario no está bloqueada, retornar HTTP 409 con mensaje "La cuenta no se encuentra bloqueada". |
| | | |
| **Excepciones** | E1 | Si ms-usuarios [USR] no responde o retorna error, retornar HTTP 503. |
| | E2 | Si el administrador no posee permisos suficientes, retornar HTTP 403. |
| | E3 | Si no se encuentra al usuario con el identificador proporcionado, retornar HTTP 404. |
| | | |
| **Postcondición** | La cuenta del usuario tiene estado `activo` y el contador de intentos fallidos es 0 en ms-usuarios [USR] | |
| | El usuario puede volver a intentar iniciar sesión | |
| | | |
| **Comentarios** | Se debe definir si este endpoint pertenece a ms-autenticacion o a ms-usuarios [Por definir]. Se sugiere en ms-autenticacion por ser el responsable del control de acceso. | |

---

**Justificación AUTH-RS-002:** El documento especifica operaciones de creación, consulta individual, actualización y desactivación de tokens de aplicación, pero no describe explícitamente un listado general. Esta vista de conjunto es una necesidad operativa evidente para que el administrador conozca el estado de todos los tokens del sistema en un único punto.

| | | |
|---|---|---|
| **Código** | AUTH-RS-002 | |
| **Nombre** | Listado de tokens de aplicación | |
| **Descripción** | Permite a un administrador obtener el listado completo de todos los tokens de aplicación registrados en el sistema, con sus metadatos y estado actual, sin exponer los valores cifrados. | |
| **Actores** | Administrador, ms-autenticacion, ms-auditoria [AUD] | |
| | | |
| **Precondición** | El administrador tiene una sesión activa en el sistema | |
| | El administrador posee permisos para consultar tokens de aplicación | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar **AUTH-RT-001** (Generación de Request ID). |
| | 2 | Ejecutar **AUTH-RT-004** (Validación de sesión activa en endpoints propios). |
| | 3 | Recibir filtros opcionales: estado (`activo` / `inactivo`). |
| | 4 | Consultar en base de datos todos los registros de tokens de aplicación, aplicando el filtro de estado si fue proporcionado. |
| | 5 | Construir la respuesta según **AUTH-RT-003** con la lista de tokens. Cada elemento incluye: nombre del servicio, descripción, estado, fecha de creación, responsable de última actualización y fecha de última actualización. El valor del token nunca se incluye. |
| | 6 | Ejecutar **AUTH-RT-002** (Auditoría asíncrona). |
| | | |
| **Secuencia alterna** | 4A | Si no existen tokens que coincidan con el filtro, retornar lista vacía con HTTP 200. |
| | | |
| **Excepciones** | E1 | Si el administrador no posee permisos suficientes, retornar HTTP 403. |
| | E2 | Si ocurre error en base de datos, retornar HTTP 500. |
| | | |
| **Postcondición** | El administrador recibe la lista de todos los tokens registrados con sus metadatos | |
| | | |
| **Comentarios** | El valor cifrado del token nunca debe ser expuesto en ninguna operación de consulta, ni en este listado ni en AUTH-RF-008. | |

---

**Justificación AUTH-RS-003:** El documento describe el listado de sesiones activas (AUTH-RF-004), pero no contempla la consulta de sesiones ya cerradas. Este historial es valioso para auditoría forense, investigación de incidentes de seguridad y soporte técnico, y la información ya existe en la entidad de sesión con estado `cerrada`.

| | | |
|---|---|---|
| **Código** | AUTH-RS-003 | |
| **Nombre** | Consulta de sesiones cerradas por usuario | |
| **Descripción** | Permite a un administrador consultar el historial de sesiones cerradas de un usuario específico, con filtro opcional por rango de fechas, para análisis de seguridad o soporte técnico. | |
| **Actores** | Administrador, ms-autenticacion, ms-auditoria [AUD] | |
| | | |
| **Precondición** | El administrador tiene una sesión activa en el sistema | |
| | El administrador posee permisos para administrar sesiones | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar **AUTH-RT-001** (Generación de Request ID). |
| | 2 | Ejecutar **AUTH-RT-004** (Validación de sesión activa en endpoints propios). |
| | 3 | Recibir el identificador del usuario y un rango de fechas opcional. |
| | 4 | Consultar en base de datos los registros de sesión del usuario con estado `cerrada`, aplicando el filtro de rango de fechas si fue proporcionado. |
| | 5 | Construir la respuesta según **AUTH-RT-003** con la lista de sesiones. Cada sesión incluye: identificador de sesión, IP, información del cliente, fecha de creación, fecha de última actividad y fecha de cierre. El valor del token no se incluye. |
| | 6 | Ejecutar **AUTH-RT-002** (Auditoría asíncrona). |
| | | |
| **Secuencia alterna** | 4A | Si no existen sesiones cerradas para el usuario en el rango indicado, retornar lista vacía con HTTP 200. |
| | | |
| **Excepciones** | E1 | Si el administrador no posee permisos suficientes, retornar HTTP 403. |
| | E2 | Si ocurre error en base de datos, retornar HTTP 500. |
| | | |
| **Postcondición** | El administrador recibe el historial de sesiones cerradas del usuario consultado | |
| | | |
| **Comentarios** | Se recomienda definir una política de retención de datos para los registros de sesiones cerradas [Por definir]. | |

---

**Justificación AUTH-RS-004:** ms-autenticacion es el componente más crítico del sistema: si no está disponible, todos los demás microservicios quedan bloqueados al no poder validar sesiones. Un endpoint de health check es una práctica estándar en arquitecturas de microservicios y es fundamental para el monitoreo, los balanceadores de carga y la detección temprana de fallos en el componente más sensible del sistema.

| | | |
|---|---|---|
| **Código** | AUTH-RS-004 | |
| **Nombre** | Health check del servicio de autenticación | |
| **Descripción** | Expone un endpoint ligero y sin autenticación que permite a sistemas de monitoreo y balanceadores de carga verificar que ms-autenticacion está operativo y puede conectarse a su base de datos. | |
| **Actores** | Sistemas de monitoreo, balanceadores de carga, operadores de infraestructura | |
| | | |
| **Precondición** | El servicio ms-autenticacion está en ejecución | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Recibir la petición de health check (sin requerir autenticación ni sesión activa). |
| | 2 | Verificar la conectividad con la base de datos PostgreSQL mediante una consulta ligera (ej: `SELECT 1`). |
| | 3 | Retornar HTTP 200 con un objeto JSON que incluya: estado general (`healthy`), estado de la base de datos (`connected`) y timestamp de la verificación. |
| | | |
| **Secuencia alterna** | 2A | Si la base de datos no responde, retornar HTTP 503 con estado `unhealthy` y detalle del componente fallido. |
| | | |
| **Excepciones** | E1 | Si el propio endpoint falla, el sistema de monitoreo recibirá un error de conexión, lo cual ya indica fallo del servicio. |
| | | |
| **Postcondición** | El sistema de monitoreo conoce el estado operativo de ms-autenticacion | |
| | | |
| **Comentarios** | Este endpoint está excluido de AUTH-RT-004 (no requiere sesión activa) y no debe generar registros de auditoría para evitar saturar ms-auditoria [AUD] con llamadas de monitoreo. Se recomienda restringir su acceso a la red interna del sistema [Por definir]. | |

---

*Fin del documento — AUTH_Requisitos_Funcionales.md*
