# Diagramas actualizados — Microservicio de Usuarios (ms-usuarios [USR])

Documento reconstruido a partir de:
- `documentacion/software_architecture_document_ms_usuarios.md`
- `Documentos de desarrollo/ms-usuarios_requisitos_funcionales_detallados.md`
- Implementación real en `ms_usuario/`.

## 1) Diagrama de clases (lógico de implementación)

```mermaid
classDiagram

class MainApp {
  +include_router(router)
  +health_check()
  +health_check_v1()
}

class UsuariosRouter
class PerfilesRouter
class HistorialRouter
class PreferenciasRouter
class TiposDocumentoRouter
class InternalAuthRouter

class UsuarioService
class PerfilService
class HistorialService
class PreferenciasService
class TipoDocumentoService

class UsuarioRepository
class PerfilRepository
class HistorialRepository
class PreferenciasRepository
class TipoDocumentoRepository

class UsuarioCrear
class UsuarioActualizar
class CambiarPassword
class CambiarEstadoBody
class UsuarioRespuesta
class PerfilCrearActualizar
class PerfilRespuesta
class PreferenciasActualizar
class PreferenciasRespuesta
class TipoDocumentoRespuesta
class RespuestaEstandar

class InterService
class Crypto
class Audit
class RequestId
class Database

MainApp --> UsuariosRouter
MainApp --> PerfilesRouter
MainApp --> HistorialRouter
MainApp --> PreferenciasRouter
MainApp --> TiposDocumentoRouter
MainApp --> InternalAuthRouter

UsuariosRouter --> UsuarioService
UsuariosRouter --> HistorialService
UsuariosRouter --> UsuarioCrear
UsuariosRouter --> UsuarioActualizar
UsuariosRouter --> CambiarPassword
UsuariosRouter --> CambiarEstadoBody
UsuariosRouter --> UsuarioRespuesta
UsuariosRouter --> RespuestaEstandar

PerfilesRouter --> PerfilService
PerfilesRouter --> PerfilCrearActualizar
PerfilesRouter --> PerfilRespuesta
PerfilesRouter --> RespuestaEstandar

HistorialRouter --> HistorialService
HistorialRouter --> RespuestaEstandar

PreferenciasRouter --> PreferenciasService
PreferenciasRouter --> PreferenciasActualizar
PreferenciasRouter --> PreferenciasRespuesta
PreferenciasRouter --> RespuestaEstandar

TiposDocumentoRouter --> TipoDocumentoService
TiposDocumentoRouter --> TipoDocumentoRespuesta
TiposDocumentoRouter --> RespuestaEstandar

InternalAuthRouter --> UsuarioService

UsuarioService --> UsuarioRepository
UsuarioService --> InterService
UsuarioService --> Crypto

PerfilService --> PerfilRepository
PerfilService --> UsuarioRepository
PerfilService --> TipoDocumentoRepository

HistorialService --> UsuarioRepository
HistorialService --> HistorialRepository
HistorialService --> Database

PreferenciasService --> PreferenciasRepository
PreferenciasService --> UsuarioRepository

TipoDocumentoService --> TipoDocumentoRepository

UsuariosRouter --> InterService
UsuariosRouter --> Audit
UsuariosRouter --> RequestId
PerfilesRouter --> InterService
PreferenciasRouter --> InterService

UsuarioRepository --> Database
PerfilRepository --> Database
HistorialRepository --> Database
PreferenciasRepository --> Database
TipoDocumentoRepository --> Database
```

## 2) Diagrama de base de datos (ER)

```mermaid
erDiagram
    usr_tipos_documento {
        int id PK
        string codigo UK
        string nombre
        string descripcion
        boolean activo
        timestamp created_at
        timestamp updated_at
    }

    usr_usuarios {
        int id PK
        string username UK
        string email UK
        string password_hash
        string estado
        int rol_id
        timestamp created_at
        timestamp updated_at
    }

    usr_perfiles {
        int id PK
        int usuario_id UK, FK
        int tipo_documento_id FK
        string numero_documento UK
        string primer_nombre
        string segundo_nombre
        string primer_apellido
        string segundo_apellido
        date fecha_nacimiento
        string genero
        string direccion_residencia
        string ciudad
        string departamento
        string telefono_fijo
        string telefono_movil
        string contacto_emergencia_nombre
        string contacto_emergencia_telefono
        string biografia
        timestamp created_at
        timestamp updated_at
    }

    usr_preferencias_notificacion {
        int id PK
        int usuario_id UK, FK
        boolean notif_email
        boolean notif_sms
        boolean notif_push
        string canal_preferido
        time horario_no_molestar_inicio
        time horario_no_molestar_fin
        timestamp created_at
        timestamp updated_at
    }

    usr_historial_estados {
        int id PK
        int usuario_id FK
        string estado_anterior
        string estado_nuevo
        string motivo
        int usuario_modificador_id
        timestamp created_at
    }

    usr_usuarios ||--o| usr_perfiles : "tiene"
    usr_tipos_documento ||--o{ usr_perfiles : "clasifica"
    usr_usuarios ||--o| usr_preferencias_notificacion : "configura"
    usr_usuarios ||--o{ usr_historial_estados : "registra"
```

## 3) Diagramas de flujo

### 3.1 Flujo transversal de seguridad (USR-RF-001, USR-RF-002, USR-RF-003)

```mermaid
flowchart TD
    A[Request HTTP] --> B[obtener_o_generar X-Request-ID]
    B --> C{Token interno valido?}
    C -- Si --> G[Continuar operacion]
    C -- No --> D[validar_sesion_activa en ms-autenticacion]
    D --> E[validar_permiso en ms-roles]
    E --> G[Continuar operacion]
    G --> H[registrar_log_async]
    H --> I[RespuestaEstandar]
```

