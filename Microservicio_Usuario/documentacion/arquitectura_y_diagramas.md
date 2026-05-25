# 🏛️ Arquitectura y Diagramas - MS-Usuarios

## Diagrama de Arquitectura Completa

```mermaid
graph TB
    subgraph "API Gateway & Cliente"
        CLIENT["👤 Cliente HTTP<br/>FastAPI Swagger UI"]
    end

    subgraph "Microservicio de Usuarios"
        MAIN["🚀 main.py<br/>FastAPI Application"]
        
        subgraph "ROUTES"
            R1["usuarios.py<br/>13 endpoints"]
            R2["perfiles.py<br/>2 endpoints"]
            R3["historial.py<br/>1 endpoint"]
            R4["preferencias.py<br/>2 endpoints"]
            R5["tipos_documento.py<br/>1 endpoint"]
        end

        subgraph "SERVICES"
            S1["usuario_service<br/>Business Logic"]
            S2["perfil_service"]
            S3["historial_service"]
            S4["preferencias_service"]
            S5["tipo_documento_service"]
        end

        subgraph "REPOSITORY"
            REP1["usuario_repository<br/>BD Queries"]
            REP2["perfil_repository"]
            REP3["historial_repository"]
            REP4["preferencias_repository"]
            REP5["tipo_documento_repository"]
        end

        subgraph "UTILITIES"
            U1["crypto.py<br/>AES-256 + bcrypt"]
            U2["request_id.py<br/>ID único"]
            U3["audit.py<br/>Logging"]
            U4["inter_service.py<br/>Comunicación"]
        end

        subgraph "DATABASE"
            DB["🐘 PostgreSQL<br/>5 tablas"]
            DB1["usr_usuarios"]
            DB2["usr_perfiles"]
            DB3["usr_historial_estados"]
            DB4["usr_preferencias"]
            DB5["usr_tipos_documento"]
        end
    end

    subgraph "Microservicios Externos"
        AUTH["🔐 ms-autenticacion<br/>:8001"]
        ROLES["👥 ms-roles<br/>:8002"]
        NOTIF["📧 ms-notificaciones<br/>:8003"]
        AUDIT["📋 ms-auditoria<br/>:8004"]
    end

    CLIENT -->|"HTTP Request"| MAIN
    MAIN --> R1 & R2 & R3 & R4 & R5
    
    R1 --> S1 & S3 & U1 & U2 & U3 & U4
    R2 --> S2
    R3 --> S3
    R4 --> S4
    R5 --> S5
    
    S1 & S2 & S3 & S4 & S5 --> REP1 & REP2 & REP3 & REP4 & REP5
    
    REP1 & REP2 & REP3 & REP4 & REP5 --> DB
    DB --> DB1 & DB2 & DB3 & DB4 & DB5
    
    U4 -->|"validar_sesion"| AUTH
    U4 -->|"validar_permiso"| ROLES
    U4 -->|"notificar_async"| NOTIF
    U3 -->|"registrar_log"| AUDIT
    
    MAIN -->|"HTTP Response"| CLIENT

    style MAIN fill:#4CAF50,color:#fff
    style DB fill:#FF9800,color:#fff
    style AUTH fill:#2196F3,color:#fff
    style ROLES fill:#2196F3,color:#fff
    style NOTIF fill:#2196F3,color:#fff
    style AUDIT fill:#2196F3,color:#fff
```

---

## Flujo de Solicitud - Crear Usuario

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant Routes
    participant Services
    participant Crypto
    participant Repository
    participant PostgreSQL
    participant InterService
    participant MSAuth
    participant MSAudit

    Client->>FastAPI: POST /users + auth header
    FastAPI->>Routes: request dispatcher
    Routes->>InterService: validar_sesion_activa()
    InterService->>MSAuth: GET /validar-sesion
    MSAuth-->>InterService: sesion válida
    Routes->>InterService: validar_permiso(rol_id, USR_CREATE)
    InterService->>MSAuth: GET /validar-permiso
    MSAuth-->>InterService: permiso válido
    Routes->>Crypto: descifrar_aes256(password_encrypted)
    Crypto-->>Routes: password_descifrada
    Routes->>Crypto: hash_bcrypt(password)
    Crypto-->>Routes: password_hash
    Routes->>Services: crear_usuario()
    Services->>Repository: crear()
    Repository->>PostgreSQL: INSERT usr_usuarios
    PostgreSQL-->>Repository: usuario_creado
    Repository-->>Services: usuario_dict
    Services-->>Routes: usuario, error=None
    Routes->>InterService: notificar_async(user_welcome)
    Routes->>InterService: registrar_log_async()
    InterService->>MSAudit: POST /registrar-log
    MSAudit-->>InterService: ok
    Routes-->>FastAPI: 201 Created + RespuestaEstandar
    FastAPI-->>Client: JSON response

