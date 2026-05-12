# Diagrama de base de datos — Microservicio de Usuarios

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

    usr_usuarios ||--o| usr_perfiles : "tiene perfil"
    usr_tipos_documento ||--o{ usr_perfiles : "clasifica"
    usr_usuarios ||--o| usr_preferencias_notificacion : "tiene preferencias"
    usr_usuarios ||--o{ usr_historial_estados : "genera historial"
```

## Restricciones observables en SQL

- `usr_usuarios.estado` limitado por `chk_usuario_estado`: `activo`, `inactivo`, `suspendido`, `eliminado`.
- `usr_perfiles.genero` limitado por `chk_perfil_genero`.
- `usr_historial_estados.estado_nuevo` limitado por `chk_historial_estado`.
- `usr_preferencias_notificacion.canal_preferido` limitado por `chk_pref_canal`: `email`, `sms`, `push`.
- El SQL define los valores permitidos de estado, pero no documenta semántica de negocio detallada para diferenciar cada estado.
