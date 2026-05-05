# 🔗 Guía de Conexión - Usuario & Autenticación

## ✅ Cambios Realizados

### 1. **Red Docker Global Creada**
```bash
docker network create microservicios-network
```

### 2. **Microservicio_Usuario/docker-compose.yml**
- ✅ URLs actualizadas a puerto interno 8000:
  - `AUTH_SERVICE_URL: http://ms-autenticacion:8000`
  - `ROL_SERVICE_URL: http://ms-roles:8000`
  - etc...
- ✅ Red cambiada a externa:
  ```yaml
  networks:
    ms_network:
      external: true
      name: microservicios-network
  ```

### 3. **Microservicio_Autenticacion/docker-compose.yml**
- ✅ Agregada red a ambos servicios (postgres y auth)
- ✅ Agregada URL de Usuarios: `USERS_SERVICE_URL: http://ms-usuarios-app:8000`
- ✅ Red definida como externa:
  ```yaml
  networks:
    microservicios-network:
      external: true
  ```

### 4. **Microservicio_Usuario/config.py**
- ✅ URLs consistentes en puerto 8000

---

## 🚀 Cómo Ejecutarlos

### Opción 1: Cada uno en su directorio (RECOMENDADO)

**Terminal 1 - Usuario:**
```powershell
cd \Microservicio_Usuario
docker-compose up -d
```

**Terminal 2 - Autenticación:**
```powershell
cd \Microservicio_Autenticacion\Autenticacion
docker-compose up -d
```

### Opción 2: Ambos desde la raíz

```powershell
# Usuario
docker-compose -f Microservicio_Usuario/docker-compose.yml up -d

# Autenticación
docker-compose -f Microservicio_Autenticacion/Autenticacion/docker-compose.yml up -d
```

---

## ✅ Verificar que están conectados

### Ver que están en la misma red
```powershell
docker network inspect microservicios-network
```

Deberías ver:
```json
{
    "Containers": {
        "...": {"Name": "ms_usuarios_db", ...},
        "...": {"Name": "ms_usuarios_app", ...},
        "...": {"Name": "ms-autenticacion-postgres", ...},
        "...": {"Name": "ms-autenticacion", ...}
    }
}
```

### Ver estado de todos los contenedores
```powershell
docker ps
```

```
CONTAINER ID   NAMES                          STATUS     PORTS
abc123...      ms_usuarios_db                 Up...      5432->5432/tcp
def456...      ms_usuarios_app                Up...      8000->8000/tcp
ghi789...      ms-autenticacion-postgres      Up...      
jkl012...      ms-autenticacion               Up...      8002->8000/tcp
```

### Testing de conectividad
```powershell
# Desde Usuario, preguntarle a Autenticación
docker exec ms_usuarios_app curl http://ms-autenticacion:8000/health

# Deberías obtener respuesta JSON
```

---

## 📍 Puertos Disponibles

| Servicio | Host | Interno | URL Interna |
|----------|------|---------|-------------|
| **Usuarios App** | 8000 | 8000 | http://ms-usuarios-app:8000 |
| **Usuarios BD** | - | 5432 | postgres://localhost:5432 |
| **Auth App** | 8002 | 8000 | http://ms-autenticacion:8000 |
| **Auth BD** | - | 5432 | postgres://localhost:5432 |

---

## 🔄 Flujo de Comunicación

```
┌─────────────────────────────────────────────────┐
│   Docker Network: microservicios-network        │
├─────────────────────────────────────────────────┤
│                                                 │
│  Dir 1: Microservicio_Usuario                   │
│  ├─ ms_usuarios_db (postgres 15)               │
│  └─ ms_usuarios_app ──→ http://ms-autenticacion:8000
│                                                 │
│  Dir 2: Microservicio_Autenticacion             │
│  ├─ ms-autenticacion-postgres (postgres 16)    │
│  └─ ms-autenticacion ←──────────────────┘      │
│                                                 │
└─────────────────────────────────────────────────┘
        ↑
      Host
   localhost:8000  (usuarios)
   localhost:8002  (autenticación)
```

---

## 🛑 Para Detener

```powershell
# Usuario
cd Microservicio_Usuario
docker-compose down

# Autenticación
cd Microservicio_Autenticacion\Autenticacion
docker-compose down

# O eliminar todo (incluyendo datos)
docker-compose down -v
```

---

## 📊 Resumen de Cambios

| Archivo | Cambio |
|---------|--------|
| `Microservicio_Usuario/docker-compose.yml` | Red externa + URLs puerto 8000 |
| `Microservicio_Autenticacion/docker-compose.yml` | Red externa + USERS_SERVICE_URL |
| `Microservicio_Usuario/config.py` | URLs consistentes puerto 8000 |

---

## ✨ Resultado Final

✅ Ambos servicios en **red Docker compartida**  
✅ Se comunican por **nombres de contenedor internos**  
✅ Cada uno tiene su **directorio independiente**  
✅ Pueden ejecutarse en **cualquier orden**  
✅ Datos **persistentes** mediante volúmenes  

¡Listo para conectar! 🎉