```

---

## Flujo de Solicitud - Cambiar Estado (Transaccional)

```mermaid
sequenceDiagram
    participant Client
    participant Routes as Routes
    participant HistorialService as Historial Service
    participant UserRepository as Usuario Repository
    participant HistorialRepository as Historial Repository
    participant PostgreSQL
    participant Audit

    Client->>Routes: PATCH /users/{id}/state
    Routes->>Routes: validar_sesion_activa()
    Routes->>Routes: validar_permiso(USR_CHANGE_STATE)
    
    rect rgb(200, 220, 255)
    note right of Routes: Transacción Atómica
    Routes->>HistorialService: cambiar_estado()
    HistorialService->>PostgreSQL: BEGIN TRANSACTION
    HistorialService->>UserRepository: cambiar_estado_transaccional()
    UserRepository->>PostgreSQL: UPDATE usr_usuarios SET estado=...
    PostgreSQL-->>UserRepository: 1 row updated
    HistorialService->>HistorialRepository: registrar_cambio_transaccional()
    HistorialRepository->>PostgreSQL: INSERT usr_historial_estados
    PostgreSQL-->>HistorialRepository: id, estado_anterior, ...
    HistorialService->>PostgreSQL: COMMIT TRANSACTION
    end

    HistorialService-->>Routes: usuario, error=None
    Routes->>Audit: notificar_async(user_state_change)
    Routes->>Audit: registrar_log_async()
    Routes-->>Client: 200 OK

```

---

## Diagrama de Flujo - Búsqueda Avanzada

```mermaid
flowchart TD
    A["GET /users?nombre=&ciudad=&pagina=1"] -->|"Validar parámetros"| B{Validaciones}
    B -->|"pagina < 1"| C["❌ 400 Bad Request"]
    B -->|"items_por_pagina > 100"| D["❌ 400 Bad Request"]
    B -->|"OK"| E["usuario_service.busqueda_avanzada()"]
    E -->|"Construir SQL"| F["SELECT u.*, p.*<br/>FROM usr_usuarios u<br/>LEFT JOIN usr_perfiles p"]
    F -->|"Condiciones dinámicas"| G{Agregar WHERE}
    G -->|"nombre"| G1["p.primer_nombre ILIKE %nombre%"]
    G -->|"numero_documento"| G2["p.numero_documento = %num%"]
    G -->|"ciudad"| G3["p.ciudad = %ciudad%"]
    G -->|"estado"| G4["u.estado = %estado%"]
    G1 & G2 & G3 & G4 -->|"Combinar"| H["Query SQL final"]
    H -->|"Contar registros"| I["SELECT COUNT(*) total"]
    I -->|"Aplicar OFFSET"| J["OFFSET (pagina-1)*items"]
    J -->|"Aplicar LIMIT"| K["LIMIT items_por_pagina"]
    K -->|"Ejecutar"| L["PostgreSQL"]
    L -->|"Retornar"| M["list[dict]"]
    M -->|"Construir respuesta"| N["ResultadoPaginado"]
    N -->|"Retornar"| O["✅ 200 OK + datos"]

    style A fill:#4CAF50
    style C fill:#f44336
    style D fill:#f44336
    style O fill:#4CAF50

```

---

## Capas de Arquitectura

```mermaid
graph TB
    subgraph PRESENTACION["📱 CAPA DE PRESENTACIÓN"]
        HTTP["HTTP Requests"]
        SWAGGER["Swagger UI"]
    end

    subgraph ROUTES["🚦 CAPA DE RUTAS"]
        R1["POST /users"]
        R2["GET /users/{id}"]
        R3["PATCH /users/{id}/state"]
        R4["PUT /users/{id}/profile"]
    end

    subgraph SERVICES["🔧 CAPA DE SERVICIOS"]
        VALID["Validaciones"]
        ENCRYPT["Encriptación"]
        LOGIC["Lógica de negocio"]
        TRANS["Transacciones"]
    end

    subgraph REPOSITORY["📊 CAPA DE REPOSITORIO"]
        QUERY["SQL Queries"]
        CURSOR["Cursor Management"]
        ERROR["Error Handling"]
    end

    subgraph DATABASE["🐘 CAPA DE DATOS"]
        PG["PostgreSQL 12+"]
        TABLES["5 Tablas normalizadas"]
        INDEXES["Índices optimizados"]
    end

    PRESENTACION --> ROUTES
    ROUTES -->|"Request validation"| SERVICES
    SERVICES -->|"Business logic"| REPOSITORY
    REPOSITORY -->|"SQL execution"| DATABASE
    DATABASE -->|"Data persistence"| PG

    style PRESENTACION fill:#E3F2FD
    style ROUTES fill:#F3E5F5
    style SERVICES fill:#FFF3E0
    style REPOSITORY fill:#F1F8E9
    style DATABASE fill:#FCE4EC

