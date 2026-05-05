# Especificación del Microservicio: MS-AUTENTICACION [AUTH]

> **Documento generado a partir de:** Propuesta de Arquitectura y Requisitos Funcionales — ERP Universitario v1.0
> **Fecha de generación:** Febrero 2026
> **Microservicio analizado:** ms-autenticacion [AUTH]

---

## 1. Extracción Textual

A continuación se reproducen, sin modificación, todos los fragmentos del documento original que hacen referencia al microservicio ms-autenticacion.

---

### 1.1 Sección 5 — Arquitectura General → Módulo 1: Seguridad y Acceso

> **Módulo 1 — Seguridad y Acceso**
>
> Responsable de la autenticación de usuarios, gestión de sesiones, control de tokens de aplicación para comunicación entre servicios, y administración de roles y permisos.
>
> - ms-autenticacion
> - ms-usuarios
> - ms-roles

---

### 1.2 Sección 6 — Reglas Transversales del Sistema (que aplican a ms-autenticacion)

> **6.1 Validación de Sesión Obligatoria**
>
> Toda operación realizada por un usuario a través de cualquier microservicio debe ser precedida por una validación de sesión activa. El microservicio que recibe la petición del usuario debe consultar al servicio de autenticación para confirmar que la sesión es válida antes de ejecutar cualquier lógica de negocio. Si la sesión no es válida, el sistema debe rechazar la petición inmediatamente sin procesarla.

> **6.3 Tokens de Aplicación para Comunicación entre Servicios**
>
> Cada microservicio posee un token de aplicación único que lo identifica ante los demás servicios. Este token es fijo (no expira ni se renueva automáticamente) y solo puede ser actualizado de forma manual por un administrador. Los tokens se almacenan cifrados con AES-256 y se transmiten cifrados en cada petición entre servicios. Cualquier microservicio puede comunicarse con cualquier otro siempre que posea un token activo y válido.

> **6.4 Cifrado de Credenciales**
>
> Las contraseñas de los usuarios nunca se almacenan en texto plano. Se guardan como hash generado con bcrypt con un factor de costo mínimo de 12. Además, las contraseñas se transmiten cifradas desde el cliente hacia el servidor utilizando AES-256 con codificación Base64. El servidor descifra la contraseña recibida antes de compararla con el hash almacenado. Los tokens de aplicación siguen la misma política: se almacenan cifrados y se transmiten cifrados. En ningún caso deben aparecer credenciales en texto plano en logs, respuestas del sistema ni archivos de configuración.

> **6.5 Trazabilidad Distribuida (Request ID)**
>
> Cada petición que ingresa al sistema recibe un identificador único de rastreo con el formato: código del servicio que la recibe, seguido de un timestamp Unix y un identificador corto aleatorio (ejemplo: `PED-1740000000-a3f8b2`). Este identificador se propaga a todos los microservicios que participan en el procesamiento de la petición. Si un servicio recibe una petición que ya trae un identificador de rastreo (porque proviene de otro servicio), debe reutilizarlo en lugar de generar uno nuevo. Toda respuesta del sistema, independientemente de si la operación fue exitosa o fallida, debe incluir este identificador tanto en las cabeceras como en el cuerpo de la respuesta.

> **6.6 Auditoría y Logs en Formato JSON**
>
> Cada operación realizada en cualquier microservicio debe generar un registro de log en formato JSON que contenga: la fecha y hora de la operación, el identificador de rastreo de la petición, el nombre del microservicio, la funcionalidad ejecutada, el método utilizado, el código de respuesta, la duración en milisegundos, el identificador del usuario que realizó la operación y un detalle descriptivo. Estos registros se envían de forma asíncrona al servicio de auditoría, de manera que el envío no bloquee ni retrase la respuesta al usuario. Si el envío al servicio de auditoría falla, el microservicio debe continuar operando normalmente.

> **6.7 Estructura de Respuesta Estándar**
>
> Todas las respuestas del sistema deben seguir una estructura uniforme que incluya: el identificador de rastreo de la petición, un indicador de éxito o error, los datos resultantes de la operación, un mensaje descriptivo y la fecha y hora de la respuesta.

---

### 1.3 Sección 7.1 — Especificación Funcional de ms-autenticacion

