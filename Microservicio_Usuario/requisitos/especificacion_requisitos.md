# Especificación de Requisitos

## 1. Introducción

Este documento presenta la especificación de requisitos funcionales a nivel del sistema para el microservicio de usuario.

## 2. Requisitos Funcionales a Nivel del Sistema

Declaración de los requisitos funcionales a nivel del sistema, no expresados como casos de uso. Ejemplos incluyen auditoría, autenticación, impresión e informes.

| Código | Nombre | Descripción |
|---|---|---|
| REQ1 | Crear usuario | Permite al cliente registrar un nuevo usuario en el sistema con credenciales y rol asignado. |

### 2.1 Detalle adicional de requisitos

**REQ1 - Crear usuario**

- **Entradas:** `username`, `email`, `contraseña`, `rol_id`.
- **Validaciones:** campos obligatorios y unicidad de usuario/correo.
- **Seguridad:** almacenar contraseña con hash seguro (bcrypt).
- **Resultado esperado:** éxito al crear el registro o error de validación si hay datos faltantes o duplicados.