```

---

## Flujo de Autenticación y Autorización

```mermaid
graph TB
    A["Request con Authorization header"] -->|"Extraer Bearer Token"| B["inter_service.validar_sesion_activa()"]
    B -->|"Call async"| C["GET ms-autenticacion/validar-sesion"]
    C -->|"Timeout: 3s"| D{¿Sesión válida?}
    D -->|"NO"| E["❌ 401 Unauthorized"]
    D -->|"SÍ"| F["✅ Retorna sesion dict<br/>user_id, rol_id, etc"]
    F -->|"Siguiente validación"| G["inter_service.validar_permiso()"]
    G -->|"Call async"| H["GET ms-roles/validar-permiso?<br/>rol_id=X&permiso=Y"]
    H -->|"Timeout: 3s"| I{¿Permiso válido?}
    I -->|"NO"| J["❌ 403 Forbidden"]
    I -->|"SÍ"| K["✅ Proceder con endpoint"]
    K -->|"Ejecutar lógica"| L["Business Logic"]
    L -->|"Ejecutada"| M["✅ 200/201 Response"]

    style E fill:#f44336,color:#fff
    style J fill:#f44336,color:#fff
    style K fill:#4CAF50,color:#fff
    style M fill:#4CAF50,color:#fff

```

---

## Flujo de Cifrado y Desencriptado

```mermaid
graph LR
    subgraph "CLIENT SIDE (Frontend)"
        PLAIN["Contraseña en texto<br/>user123"]
        AES["AES-256-CBC<br/>Encrypt"]
        B64["Base64 Encode"]
        ENCRYPTED["eyJhbGciOi...<br/>base64_cipher"]
    end

    subgraph "SERVER SIDE (Backend)"
        RECV["Recibir<br/>password_encrypted"]
        B64D["Base64 Decode"]
        AESD["AES-256-CBC<br/>Decrypt"]
        PLAIN2["Contraseña descifrada"]
        BCRYPT["bcrypt Hash<br/>cost factor 12"]
        HASH["$2b$12$...<br/>password_hash"]
        STORE["Almacenar en BD"]
    end

    PLAIN -->|"User types password"| AES
    AES -->|"IV + Ciphertext"| B64
    B64 -->|"Base64 encode"| ENCRYPTED
    ENCRYPTED -->|"HTTP POST"| RECV
    RECV -->|"Request body"| B64D
    B64D -->|"Decode"| AESD
    AESD -->|"AES_SECRET_KEY from .env"| PLAIN2
    PLAIN2 -->|"Hash"| BCRYPT
    BCRYPT -->|"Cost: 12"| HASH
    HASH -->|"INSERT"| STORE

    style ENCRYPTED fill:#2196F3,color:#fff
    style HASH fill:#4CAF50,color:#fff

```

---

## Estados del Usuario - Diagrama de Transiciones

```mermaid
stateDiagram-v2
    [*] --> ACTIVO: Crear usuario
    
    ACTIVO --> INACTIVO: DELETE /users/{id}<br/>PATCH /state → inactivo
    ACTIVO --> SUSPENDIDO: PATCH /state → suspendido<br/>Violación de política
    ACTIVO --> ELIMINADO: PATCH /state → eliminado<br/>Solicitud usuario
    
    INACTIVO --> ACTIVO: POST /reactivate<br/>Cambiar estado
    INACTIVO --> ELIMINADO: PATCH /state → eliminado
    
    SUSPENDIDO --> ACTIVO: POST /reactivate<br/>Apelación aprobada
    SUSPENDIDO --> ELIMINADO: PATCH /state → eliminado
    
    ELIMINADO --> [*]

    note right of ACTIVO
        Usuario funcional
        Puede autenticarse
        Puede hacer operaciones
    end

    note right of INACTIVO
        Usuario desactivado
        No puede autenticarse
        Sin operaciones
    end

    note right of SUSPENDIDO
        Usuario suspendido
        No puede autenticarse
        En revisión/apelación
    end

    note right of ELIMINADO
        Usuario eliminado (soft delete)
        No puede autenticarse
        Datos conservados
    end