> #### 7.1 ms-autenticacion [AUTH]
>
> **Propósito:** Servicio central de seguridad del sistema. Es responsable de autenticar a los usuarios, gestionar sus sesiones activas, administrar los tokens de aplicación que permiten la comunicación entre microservicios y proveer la funcionalidad de validación de sesión que todos los demás servicios deben consumir antes de ejecutar cualquier operación.
>
> ##### Información que gestiona
>
> **Sesiones de usuario:** El sistema debe registrar y mantener las sesiones activas de los usuarios. De cada sesión se requiere almacenar: el usuario al que pertenece, el token generado para la sesión, la dirección IP desde la cual se conectó, la información del navegador o cliente utilizado, la fecha y hora en que se creó la sesión, la fecha y hora de la última actividad registrada y el estado de la sesión (activa o cerrada). Se debe registrar también la fecha y hora de creación y de cualquier modificación al registro.
>
> **Tokens de aplicación:** El sistema debe almacenar los tokens que identifican a cada microservicio. De cada token se requiere: el nombre del servicio al que pertenece, el valor del token almacenado de forma cifrada, una descripción del servicio, el estado del token (activo o inactivo), la fecha de creación, quién realizó la última actualización y la fecha de dicha actualización.
>
> **Historial de accesos:** El sistema debe registrar un historial de todos los eventos de acceso. De cada evento se requiere: el usuario involucrado, el tipo de evento (inicio de sesión, cierre de sesión, intento fallido o bloqueo de cuenta), la dirección IP, la información del navegador o cliente, la fecha y hora del evento y el identificador de rastreo de la petición.
>
> ##### Requisitos funcionales
>
> - El sistema debe permitir a un usuario iniciar sesión proporcionando sus credenciales cifradas. Al autenticarse correctamente, debe generar un token JWT que contenga el identificador del usuario, su rol y sus permisos, y crear un registro de sesión activa.
> - El sistema debe permitir a un usuario cerrar su sesión, invalidando el token y marcando la sesión como cerrada.
> - El sistema debe proveer una funcionalidad de validación de sesión que, dado un token de usuario, verifique que la sesión existe en la base de datos y que se encuentra activa. Este es el servicio más crítico del sistema, ya que todos los demás microservicios lo consumen antes de ejecutar cualquier operación.
> - El sistema debe permitir crear, consultar, actualizar y desactivar tokens de aplicación. Los tokens se generan cifrados con AES-256 y no tienen fecha de expiración; solo se actualizan o desactivan de forma manual.
> - El sistema debe permitir listar las sesiones activas del sistema, con posibilidad de filtrar por usuario, y permitir forzar el cierre de una sesión específica por parte de un administrador.
> - El sistema debe permitir consultar el historial de accesos con filtros por usuario, tipo de evento y rango de fechas.
> - El sistema debe implementar un mecanismo de bloqueo por intentos fallidos: después de 5 intentos consecutivos de inicio de sesión fallidos, la cuenta del usuario debe bloquearse. El contador de intentos se reinicia cuando el usuario inicia sesión exitosamente.
> - Las sesiones no expiran por tiempo. Solo se invalidan mediante cierre de sesión explícito por parte del usuario o cierre forzado por un administrador.
>
> ##### Dependencias con otros servicios
>
> - Debe consultar al servicio de usuarios para obtener los datos del usuario y verificar sus credenciales durante el inicio de sesión.
> - Debe consultar al servicio de roles para obtener el rol y los permisos del usuario al momento de generar el token JWT.
> - Debe enviar registros de log al servicio de auditoría de forma asíncrona con cada operación realizada.

---

### 1.4 Sección 7.3 — ms-roles hace referencia a ms-autenticacion

> **ms-roles | Consume datos de:** ms-autenticacion (confianza mutua)

*(Fragmento extraído del mapa de dependencias — Sección 8)*

---

### 1.5 Sección 8 — Mapa de Dependencias (fila de ms-autenticacion y nota general)

> | ms-autenticacion | ms-usuarios, ms-roles |

> Adicionalmente, todos los microservicios (excepto ms-autenticacion y ms-roles entre sí) consumen:
>
> - **ms-autenticacion** para validar sesiones activas.
> - **ms-roles** para validar permisos por funcionalidad.
> - **ms-auditoria** para enviar registros de log de forma asíncrona.

---

## 2. Información General

