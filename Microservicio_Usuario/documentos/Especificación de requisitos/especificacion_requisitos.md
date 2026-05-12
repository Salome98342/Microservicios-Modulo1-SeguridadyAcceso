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
