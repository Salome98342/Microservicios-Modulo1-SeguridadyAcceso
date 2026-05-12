# Diagramas de secuencia — Microservicio de Usuarios

## 1) Crear usuario (`POST /api/v1/users`)

```mermaid
sequenceDiagram
    actor Cliente
    participant API as Router Usuarios
    participant Auth as ms-autenticacion/ms-permisos
    participant SVC as usuario_service
    participant DB as usuario_repository (PostgreSQL)
    participant Notif as ms-notificaciones

    Cliente->>API: POST /users + Authorization
    API->>Auth: validar_sesion_activa()
    Auth-->>API: sesión válida
    API->>Auth: validar_permiso(USR_CREATE)
    Auth-->>API: permitido
    API->>SVC: crear_usuario()
    SVC->>DB: existe_username / existe_email
    DB-->>SVC: validación
    SVC->>DB: crear()
    DB-->>SVC: usuario creado
    SVC-->>API: usuario
    API->>Notif: notificar_async(user_welcome)
    API-->>Cliente: 201 Usuario creado
```

## 2) Actualizar perfil (`PUT /api/v1/users/{usuario_id}/profile`)

```mermaid
sequenceDiagram
    actor Cliente
    participant API as Router Perfiles
    participant Auth as ms-autenticacion/ms-permisos
    participant SVC as perfil_service
    participant URepo as usuario_repository
    participant TRepo as tipo_documento_repository
    participant PRepo as perfil_repository

    Cliente->>API: PUT /users/{id}/profile
    API->>Auth: validar_sesion_activa()
    Auth-->>API: sesión válida
    API->>Auth: validar_permiso(USR_PROFILE_UPDATE)
    Auth-->>API: permitido
    API->>SVC: crear_o_actualizar_perfil(id, datos)
    SVC->>URepo: obtener_por_id(id)
    URepo-->>SVC: usuario
    SVC->>TRepo: obtener_por_id(tipo_documento_id)
    TRepo-->>SVC: tipo activo
    SVC->>PRepo: crear_o_actualizar(id, datos)
    PRepo-->>SVC: perfil actualizado/creado
    SVC-->>API: perfil + fue_creado
    API-->>Cliente: 200/201 Perfil actualizado/creado
```

## 3) Cambiar estado de usuario (`PATCH /api/v1/users/{usuario_id}/state`)

```mermaid
sequenceDiagram
    actor Cliente
    participant API as Router Usuarios
    participant Auth as ms-autenticacion/ms-permisos
    participant HSVC as historial_service
    participant URepo as usuario_repository
    participant HRepo as historial_repository
    participant Notif as ms-notificaciones

    Cliente->>API: PATCH /users/{id}/state
    API->>Auth: validar_sesion_activa()
    Auth-->>API: sesión válida
    API->>Auth: validar_permiso(USR_CHANGE_STATE)
    Auth-->>API: permitido
    API->>HSVC: cambiar_estado(id, nuevo_estado, motivo, user_id)
    HSVC->>URepo: obtener_por_id(id)
    URepo-->>HSVC: usuario actual
    HSVC->>URepo: cambiar_estado_transaccional(...)
    HSVC->>HRepo: registrar_cambio_transaccional(...)
    HSVC-->>API: estado actualizado
    API->>Notif: notificar_async(user_state_change)
    API-->>Cliente: 200 Estado actualizado
```