| Campo | Detalle |
|---|---|
| **Nombre** | ms-autenticacion |
| **Código** | AUTH |
| **Módulo** | Módulo 1 — Seguridad y Acceso |
| **Stack** | FastAPI + Python + PostgreSQL |

**Propósito:**
ms-autenticacion es el servicio central de seguridad del sistema ERP universitario. Es responsable de autenticar a los usuarios, gestionar sus sesiones activas y administrar los tokens de aplicación que permiten la comunicación segura entre microservicios. Adicionalmente, provee la funcionalidad de validación de sesión que **todos los demás servicios** deben consumir antes de ejecutar cualquier operación, convirtiéndolo en el componente más crítico de toda la arquitectura.

**Rol dentro del sistema:**
Actúa como guardián de acceso de todo el sistema. Sin ms-autenticacion, ningún otro microservicio puede operar, ya que la validación de sesión es un requisito transversal obligatorio.

---

## 3. Reglas de Negocio

### 3.1 Reglas Transversales del Sistema que Aplican a ms-autenticacion

1. **Validación de sesión obligatoria (RT-01):** Aunque ms-autenticacion es quien *provee* el servicio de validación, sus propios endpoints (excepto login) también deben validar que quien realiza la petición tenga sesión activa.
2. **Cifrado de credenciales (RT-04):** Las contraseñas nunca se almacenan en texto plano. Se almacenan como hash bcrypt con factor de costo mínimo de 12. Las contraseñas se reciben cifradas con AES-256 + Base64 desde el cliente; el servidor las descifra antes de compararlas. Los tokens de aplicación también se almacenan y transmiten cifrados. Ninguna credencial puede aparecer en logs, respuestas ni archivos de configuración.
3. **Tokens de aplicación (RT-03):** Cada microservicio tiene un token de aplicación único, fijo, sin expiración automática y cifrado con AES-256. Solo un administrador puede actualizarlos o desactivarlos manualmente.
4. **Trazabilidad distribuida (RT-05):** Cada petición recibida debe generar un Request ID con el formato `AUTH-<timestamp_unix>-<id_corto>`. Si la petición ya trae un Request ID (proveniente de otro servicio), debe reutilizarlo. El Request ID debe incluirse en cabeceras y cuerpo de toda respuesta.
5. **Auditoría asíncrona (RT-06):** Cada operación debe generar un log en formato JSON y enviarlo de forma asíncrona a ms-auditoria. Si el envío falla, el servicio debe continuar operando con normalidad (patrón fire-and-forget).
6. **Estructura de respuesta estándar (RT-07):** Todas las respuestas deben incluir: Request ID, indicador de éxito/error, datos del resultado, mensaje descriptivo y fecha/hora de la respuesta.

### 3.2 Reglas Específicas de ms-autenticacion

7. **Inicio de sesión con credenciales cifradas:** El usuario debe enviar sus credenciales cifradas. El sistema las descifra, valida contra el hash almacenado y, si son correctas, genera un JWT que contenga el identificador del usuario, su rol y sus permisos.
8. **Creación de sesión activa:** Al autenticar correctamente, se debe crear un registro de sesión activa que almacene usuario, token, IP, datos del cliente, fecha/hora de creación y última actividad.
9. **Cierre de sesión:** Al cerrar sesión, el token debe invalidarse y la sesión debe marcarse como cerrada.
10. **Validación de sesión para terceros:** El servicio debe exponer un endpoint de validación que, dado un token, verifique que la sesión existe en base de datos y está activa. Este endpoint es consumido por todos los demás microservicios del sistema.
11. **Sesiones sin expiración por tiempo:** Las sesiones no caducan automáticamente por inactividad o tiempo transcurrido. Solo se invalidan por cierre explícito del usuario o cierre forzado por un administrador.
12. **Bloqueo por intentos fallidos:** Después de 5 intentos consecutivos fallidos de inicio de sesión, la cuenta del usuario debe bloquearse. El contador se reinicia al iniciar sesión exitosamente.
13. **Gestión de tokens de aplicación:** Los tokens de aplicación se crean cifrados con AES-256, no tienen fecha de expiración y solo se pueden desactivar o actualizar manualmente por un administrador.
14. **Administración de sesiones por administrador:** Un administrador puede listar todas las sesiones activas (filtrando por usuario) y forzar el cierre de una sesión específica.
15. **Historial de accesos:** Cada evento de acceso (inicio de sesión, cierre de sesión, intento fallido, bloqueo de cuenta) debe registrarse con usuario, tipo de evento, IP, cliente, fecha/hora y Request ID.