```

---

## Integración con Otros Microservicios

```mermaid
graph TB
    subgraph "MS-Usuarios (Este Microservicio)"
        APP["FastAPI Application"]
    end

    subgraph "MS-Autenticacion"
        AUTH["Servicio de Autenticación<br/>:8001"]
        AUTHDB["Usuario + password_hash"]
    end

    subgraph "MS-Roles"
        ROLES["Servicio de Roles<br/>:8002"]
        ROLESDB["Roles + Permisos"]
    end

    subgraph "MS-Notificaciones"
        NOTIF["Servicio de Notificaciones<br/>:8003"]
        QUEUE["Cola de eventos"]
    end

    subgraph "MS-Auditoria"
        AUDIT["Servicio de Auditoría<br/>:8004"]
        AUDITDB["Log de operaciones"]
    end

    APP -->|"1. validar_sesion_activa()"| AUTH
    APP -->|"2. validar_permiso()"| ROLES
    APP -->|"3. obtener_por_email_con_hash()<br/>[AUTH ONLY]"| AUTH
    APP -->|"4. notificar_async()"| NOTIF
    APP -->|"5. registrar_log_async()"| AUDIT

    AUTH --> AUTHDB
    ROLES --> ROLESDB
    NOTIF --> QUEUE
    AUDIT --> AUDITDB

    style APP fill:#4CAF50,color:#fff
    style AUTH fill:#2196F3,color:#fff
    style ROLES fill:#2196F3,color:#fff
    style NOTIF fill:#2196F3,color:#fff
    style AUDIT fill:#2196F3,color:#fff

```

---

## Flujo de Validación de Datos - Perfil

```mermaid
flowchart TD
    A["PUT /users/{id}/profile"] -->|"Payload JSON"| B["PerfilCrearActualizar"]
    B -->|"Pydantic Validation"| C{¿Validaciones básicas?}
    C -->|"type check"| D["Email, strings, etc"]
    C -->|"campo_requerido"| E["Checar required fields"]
    C -->|"minLength"| F["Checar longitudes mínimas"]
    
    D & E & F -->|"OK"| G{Validators personalizados}
    G -->|"fecha_nacimiento"| H{Edad ≥ 14 años?}
    H -->|"< 14"| I["❌ Rechazar: menor de edad"]
    H -->|"≥ 14"| J["✅ OK"]
    G -->|"genero"| K{Valor en enum?}
    K -->|"NO"| L["❌ Rechazar: género inválido"]
    K -->|"SÍ"| M["✅ OK"]
    
    I & L -->|"Error"| N["400 Bad Request"]
    J & M -->|"Success"| O["Continuar con lógica"]
    O -->|"Repository"| P["Upsert en BD"]
    P -->|"Insertar o actualizar"| Q["Validaciones BD"]
    Q -->|"Unique: numero_documento"| R{¿Único?}
    R -->|"Duplicado"| S["❌ 409 Conflict"]
    R -->|"Único"| T["✅ Insertar/Actualizar"]
    T -->|"Success"| U["201 Created o 200 OK"]

    style N fill:#f44336,color:#fff
    style S fill:#f44336,color:#fff
    style U fill:#4CAF50,color:#fff

```

---

## Modelo de Paginación

```mermaid
graph TB
    A["GET /users?pagina=2&items_por_pagina=10"] -->|"Parámetros"| B["pagina: 2<br/>items_por_pagina: 10"]
    B -->|"Validar"| C{¿Rango válido?}
    C -->|"pagina < 1"| D["❌ 400"]
    C -->|"items > 100"| E["❌ 400"]
    C -->|"OK"| F["Calcular OFFSET"]
    F -->|"Formula: (pagina-1)*items"| G["OFFSET = 1 * 10 = 10"]
    G -->|"SQL"| H["SELECT * FROM usuarios<br/>OFFSET 10 LIMIT 10"]
    H -->|"Execute"| I["Registros 11-20"]
    I -->|"Count total"| J["SELECT COUNT(*) = 150"]
    J -->|"Calcular páginas"| K["total_paginas = 150/10 = 15"]
    K -->|"Construir respuesta"| L["ResultadoPaginado<br/>pagina_actual: 2<br/>total_registros: 150<br/>total_paginas: 15<br/>resultados: [...]"]
    L -->|"Response"| M["✅ 200 OK"]

    style M fill:#4CAF50,color:#fff

