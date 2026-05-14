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

#### REQ1 — Crear usuario
| Campo | Detalle |
|---|---|
| Código | REQ1 |
| Nombre | Crear usuario |
| Entradas | `username`, `email`, contraseña, `rol_id`. |
| Validaciones | Unicidad de `username` y `email`; consistencia de datos de creación. |
| Seguridad | Manejo seguro de contraseña y flujo de registro. |
| Resultado esperado | Usuario creado con estado inicial `activo` o respuesta de validación si falla alguna regla. |

#### REQ2 — Consultar usuario por ID
| Campo | Detalle |
|---|---|
| Código | REQ2 |
| Nombre | Consultar usuario por ID |
| Entradas | `user_id`. |
| Validaciones | Existencia del identificador consultado. |
| Seguridad | Exposición de datos públicos del usuario. |
| Resultado esperado | Retorno de datos públicos del usuario o error de no encontrado. |

#### REQ3 — Consultar usuario por email
| Campo | Detalle |
|---|---|
| Código | REQ3 |
| Nombre | Consultar usuario por email |
| Entradas | `email`. |
| Validaciones | Formato y existencia del correo consultado. |
| Seguridad | En integración interna con autenticación puede incluir `password_hash`. |
| Resultado esperado | Retorno de datos del usuario asociado al correo o error de no encontrado. |

#### REQ4 — Actualizar datos básicos de usuario
| Campo | Detalle |
|---|---|
| Código | REQ4 |
| Nombre | Actualizar datos básicos de usuario |
| Entradas | `username`, `email` y/o `rol_id` del usuario objetivo. |
| Validaciones | Colisiones de `username`/`email` y reglas de rol. |
| Seguridad | Control de actualización de atributos sensibles del usuario. |
| Resultado esperado | Datos básicos actualizados correctamente o error por validación/regla de negocio. |

#### REQ5 — Cambiar estado de usuario
| Campo | Detalle |
|---|---|
| Código | REQ5 |
| Nombre | Cambiar estado de usuario |
| Entradas | Estado destino (`activo`, `inactivo`, `suspendido`) y motivo. |
| Validaciones | Estado permitido y consistencia del cambio de estado. |
| Seguridad | Registro de auditoría y trazabilidad del cambio. |
| Resultado esperado | Estado actualizado y evento registrado en historial/auditoría. |

#### REQ6 — Desactivar y reactivar usuario
| Campo | Detalle |
|---|---|
| Código | REQ6 |
| Nombre | Desactivar y reactivar usuario |
| Entradas | Acción de desactivar o reactivar sobre un usuario existente. |
| Validaciones | Existencia del usuario y transición válida de estado. |
| Seguridad | Operación lógica con trazabilidad y notificación. |
| Resultado esperado | Usuario desactivado o reactivado con registro de la operación. |

#### REQ7 — Gestionar contraseña
| Campo | Detalle |
|---|---|
| Código | REQ7 |
| Nombre | Gestionar contraseña |
| Entradas | Contraseña actual y nueva contraseña. |
| Validaciones | Verificación de contraseña actual y política de seguridad de la nueva clave. |
| Seguridad | Actualización segura de credencial del propio usuario. |
| Resultado esperado | Contraseña actualizada o error por validación/credencial inválida. |

#### REQ8 — Gestionar perfil extendido
| Campo | Detalle |
|---|---|
| Código | REQ8 |
| Nombre | Gestionar perfil extendido |
| Entradas | Datos del perfil extendido asociados al usuario. |
| Validaciones | Existencia del usuario y consistencia de los campos de perfil. |
| Seguridad | Asociación controlada del perfil a su usuario propietario. |
| Resultado esperado | Perfil extendido creado/actualizado/consultado correctamente. |

#### REQ9 — Gestionar preferencias de notificación
| Campo | Detalle |
|---|---|
| Código | REQ9 |
| Nombre | Gestionar preferencias de notificación |
| Entradas | Configuración de preferencias y horarios de no molestar por usuario. |
| Validaciones | Formato y coherencia de preferencias/horarios. |
| Seguridad | Configuración aplicada al usuario correspondiente. |
| Resultado esperado | Preferencias consultadas o actualizadas correctamente. |

#### REQ10 — Consultar historial de estados
| Campo | Detalle |
|---|---|
| Código | REQ10 |
| Nombre | Consultar historial de estados |
| Entradas | Identificador de usuario para consulta histórica. |
| Validaciones | Existencia de usuario e integridad del historial consultado. |
| Seguridad | Acceso controlado a información de trazabilidad. |
| Resultado esperado | Retorno cronológico de cambios de estado del usuario. |

#### REQ11 — Consultar catálogo de tipos de documento
| Campo | Detalle |
|---|---|
| Código | REQ11 |
| Nombre | Consultar catálogo de tipos de documento |
| Entradas | Solicitud de catálogo (sin filtros obligatorios). |
| Validaciones | Estado activo de tipos de documento retornados. |
| Seguridad | Exposición de catálogo de referencia para perfiles. |
| Resultado esperado | Lista de tipos de documento activos disponible para consumo. |

#### REQ12 — Búsqueda avanzada y paginación
| Campo | Detalle |
|---|---|
| Código | REQ12 |
| Nombre | Búsqueda avanzada y paginación |
| Entradas | Filtros (`nombre`, `documento`, `email`, `estado`, `ciudad`) y parámetros de paginación. |
| Validaciones | Coherencia de filtros y parámetros de paginación. |
| Seguridad | Consulta acotada con respuesta paginada. |
| Resultado esperado | Lista de usuarios filtrada y paginada según criterios. |

#### REQ13 — Estadísticas por estado
| Campo | Detalle |
|---|---|
| Código | REQ13 |
| Nombre | Estadísticas por estado |
| Entradas | Solicitud de agregación estadística del universo de usuarios. |
| Validaciones | Consistencia del conteo total y distribución por estado. |
| Seguridad | Entrega de datos agregados sin exponer información sensible individual. |
| Resultado esperado | Total de usuarios y distribución por estado disponible para consulta. |

#### REQ14 — Listar usuarios por rol
| Campo | Detalle |
|---|---|
| Código | REQ14 |
| Nombre | Listar usuarios por rol |
| Entradas | `rol_id` y estado opcional. |
| Validaciones | Existencia/validez del rol y del estado opcional. |
| Seguridad | Filtrado controlado por criterios funcionales permitidos. |
| Resultado esperado | Listado de usuarios que cumplen filtro por rol (y estado si aplica). |

#### REQ15 — Validación interna de existencia y credenciales
| Campo | Detalle |
|---|---|
| Código | REQ15 |
| Nombre | Validación interna de existencia y credenciales |
| Entradas | Datos internos de identificación y verificación de credenciales. |
| Validaciones | Verificación de existencia de usuario y validez de credenciales. |
| Seguridad | Uso interno para integración con autenticación. |
| Resultado esperado | Confirmación o rechazo de existencia/credenciales para flujos internos. |