### 3.3 Reglas Derivadas de la Relación con Otros Microservicios

16. **Antes de autenticar, consultar ms-usuarios:** Durante el inicio de sesión, ms-autenticacion debe consultar a ms-usuarios para obtener los datos del usuario y verificar sus credenciales.
17. **Antes de emitir el JWT, consultar ms-roles:** ms-autenticacion debe consultar a ms-roles para obtener el rol y los permisos del usuario e incluirlos en el token JWT generado.
18. **Relación de confianza mutua con ms-roles:** Existe una relación de confianza mutua documentada entre ms-autenticacion y ms-roles. Ambos servicios se reconocen mutuamente sin requerir la cadena completa de validación que aplica a los demás servicios.

---

## 4. Entidades y Datos

### 4.1 Sesiones de usuario

> **Sesiones de usuario:** El sistema debe registrar y mantener las sesiones activas de los usuarios. De cada sesión se requiere almacenar: el usuario al que pertenece, el token generado para la sesión, la dirección IP desde la cual se conectó, la información del navegador o cliente utilizado, la fecha y hora en que se creó la sesión, la fecha y hora de la última actividad registrada y el estado de la sesión (activa o cerrada). Se debe registrar también la fecha y hora de creación y de cualquier modificación al registro.

| Atributo | Descripción |
|---|---|
| usuario | Usuario al que pertenece la sesión |
| token | Token JWT generado para la sesión |
| dirección IP | IP desde la cual se conectó el usuario |
| información del cliente | Navegador o cliente utilizado |
| fecha y hora de creación | Cuándo se creó la sesión |
| fecha y hora de última actividad | Última actividad registrada |
| estado | Activa o cerrada |
| fecha de creación del registro | Auditoría de creación |
| fecha de modificación del registro | Auditoría de modificación |

---

### 4.2 Tokens de aplicación

> **Tokens de aplicación:** El sistema debe almacenar los tokens que identifican a cada microservicio. De cada token se requiere: el nombre del servicio al que pertenece, el valor del token almacenado de forma cifrada, una descripción del servicio, el estado del token (activo o inactivo), la fecha de creación, quién realizó la última actualización y la fecha de dicha actualización.

| Atributo | Descripción |
|---|---|
| nombre del servicio | Microservicio al que pertenece el token |
| valor del token | Token almacenado cifrado con AES-256 |
| descripción | Descripción del servicio |
| estado | Activo o inactivo |
| fecha de creación | Cuándo se creó el token |
| quién realizó la última actualización | Usuario administrador responsable |
| fecha de última actualización | Cuándo se actualizó por última vez |

---

### 4.3 Historial de accesos

> **Historial de accesos:** El sistema debe registrar un historial de todos los eventos de acceso. De cada evento se requiere: el usuario involucrado, el tipo de evento (inicio de sesión, cierre de sesión, intento fallido o bloqueo de cuenta), la dirección IP, la información del navegador o cliente, la fecha y hora del evento y el identificador de rastreo de la petición.

| Atributo | Descripción |
|---|---|
| usuario | Usuario involucrado en el evento |
| tipo de evento | inicio de sesión / cierre de sesión / intento fallido / bloqueo de cuenta |
| dirección IP | IP desde la cual ocurrió el evento |
| información del cliente | Navegador o cliente utilizado |
| fecha y hora del evento | Cuándo ocurrió el evento |
| identificador de rastreo | Request ID de la petición asociada |

---

## 5. Funcionalidades Requeridas

