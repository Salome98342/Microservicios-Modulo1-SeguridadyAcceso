# Microservicio de Usuarios - Docker Setup

Este documento explica cómo ejecutar el microservicio de usuarios usando Docker y Docker Compose.

## Requisitos Previos

- **Docker** instalado ([descargar](https://www.docker.com/products/docker-desktop))
- **Docker Compose** (incluido en Docker Desktop)
- Git (opcional, para clonar el repositorio)

## Estructura de Archivos

```
Microservicio_Usuario/
├── docker-compose.yml          # Orquestación de servicios
├── .dockerignore               # Archivos a ignorar en la imagen Docker
├── .env.example                # Ejemplo de variables de entorno
└── ms_usuario/
    ├── Dockerfile              # Configuración de la imagen
    ├── main.py                 # Punto de entrada de la aplicación
    ├── requirements.txt        # Dependencias Python
    ├── config.py               # Configuración
    ├── init_db.sql             # Script de inicialización de BD
    └── ...
```

## Instrucciones de Uso

### 1. Configurar Variables de Entorno

Copia el archivo `.env.example` a `.env` en la raíz del proyecto:

```bash
copy .env.example .env
```

Opcionalmente, edita los valores en `.env` según tu entorno (especialmente los tokens de seguridad).

### 2. Iniciar los Servicios

Desde la raíz del proyecto (donde está `docker-compose.yml`):

```bash
docker-compose up -d
```

- `-d`: Ejecuta los servicios en segundo plano (detached mode)

### 3. Verificar que los Servicios están Corriendo

```bash
docker-compose ps
```

Debes ver algo como:

```
NAME                   COMMAND                  SERVICE   STATUS
ms_usuarios_db         "docker-entrypoint..."   db        Up (healthy)
ms_usuarios_app        "uvicorn main:app..."    app       Up
```

### 4. Acceder a la Aplicación

- **API**: http://localhost:8000
- **Documentación Swagger**: http://localhost:8000/docs
- **Documentación ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/ (devuelve estado del servicio)

### 5. Ver Logs

Para ver los logs de toda la aplicación:

```bash
docker-compose logs -f
```

Para ver los logs de un servicio específico:

```bash
docker-compose logs -f app
docker-compose logs -f db
```

### 6. Parar los Servicios

```bash
docker-compose down
```

Para también eliminar los volúmenes (borra la BD):

```bash
docker-compose down -v
```

## Estructura del docker-compose.yml

### Servicio `db` (PostgreSQL)

- **Imagen**: `postgres:15-alpine`
- **Puerto**: `5432:5432`
- **Variables de Entorno**:
  - `POSTGRES_USER`: postgres
  - `POSTGRES_PASSWORD`: postgres
  - `POSTGRES_DB`: db_usuarios

- **Volumen**: `postgres_data` (persistencia de datos)
- **Script de Inicialización**: Ejecuta `init_db.sql` automáticamente

### Servicio `app` (FastAPI)

- **Build**: Construye desde `./ms_usuario/Dockerfile`
- **Puerto**: `8000:8000`
- **Dependencia**: Espera a que `db` esté healthy
- **Variables de Entorno**: Configurables en el docker-compose.yml
- **Volumen**: Monta el código fuente para desarrollo (hot-reload)

## Desarrollo

Durante el desarrollo, los cambios en `ms_usuario/` se reflejan automáticamente sin necesidad de reconstruir (gracias al volume mount).

### Reconstruir la Imagen (después de cambiar requirements.txt)

```bash
docker-compose up -d --build
```

### Instalar Nuevas Dependencias

1. Añade el paquete a `ms_usuario/requirements.txt`
2. Reconstruye la imagen:

```bash
docker-compose up -d --build
```

## Solución de Problemas

### El servicio `app` no se conecta a la BD

Verifica los logs:

```bash
docker-compose logs app
```

Asegúrate de que `DB_HOST=db` en las variables de entorno (es importante para la resolución de nombres de Docker).

### El puerto 5432 o 8000 ya está en uso

Cambia los puertos en `docker-compose.yml`:

```yaml
ports:
  - "5433:5432"  # Cambiar a 5433 localmente
  - "8001:8000"  # Cambiar a 8001 localmente
```

### Limpiar contenedores y volúmenes

```bash
docker-compose down -v
docker system prune -a --volumes
```

## Producción

En producción:

1. **Cambiar los tokens** en `.env` por valores seguros
2. **No usar volúmenes** para el código (poner en READONLY o eliminar)
3. **Usar credenciales seguras** para la BD
4. **Configurar healthchecks** adecuados
5. **Usar una red privada** en lugar de exponer puertos directamente
6. **Habilitar logging** centralizado

## Contacto

Para preguntas o problemas, contacta al equipo de desarrollo.
