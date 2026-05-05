# 🚀 INICIO RÁPIDO - Microservicios Conectados

## Opción 1: Usando docker-compose directamente (recomendado)

### Paso 1: Abrir PowerShell en la raíz del proyecto

```powershell
# Desde c:\Users\salom\OneDrive\Documentos\7 Semestre\Desarrollo 3\Microservicios
cd c:\Users\salom\OneDrive\Documentos\7 Semestre\Desarrollo 3\Microservicios
```

### Paso 2: Levantar los servicios

```powershell
docker-compose up -d
```

**Output esperado:**
```
✓ Container ms-autenticacion-postgres  Created
✓ Container ms-usuarios-postgres       Created
✓ Container ms-autenticacion           Created
✓ Container ms-usuarios-app            Created
```

### Paso 3: Verificar que están corriendo

```powershell
docker-compose ps
```

**Output esperado:**
```
NAME                         STATUS
ms-autenticacion-postgres    Up (healthy)
ms-autenticacion             Up
ms-usuarios-postgres         Up (healthy)
ms-usuarios-app              Up
```

### Paso 4: Ver los logs (opcional)

```powershell
# Ver todos
docker-compose logs -f

# O solo un servicio
docker-compose logs -f ms-autenticacion
docker-compose logs -f ms-usuarios-app
```

---

## Opción 2: Usando el script PowerShell

### Paso 1: Permitir ejecución de scripts (primera vez)

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Paso 2: Usar el script

```powershell
# Iniciar todos los servicios
.\manage-services.ps1 -Action up

# Ver logs
.\manage-services.ps1 -Action logs -Service all

# Ver estado
.\manage-services.ps1 -Action ps

# Detener
.\manage-services.ps1 -Action down

# Reiniciar
.\manage-services.ps1 -Action restart
```

---

## ✅ Verificar que funciona

### 1. Autenticación está respondiendo

```powershell
curl http://localhost:8002/docs
```

Deberías ver la documentación de Swagger de autenticación.

### 2. Usuarios está respondiendo

```powershell
curl http://localhost:8000/docs
```

Deberías ver la documentación de Swagger de usuarios.

### 3. Los servicios se comunican

Los logs de `ms-usuarios` deberían mostrar conexiones exitosas a `ms-autenticacion:8000`.

---

## 🔑 URLs de acceso

| Servicio | URL | Documentación |
|----------|-----|---------------|
| **Autenticación** | http://localhost:8002 | http://localhost:8002/docs |
| **Usuarios** | http://localhost:8000 | http://localhost:8000/docs |
| **Autenticación (interno)** | http://ms-autenticacion:8000 | Solo desde otros servicios |

---

## 🛑 Parar los servicios

```powershell
docker-compose down
```

Para eliminar también base de datos:

```powershell
docker-compose down -v
```

---

## 🐛 Troubleshooting

### Puerto 8000 o 8002 ya en uso

```powershell
# Encontrar qué está usando el puerto
netstat -ano | findstr :8000
netstat -ano | findstr :8002

# O cambiar los puertos en docker-compose.yml:
# Cambiar "8000:8000" por "8001:8000" por ejemplo
```

### Los servicios no se ven

```powershell
# Reconstruir todo
docker-compose build --no-cache
docker-compose up -d
```

### Ver errores detallados

```powershell
# Ver logs de un servicio específico
docker-compose logs ms-usuarios-app
docker-compose logs ms-autenticacion

# Ver logs con más contexto
docker-compose logs --tail=50 -f ms-usuarios-app
```

---

## 📝 Notas importantes

✅ **Ambos servicios usan la misma red Docker**: `microservicios-network`

✅ **El usuario se comunica con autenticación en**: `http://ms-autenticacion:8000`

✅ **Las bases de datos son independientes** pero accesibles desde los servicios

✅ **Los volúmenes persisten los datos** entre reinicios

---

## 🔄 Flujo de comunicación

```
[Cliente en localhost]
        ↓
    [Puertos expuestos]
        ↓
  localhost:8000 ──→ ms-usuarios:8000
  localhost:8002 ──→ ms-autenticacion:8000
        ↓
    [Red Docker]
        ↓
  ms-usuarios ──→ ms-autenticacion (para validar tokens)
        ↓
   [Bases de datos]
```

---

¡Ya está! Los servicios están conectados y comunicándose. 🎉