> - El sistema debe permitir a un usuario iniciar sesión proporcionando sus credenciales cifradas. Al autenticarse correctamente, debe generar un token JWT que contenga el identificador del usuario, su rol y sus permisos, y crear un registro de sesión activa.
> - El sistema debe permitir a un usuario cerrar su sesión, invalidando el token y marcando la sesión como cerrada.
> - El sistema debe proveer una funcionalidad de validación de sesión que, dado un token de usuario, verifique que la sesión existe en la base de datos y que se encuentra activa. Este es el servicio más crítico del sistema, ya que todos los demás microservicios lo consumen antes de ejecutar cualquier operación.
> - El sistema debe permitir crear, consultar, actualizar y desactivar tokens de aplicación. Los tokens se generan cifrados con AES-256 y no tienen fecha de expiración; solo se actualizan o desactivan de forma manual.
> - El sistema debe permitir listar las sesiones activas del sistema, con posibilidad de filtrar por usuario, y permitir forzar el cierre de una sesión específica por parte de un administrador.
> - El sistema debe permitir consultar el historial de accesos con filtros por usuario, tipo de evento y rango de fechas.
> - El sistema debe implementar un mecanismo de bloqueo por intentos fallidos: después de 5 intentos consecutivos de inicio de sesión fallidos, la cuenta del usuario debe bloquearse. El contador de intentos se reinicia cuando el usuario inicia sesión exitosamente.
> - Las sesiones no expiran por tiempo. Solo se invalidan mediante cierre de sesión explícito por parte del usuario o cierre forzado por un administrador.

---

## 6. Dependencias (de quién dependo)

| Microservicio | Qué consume | Cuándo se realiza la consulta |
|---|---|---|
| **ms-usuarios** [USR] | Datos del usuario (credenciales, estado) para verificarlos durante el proceso de autenticación | Durante el inicio de sesión, antes de generar el token JWT |
| **ms-roles** [ROL] | Rol del usuario y lista de permisos asociados para incluirlos en el token JWT | Durante el inicio de sesión, al momento de generar el JWT, después de validar las credenciales |
| **ms-auditoria** [AUD] | Servicio de recepción de logs | De forma asíncrona tras cada operación realizada (fire-and-forget) |

---

## 7. Consumidores (quién depende de mí)

Según el mapa de dependencias (Sección 8) y las reglas transversales (Sección 6.1), **todos los microservicios del sistema** consumen ms-autenticacion para validar sesiones activas antes de ejecutar cualquier operación. A continuación se detalla el consumo de cada uno:

| Microservicio consumidor | Qué consume | Cuándo realiza la consulta |
|---|---|---|
| **ms-usuarios** [USR] | Validación de sesión activa | Antes de ejecutar cualquier operación |
| **ms-roles** [ROL] | Confianza mutua (reconocimiento recíproco) | Al recibir peticiones de autenticación |
| **ms-inventario** [INV] | Validación de sesión activa | Antes de ejecutar cualquier operación |
| **ms-espacios** [ESP] | Validación de sesión activa | Antes de ejecutar cualquier operación |
| **ms-reservas** [RES] | Validación de sesión activa | Antes de ejecutar cualquier operación |
| **ms-presupuesto** [PRE] | Validación de sesión activa | Antes de ejecutar cualquier operación |
| **ms-gastos** [GAS] | Validación de sesión activa | Antes de ejecutar cualquier operación |
| **ms-facturacion** [FAC] | Validación de sesión activa | Antes de ejecutar cualquier operación |
| **ms-pedidos** [PED] | Validación de sesión activa | Antes de ejecutar cualquier operación |
| **ms-domicilios** [DOM] | Validación de sesión activa | Antes de ejecutar cualquier operación |
| **ms-proveedores** [PRO] | Validación de sesión activa | Antes de ejecutar cualquier operación |
| **ms-programas** [PGM] | Validación de sesión activa | Antes de ejecutar cualquier operación |
| **ms-matriculas** [MAT] | Validación de sesión activa | Antes de ejecutar cualquier operación |
| **ms-calificaciones** [CAL] | Validación de sesión activa | Antes de ejecutar cualquier operación |
| **ms-horarios** [HOR] | Validación de sesión activa | Antes de ejecutar cualquier operación |
| **ms-notificaciones** [NOT] | Validación de sesión activa | Antes de ejecutar cualquier operación |
| **ms-auditoria** [AUD] | Validación de sesión activa | Antes de ejecutar cualquier operación |
| **ms-reportes** [REP] | Validación de sesión activa | Antes de ejecutar cualquier operación |

> **Nota:** La regla transversal 6.1 establece explícitamente que *todos* los microservicios (excepto ms-autenticacion y ms-roles entre sí) deben consultar ms-autenticacion antes de ejecutar cualquier operación. ms-autenticacion es, por tanto, el microservicio con mayor número de consumidores del sistema.

---

*Fin del documento — MS-AUTENTICACION [AUTH]*