### 3.2 Flujo de creación de usuario (USR-RF-006)

```mermaid
flowchart TD
    A[POST /api/v1/users] --> B[Validar sesion y permiso USR_CREATE]
    B --> C[Validar unicidad username/email]
    C --> D[Validar rol en ms-roles]
    D --> E{Password fuente}
    E -- DEBUG --> F[Usar password_plana]
    E -- Normal --> G[Descifrar password_encrypted AES-256]
    F --> H[Hash bcrypt]
    G --> H[Hash bcrypt]
    H --> I[Insert en usr_usuarios]
    I --> J[Notificar user_welcome]
    J --> K[Auditoria async]
    K --> L[201 Usuario creado]
```

### 3.3 Flujo de cambio de estado transaccional (USR-RF-015)

```mermaid
flowchart TD
    A[PATCH /users/{id}/state] --> B[Validar sesion y permiso USR_CHANGE_STATE]
    B --> C[Validar estado y motivo]
    C --> D[Obtener usuario actual]
    D --> E{Existe y cambia estado?}
    E -- No --> X[Error 4xx]
    E -- Si --> F[BEGIN]
    F --> G[UPDATE usr_usuarios.estado]
    G --> H[INSERT usr_historial_estados]
    H --> I[COMMIT]
    I --> J[Notificar user_state_change]
    J --> K[Auditoria async]
    K --> L[200 Estado actualizado]
```

## 4) Diagramas de secuencia

### 4.1 Crear usuario (`POST /api/v1/users`)

```mermaid
sequenceDiagram
    actor Cliente
    participant API as routes/usuarios.py
    participant AUTH as ms-autenticacion
    participant ROL as ms-roles
    participant SVC as usuario_service
    participant CR as utils/crypto
    participant URepo as usuario_repository
    participant NOT as ms-notificaciones
    participant AUD as ms-auditoria

    Cliente->>API: POST /api/v1/users
    API->>AUTH: validar_sesion_activa()
    AUTH-->>API: sesion valida
    API->>ROL: validar_permiso(USR_CREATE)
    ROL-->>API: autorizado
    API->>SVC: crear_usuario(...)
    SVC->>ROL: validar_rol_externo(rol_id)
    ROL-->>SVC: rol valido
    SVC->>CR: descifrar_aes256(password_encrypted)
    CR-->>SVC: password_plano
    SVC->>CR: hashear_bcrypt(password)
    CR-->>SVC: password_hash
    SVC->>URepo: crear(username,email,hash,rol)
    URepo-->>SVC: usuario creado
    SVC-->>API: usuario
    API->>NOT: notificar_async(user_welcome)
    API->>AUD: registrar_log_async(...)
    API-->>Cliente: 201 + RespuestaEstandar
```

### 4.2 Cambio de estado con historial (`PATCH /users/{id}/state`)

```mermaid
sequenceDiagram
    actor Cliente
    participant API as routes/usuarios.py
    participant AUTH as ms-autenticacion
    participant ROL as ms-roles
    participant HSVC as historial_service
    participant URepo as usuario_repository
    participant HRepo as historial_repository
    participant DB as PostgreSQL
    participant NOT as ms-notificaciones

    Cliente->>API: PATCH /users/{id}/state
    API->>AUTH: validar_sesion_activa()
    AUTH-->>API: sesion valida
    API->>ROL: validar_permiso(USR_CHANGE_STATE)
    ROL-->>API: autorizado
    API->>HSVC: cambiar_estado(id, estado, motivo, user_id)
    HSVC->>URepo: obtener_por_id(id)
    URepo-->>HSVC: usuario actual
    HSVC->>DB: BEGIN
    HSVC->>URepo: cambiar_estado_transaccional(conn,...)
    URepo->>DB: UPDATE usr_usuarios
    HSVC->>HRepo: registrar_cambio_transaccional(conn,...)
    HRepo->>DB: INSERT usr_historial_estados
    HSVC->>DB: COMMIT
    HSVC-->>API: OK
    API->>NOT: notificar_async(user_state_change)
    API-->>Cliente: 200 + RespuestaEstandar
```

### 4.3 Verificación interna de credenciales (`POST /internal/users/credentials/verify`)

```mermaid
sequenceDiagram
    participant AUTH as ms-autenticacion
    participant API as routes/internal_auth.py
    participant SVC as usuario_service
    participant URepo as usuario_repository
    participant CR as utils/crypto

    AUTH->>API: POST /internal/users/credentials/verify
    API->>SVC: verificar_credenciales_internas(username, encrypted_password)
    SVC->>URepo: obtener_por_username_con_hash(username)
    URepo-->>SVC: usuario + password_hash + estado
    SVC->>CR: descifrar_aes256(password)
    CR-->>SVC: password_plano
    SVC->>CR: verificar_bcrypt(password_plano, hash)
    CR-->>SVC: true/false
    SVC-->>API: {user_id,status} o INVALID_CREDENTIALS
    API-->>AUTH: 200 / 401 / 423
```

## 5) Cobertura de requisitos trazada en diagramas

- **Transversales:** USR-RF-001, 002, 003, 004, 005.
- **Usuarios:** USR-RF-006, 007, 008, 010, 011, 012, 020, 021, 022, 023, 024.
- **Perfiles:** USR-RF-013, 014.
- **Historial:** USR-RF-015, 016.
- **Catálogo:** USR-RF-017.
- **Preferencias:** USR-RF-018, 019.
