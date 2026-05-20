# Microservicio: ms-usuarios [USR]

## Documento de Requisitos Funcionales

| Campo | Detalle |
|-------|---------|
| **Microservicio** | ms-usuarios [USR] |
| **Módulo** | Módulo 1 — Seguridad y Acceso |
| **Versión** | 1.0 |
| **Fecha** | Marzo 2026 |
| **Documento origen** | ERP UNIVERSITARIO - Propuesta de Arquitectura y Requisitos Funcionales v1.0 |

---

## Tabla de Contenido

1. [Extracción Textual](#1-extracción-textual)
2. [Información General](#2-información-general)
3. [Reglas de Negocio](#3-reglas-de-negocio)
4. [Entidades y Datos](#4-entidades-y-datos)
5. [Funcionalidades Requeridas](#5-funcionalidades-requeridas)
6. [Dependencias (de quién dependo)](#6-dependencias-de-quién-dependo)
7. [Consumidores (quién depende de mí)](#7-consumidores-quién-depende-de-mí)

---

## 1. Extracción Textual

A continuación se presentan todos los fragmentos del documento original que son relevantes para el microservicio **ms-usuarios**, sin modificaciones.

### Sección 7.2 — Especificación del Microservicio

#### 7.2 ms-usuarios [USR]

**Propósito:** Gestiona toda la información de los usuarios del sistema: sus credenciales de acceso, datos personales, información de contacto y estados. Es el servicio de referencia cuando cualquier otro componente del sistema necesita datos de un usuario.

##### Información que gestiona

**Usuarios:** Información de las credenciales y estado de cada usuario. Se requiere almacenar: un nombre de usuario único, una dirección de correo electrónico única, la contraseña almacenada como hash cifrado, el estado del usuario (activo, inactivo o suspendido), la fecha y hora de registro y la fecha y hora de la última actualización.

**Perfiles:** Información personal y de contacto extendida de cada usuario. Se requiere almacenar: el tipo de documento de identidad, el número de documento (único), primer nombre, segundo nombre, primer apellido, segundo apellido, fecha de nacimiento, género, dirección de residencia, ciudad, departamento, teléfono fijo, teléfono móvil, nombre del contacto de emergencia, teléfono del contacto de emergencia y una biografía o descripción personal. Se debe registrar la fecha de creación y la fecha de la última actualización del perfil.

**Historial de estados:** Cada vez que el estado de un usuario cambia, se debe registrar: el estado anterior, el nuevo estado, el motivo del cambio, la fecha y hora del cambio y el identificador del usuario que realizó el cambio.

##### Requisitos funcionales

- El sistema debe permitir crear, consultar, actualizar y desactivar usuarios. La desactivación debe ser lógica (no se eliminan registros de la base de datos), cambiando el estado a inactivo y registrando el motivo.
- Al crear un usuario, el sistema debe recibir la contraseña cifrada, descifrarla y almacenarla como hash bcrypt. Debe validar que el nombre de usuario, el correo electrónico y el número de documento no estén duplicados.
- El sistema debe permitir consultar y actualizar el perfil extendido de cada usuario de forma independiente.
- El sistema debe permitir cambiar el estado de un usuario proporcionando un motivo, y debe registrar este cambio en el historial de estados.
- El sistema debe permitir consultar el historial de cambios de estado de un usuario.
- El sistema debe ofrecer una búsqueda avanzada que permita filtrar usuarios por combinaciones de nombre, número de documento, correo electrónico, estado y ciudad, con paginación de resultados que incluya el total de registros y el total de páginas.
- El sistema debe permitir buscar un usuario por su correo electrónico (utilizado internamente por el servicio de autenticación para validar credenciales).
- El sistema debe permitir buscar un usuario por su número de documento.

##### Dependencias con otros servicios

- Debe consultar al servicio de roles para verificar que el rol asignado a un nuevo usuario exista.
- Debe enviar notificaciones a través del servicio de notificaciones cuando una cuenta de usuario es creada, activada o suspendida.
- Debe enviar registros de log al servicio de auditoría de forma asíncrona con cada operación realizada.

---

### Sección 6 — Reglas Transversales del Sistema

Las siguientes reglas son de cumplimiento obligatorio para todos los microservicios del sistema. Representan requisitos no funcionales y de seguridad que garantizan la integridad, trazabilidad y protección del sistema.

#### 6.1 Validación de Sesión Obligatoria

Toda operación realizada por un usuario a través de cualquier microservicio debe ser precedida por una validación de sesión activa. El microservicio que recibe la petición del usuario debe consultar al servicio de autenticación para confirmar que la sesión es válida antes de ejecutar cualquier lógica de negocio. Si la sesión no es válida, el sistema debe rechazar la petición inmediatamente sin procesarla.

#### 6.2 Validación de Permisos por Funcionalidad

Cada funcionalidad del sistema tiene asociado un código de permiso único. Después de validar la sesión, el microservicio debe consultar al servicio de roles para verificar que el rol del usuario tiene autorización para ejecutar la funcionalidad solicitada. Si el usuario no tiene el permiso correspondiente, el sistema debe rechazar la petición.

#### 6.3 Tokens de Aplicación para Comunicación entre Servicios

Cada microservicio posee un token de aplicación único que lo identifica ante los demás servicios. Este token es fijo (no expira ni se renueva automáticamente) y solo puede ser actualizado de forma manual por un administrador. Los tokens se almacenan cifrados con AES-256 y se transmiten cifrados en cada petición entre servicios. Cualquier microservicio puede comunicarse con cualquier otro siempre que posea un token activo y válido.

#### 6.4 Cifrado de Credenciales

Las contraseñas de los usuarios nunca se almacenan en texto plano. Se guardan como hash generado con bcrypt con un factor de costo mínimo de 12. Además, las contraseñas se transmiten cifradas desde el cliente hacia el servidor utilizando AES-256 con codificación Base64. El servidor descifra la contraseña recibida antes de compararla con el hash almacenado. Los tokens de aplicación siguen la misma política: se almacenan cifrados y se transmiten cifrados. En ningún caso deben aparecer credenciales en texto plano en logs, respuestas del sistema ni archivos de configuración.

#### 6.5 Trazabilidad Distribuida (Request ID)

Cada petición que ingresa al sistema recibe un identificador único de rastreo con el formato: código del servicio que la recibe, seguido de un timestamp Unix y un identificador corto aleatorio (ejemplo: `PED-1740000000-a3f8b2`). Este identificador se propaga a todos los microservicios que participan en el procesamiento de la petición. Si un servicio recibe una petición que ya trae un identificador de rastreo (porque proviene de otro servicio), debe reutilizarlo en lugar de generar uno nuevo. Toda respuesta del sistema, independientemente de si la operación fue exitosa o fallida, debe incluir este identificador tanto en las cabeceras como en el cuerpo de la respuesta.

#### 6.6 Auditoría y Logs en Formato JSON

Cada operación realizada en cualquier microservicio debe generar un registro de log en formato JSON que contenga: la fecha y hora de la operación, el identificador de rastreo de la petición, el nombre del microservicio, la funcionalidad ejecutada, el método utilizado, el código de respuesta, la duración en milisegundos, el identificador del usuario que realizó la operación y un detalle descriptivo. Estos registros se envían de forma asíncrona al servicio de auditoría, de manera que el envío no bloquee ni retrase la respuesta al usuario. Si el envío al servicio de auditoría falla, el microservicio debe continuar operando normalmente.

#### 6.7 Estructura de Respuesta Estándar

Todas las respuestas del sistema deben seguir una estructura uniforme que incluya: el identificador de rastreo de la petición, un indicador de éxito o error, los datos resultantes de la operación, un mensaje descriptivo y la fecha y hora de la respuesta.

---

### Referencias en Otros Microservicios

#### Desde ms-autenticacion (Sección 7.1)

##### Dependencias con otros servicios

- Debe consultar al servicio de usuarios para obtener los datos del usuario y verificar sus credenciales durante el inicio de sesión.

#### Desde ms-programas (Sección 7.13)

##### Dependencias con otros servicios

- Debe consultar al servicio de usuarios para validar la existencia del coordinador del programa.

#### Desde ms-notificaciones (Sección 7.17)

##### Dependencias con otros servicios

- Debe consultar al servicio de usuarios para obtener los datos de contacto y las preferencias del destinatario.

---

### Sección 8 — Mapa de Dependencias entre Microservicios

| Microservicio | Consume datos de |
|---|---|
| ms-usuarios | ms-roles, ms-notificaciones |

| Microservicio | Consumido por |
|---|---|
| ms-usuarios | ms-autenticacion, ms-programas, ms-notificaciones |

---

## 2. Información General

**Nombre del microservicio:** ms-usuarios  
**Código:** USR  
**Módulo:** Módulo 1 — Seguridad y Acceso

### Propósito

El microservicio ms-usuarios es el componente central del sistema responsable de gestionar toda la información de los usuarios, incluyendo sus credenciales de acceso, datos personales, información de contacto y estados. Actúa como el servicio de referencia que cualquier otro componente del sistema consulta cuando necesita obtener datos de un usuario.

### Rol dentro del sistema

ms-usuarios es uno de los tres pilares del módulo de Seguridad y Acceso, junto con ms-autenticacion y ms-roles. Su función principal es ser el repositorio maestro de información de usuarios del ERP universitario. Provee servicios de consulta críticos para otros microservicios que necesitan validar la existencia de usuarios, obtener sus datos de contacto o verificar su estado actual. También gestiona el ciclo de vida completo de las cuentas de usuario, desde su creación hasta su desactivación, manteniendo un historial completo de cambios de estado para auditoría y trazabilidad.

---

## 3. Reglas de Negocio

### Reglas Transversales del Sistema (aplican a ms-usuarios)

1. **Validación de sesión obligatoria**: Toda operación realizada por un usuario debe ser precedida por una validación de sesión activa consultando al servicio de autenticación. Si la sesión no es válida, la petición debe ser rechazada inmediatamente.

2. **Validación de permisos por funcionalidad**: Después de validar la sesión, se debe consultar al servicio de roles para verificar que el usuario tiene autorización para ejecutar la funcionalidad solicitada mediante su código de permiso único.

3. **Uso de tokens de aplicación**: Para la comunicación con otros microservicios, ms-usuarios debe utilizar su token de aplicación único, el cual se almacena y transmite cifrado con AES-256.

4. **Cifrado de credenciales obligatorio**: Las contraseñas nunca se almacenan en texto plano. Deben guardarse como hash bcrypt con factor de costo mínimo de 12. Las contraseñas se reciben cifradas con AES-256 en Base64, deben descifrarse antes de procesarse y nunca deben aparecer en logs ni respuestas.

5. **Trazabilidad distribuida mediante Request ID**: Cada petición debe generar o reutilizar un identificador único con el formato `USR-{timestamp}-{aleatorio}` que se propaga a todos los servicios involucrados y se incluye en todas las respuestas.

6. **Generación de logs en formato JSON**: Cada operación debe generar un registro de log que incluya fecha, identificador de rastreo, nombre del microservicio, funcionalidad, método, código de respuesta, duración en milisegundos, identificador de usuario y detalle descriptivo. Los logs se envían de forma asíncrona a ms-auditoria.

7. **Estructura de respuesta estándar**: Todas las respuestas deben seguir una estructura uniforme con identificador de rastreo, indicador de éxito/error, datos resultantes, mensaje descriptivo y timestamp.

### Reglas Específicas del Microservicio

8. **Unicidad de credenciales**: El nombre de usuario, el correo electrónico y el número de documento deben ser únicos en el sistema. No se pueden crear usuarios con credenciales duplicadas.

9. **Desactivación lógica**: La desactivación de usuarios debe ser lógica (soft delete), cambiando el estado a "inactivo" sin eliminar el registro de la base de datos, y debe registrarse el motivo de la desactivación.

10. **Recepción de contraseñas cifradas**: Al crear un usuario, el sistema debe recibir la contraseña cifrada con AES-256, descifrarla y almacenarla como hash bcrypt antes de guardar el registro.

11. **Estados válidos de usuario**: Los usuarios solo pueden estar en tres estados: activo, inactivo o suspendido. Todo cambio de estado debe ser rastreado en el historial.

12. **Registro de cambios de estado**: Cada vez que el estado de un usuario cambia, se debe crear un registro en el historial que incluya el estado anterior, el nuevo estado, el motivo del cambio, la fecha/hora y quién realizó el cambio.

13. **Validación de existencia de rol**: Antes de crear o actualizar un usuario con un rol asignado, se debe consultar a ms-roles para verificar que el rol existe en el sistema.

14. **Notificaciones automáticas**: El sistema debe enviar notificaciones automáticas a través de ms-notificaciones cuando una cuenta de usuario es creada, activada o suspendida.

15. **Paginación obligatoria en búsquedas**: Las búsquedas avanzadas deben incluir paginación de resultados, proporcionando el total de registros y el total de páginas.

### Reglas que Provienen de Relaciones con Otros Microservicios

16. **Validación de credenciales para autenticación (desde ms-autenticacion)**: Debe proveer una funcionalidad de búsqueda por correo electrónico que ms-autenticacion consulta durante el proceso de inicio de sesión para obtener los datos del usuario y verificar sus credenciales.

17. **Validación de coordinadores de programa (desde ms-programas)**: Debe proveer servicios de consulta que permitan a ms-programas validar que un usuario asignado como coordinador de programa existe en el sistema.

18. **Provisión de datos de contacto (desde ms-notificaciones)**: Debe proveer los datos de contacto y las preferencias de notificación de los usuarios cuando ms-notificaciones los solicita para el envío de notificaciones.

---

## 4. Entidades y Datos

### Entidad: Usuarios

**Propósito:** Información de las credenciales y estado de cada usuario.

**Descripción original del documento:** Información de las credenciales y estado de cada usuario.

**Atributos requeridos:**
- Nombre de usuario (único)
- Dirección de correo electrónico (única)
- Contraseña almacenada como hash cifrado
- Estado del usuario (activo, inactivo o suspendido)
- Fecha y hora de registro
- Fecha y hora de la última actualización

### Entidad: Perfiles

**Propósito:** Información personal y de contacto extendida de cada usuario.

**Descripción original del documento:** Información personal y de contacto extendida de cada usuario.

**Atributos requeridos:**
- Tipo de documento de identidad
- Número de documento (único)
- Primer nombre
- Segundo nombre
- Primer apellido
- Segundo apellido
- Fecha de nacimiento
- Género
- Dirección de residencia
- Ciudad
- Departamento
- Teléfono fijo
- Teléfono móvil
- Nombre del contacto de emergencia
- Teléfono del contacto de emergencia
- Biografía o descripción personal
- Fecha de creación
- Fecha de la última actualización del perfil

### Entidad: Historial de Estados

**Propósito:** Registro de cambios de estado de los usuarios para trazabilidad y auditoría.

**Descripción original del documento:** Cada vez que el estado de un usuario cambia, se debe registrar.

**Atributos requeridos:**
- Estado anterior
- Nuevo estado
- Motivo del cambio
- Fecha y hora del cambio
- Identificador del usuario que realizó el cambio

---

## 5. Funcionalidades Requeridas

A continuación se presenta la lista completa de requisitos funcionales del microservicio tal como aparece en el documento original, sin modificaciones:

- El sistema debe permitir crear, consultar, actualizar y desactivar usuarios. La desactivación debe ser lógica (no se eliminan registros de la base de datos), cambiando el estado a inactivo y registrando el motivo.

- Al crear un usuario, el sistema debe recibir la contraseña cifrada, descifrarla y almacenarla como hash bcrypt. Debe validar que el nombre de usuario, el correo electrónico y el número de documento no estén duplicados.

- El sistema debe permitir consultar y actualizar el perfil extendido de cada usuario de forma independiente.

- El sistema debe permitir cambiar el estado de un usuario proporcionando un motivo, y debe registrar este cambio en el historial de estados.

- El sistema debe permitir consultar el historial de cambios de estado de un usuario.

- El sistema debe ofrecer una búsqueda avanzada que permita filtrar usuarios por combinaciones de nombre, número de documento, correo electrónico, estado y ciudad, con paginación de resultados que incluya el total de registros y el total de páginas.

- El sistema debe permitir buscar un usuario por su correo electrónico (utilizado internamente por el servicio de autenticación para validar credenciales).

- El sistema debe permitir buscar un usuario por su número de documento.

---

## 6. Dependencias (de quién dependo)

### ms-roles [ROL]

**Qué información o funcionalidad consume:**
- Validación de existencia de roles antes de asignar un rol a un usuario

**Momento o contexto de la consulta:**
- Durante la creación de un nuevo usuario que tiene un rol asignado
- Durante la actualización de un usuario cuando se modifica su rol

**Detalle:**
ms-usuarios debe consultar a ms-roles para verificar que el rol que se desea asignar a un usuario existe en el sistema antes de completar la operación de creación o actualización. Esto garantiza la integridad referencial de las asignaciones de roles.

---

### ms-notificaciones [NOT]

**Qué información o funcionalidad consume:**
- Servicio de envío de notificaciones

**Momento o contexto de la consulta:**
- Cuando una cuenta de usuario es creada (notificación de bienvenida)
- Cuando una cuenta de usuario es activada (notificación de reactivación)
- Cuando una cuenta de usuario es suspendida (notificación de suspensión)

**Detalle:**
ms-usuarios envía notificaciones automáticas a través de ms-notificaciones para informar a los usuarios sobre cambios importantes en el estado de su cuenta. Estas notificaciones son enviadas de forma asíncrona para no bloquear las operaciones principales del servicio.

---

### ms-auditoria [AUD]

**Qué información o funcionalidad consume:**
- Servicio de registro de logs de auditoría

**Momento o contexto de la consulta:**
- Con cada operación realizada en el microservicio (creación, consulta, actualización, desactivación de usuarios, cambios de estado)

**Detalle:**
ms-usuarios envía registros de log en formato JSON de forma asíncrona a ms-auditoria con cada operación realizada. Los logs incluyen información completa de trazabilidad: fecha/hora, identificador de rastreo, nombre del microservicio, funcionalidad ejecutada, método, código de respuesta, duración, identificador del usuario y detalle descriptivo.

---

### ms-autenticacion [AUTH]

**Qué información o funcionalidad consume:**
- Validación de sesiones activas
- Validación de tokens de aplicación para comunicación entre servicios

**Momento o contexto de la consulta:**
- Antes de ejecutar cualquier operación solicitada por un usuario (validación de sesión)
- En cada comunicación entre ms-usuarios y otros microservicios (validación de token de aplicación)

**Detalle:**
Como parte de las reglas transversales del sistema, ms-usuarios debe consultar a ms-autenticacion para validar que la sesión del usuario es válida antes de procesar cualquier petición. Además, utiliza tokens de aplicación para autenticarse ante otros servicios.

---

## 7. Consumidores (quién depende de mí)

### ms-autenticacion [AUTH]

**Qué información o funcionalidad consume:**
- Datos completos del usuario (credenciales, estado, rol)
- Búsqueda de usuario por correo electrónico

**Momento o contexto de la consulta:**
- Durante el proceso de inicio de sesión del usuario
- Para verificar credenciales y obtener datos del usuario que se incluirán en el token JWT

**Detalle:**
ms-autenticacion es el principal consumidor de ms-usuarios. Consulta los datos del usuario por correo electrónico durante el proceso de autenticación para verificar las credenciales (comparando el hash de la contraseña) y obtener información como el rol y los permisos del usuario que se incluirán en el token de sesión generado.

---

### ms-programas [PRG]

**Qué información o funcionalidad consume:**
- Validación de existencia de usuarios
- Datos de usuarios asignados como coordinadores de programa

**Momento o contexto de la consulta:**
- Al crear o actualizar un programa académico que tiene un coordinador asignado
- Para validar que el usuario designado como coordinador existe y está activo

**Detalle:**
ms-programas consulta a ms-usuarios para verificar que el usuario que se desea asignar como coordinador de un programa académico existe en el sistema y está en estado activo. Esto garantiza la integridad de las asignaciones de roles académicos.

---

### ms-notificaciones [NOT]

**Qué información o funcionalidad consume:**
- Datos de contacto de los usuarios (correo electrónico, teléfono móvil)
- Preferencias de notificación de los usuarios

**Momento o contexto de la consulta:**
- Al momento de enviar notificaciones a usuarios específicos
- Para obtener la información de contacto necesaria para el envío
- Para respetar las preferencias configuradas por cada usuario (canal preferido, horarios de no molestar)

**Detalle:**
ms-notificaciones consulta a ms-usuarios para obtener los datos de contacto necesarios al enviar notificaciones. Esto incluye el correo electrónico, teléfono móvil y las preferencias de notificación configuradas por cada usuario, garantizando que las notificaciones se envíen por el canal correcto y respetando las preferencias del destinatario.

---

### Otros microservicios (de forma indirecta)

**Detalle adicional:**
Aunque no están explícitamente mencionados en el mapa de dependencias, prácticamente todos los microservicios del sistema pueden necesitar consultar información básica de usuarios en diversos contextos, como:
- Validar la existencia de un usuario al registrar operaciones
- Obtener nombres y datos básicos para mostrar en interfaces
- Verificar estados de usuarios antes de permitir ciertas operaciones

---

## Notas Finales

Este documento contiene toda la información relevante extraída del documento original de requisitos funcionales para el microservicio **ms-usuarios**. El equipo de desarrollo debe utilizarlo como base para:

1. Elaborar los diagramas de casos de uso específicos del microservicio
2. Diseñar el modelo de clases y el diagrama entidad-relación de la base de datos
3. Definir los endpoints REST de la API
4. Implementar las funcionalidades descritas
5. Diseñar las pruebas unitarias y de integración

**Stack tecnológico a utilizar:**
- Lenguaje: Python
- Framework: FastAPI
- Base de datos: PostgreSQL
- Cifrado de contraseñas: bcrypt (salt rounds ≥ 12)
- Cifrado de datos: AES-256
- Autenticación: JWT (JSON Web Tokens)
- Documentación automática: Swagger UI

**Contacto para aclaraciones:**
Para cualquier duda o aclaración sobre estos requisitos, contactar al Arquitecto de Software del proyecto.

---

**Fin del documento**