```

---

## Arquitectura de Carpetas - Detallada

```
ms_usuario/
├── Microservicio_Usuario/
│   ├── main.py                          # Punto de entrada, instancia de FastAPI
│   ├── config.py                        # Variables de configuración centralizadas
│   ├── database.py                      # Pool de conexiones PostgreSQL
│   ├── requirements.txt                 # Dependencias Python
│   │
│   ├── models/                          # Modelos Pydantic (validación de datos)
│   │   ├── __init__.py
│   │   ├── usuario.py                   # DTOs: UsuarioCrear, UsuarioActualizar, UsuarioRespuesta
│   │   ├── perfil.py                    # DTOs: PerfilCrearActualizar, PerfilRespuesta
│   │   ├── historial_estado.py          # DTO: HistorialRespuesta
│   │   ├── preferencias_notificacion.py # DTOs: PreferenciasActualizar, PreferenciasRespuesta
│   │   ├── tipo_documento.py            # DTO: TipoDocumentoRespuesta
│   │   └── response.py                  # RespuestaEstandar (envelope)
│   │
│   ├── routes/                          # Endpoints FastAPI (capa de presentación)
│   │   ├── __init__.py
│   │   ├── usuarios.py                  # 13 endpoints de usuarios
│   │   ├── perfiles.py                  # 2 endpoints de perfiles
│   │   ├── historial.py                 # 1 endpoint de historial
│   │   ├── preferencias.py              # 2 endpoints de preferencias
│   │   └── tipos_documento.py           # 1 endpoint de tipos de documento
│   │
│   ├── services/                        # Lógica de negocio (capa de aplicación)
│   │   ├── __init__.py
│   │   ├── usuario_service.py           # Crear, actualizar, buscar usuarios
│   │   ├── perfil_service.py            # Gestionar perfiles
│   │   ├── historial_service.py         # Cambios de estado con historial
│   │   ├── preferencias_service.py      # Gestionar notificaciones
│   │   └── tipo_documento_service.py    # Listar tipos de documento
│   │
│   ├── repository/                      # Acceso a datos (capa de persistencia)
│   │   ├── __init__.py
│   │   ├── usuario_repository.py        # Queries: crear, obtener, actualizar usuarios
│   │   ├── perfil_repository.py         # Queries: CRUD de perfiles
│   │   ├── historial_repository.py      # Queries: registrar cambios de estado
│   │   ├── preferencias_repository.py   # Queries: CRUD de preferencias
│   │   └── tipo_documento_repository.py # Queries: listar tipos
│   │
│   ├── utils/                           # Utilidades y funciones auxiliares
│   │   ├── __init__.py
│   │   ├── crypto.py                    # AES-256 (encrypt/decrypt) + bcrypt (hash)
│   │   ├── request_id.py                # Generación de Request IDs únicos
│   │   ├── audit.py                     # Logging asincrónico a ms-auditoria
│   │   └── inter_service.py             # Comunicación con otros microservicios
│   │
│   └── .env                             # Variables de entorno (crear con ms_usuario/init_db.sql)
│
├── documentacion/                       # Documentación técnica
│   ├── README.md                        # Índice y descripción general
│   ├── modelo_relacional.md             # Diagrama ER y descripción de tablas
│   ├── rutas_y_endpoints.md             # API Reference completa
│   ├── arquitectura_y_diagramas.md      # Este archivo
│   ├── diagramas/                       # Diagramas técnicos adicionales
│   ├── requisitos/                      # Especificación de requisitos
│   └── desarrollo/                      # Documentos de desarrollo funcional y datos

```

---

## Métricas de Rendimiento Esperadas

| Operación | Tiempo Promedio | Condiciones |
|-----------|-----------------|-------------|
| Crear usuario | 150-200ms | Validación + hash bcrypt |
| Obtener por ID | 5-10ms | Con índice en id |
| Búsqueda avanzada | 50-100ms | Con 1000 registros, paginación 10 |
| Cambiar estado | 100-150ms | Transacción + historial |
| Buscar por email | 10-15ms | Con índice en email |

> **Nota:** Tiempos incluyen validación, procesamiento y respuesta HTTP

---

## Checklist de Deployment

- [ ] Base de datos PostgreSQL creada
    - [ ] Tablas e índices creados (ms_usuario/init_db.sql)
- [ ] `.env` configurado con valores reales
- [ ] `AES_SECRET_KEY` generado (64 caracteres hex)
- [ ] Tokens de servicios externos configurados
- [ ] URLs de microservicios validadas
- [ ] Timeouts ajustados según red
- [ ] CORS configurado si es necesario
- [ ] Logs centralizados configurados
- [ ] Backups de BD programados
- [ ] Monitoreo de performance activo
