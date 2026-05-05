# Guía de Inicio Rápido - Base de Datos ms-autenticacion

## 🚀 Iniciar en 30 segundos

### Windows (PowerShell)
```powershell
cd Autenticacion
.\scripts\deploy-db.ps1
```

### Linux / macOS
```bash
cd Autenticacion
chmod +x scripts/deploy-db.sh
./scripts/deploy-db.sh
```

### Sin scripts (cualquier SO)
```bash
cd Autenticacion
docker-compose up -d
```

## ✅ Verificar que todo funciona

```bash
# Ver estado de los contenedores
docker-compose ps

# Ver logs
docker-compose logs postgres

# Conectar a la BD
docker-compose exec postgres psql -U auth -d auth_db -c "\dt"
```

## 📊 Detalles de Conexión

```
Host:     localhost
Puerto:   5432
Usuario:  auth
Password: auth
BD:       auth_db

Conexión: postgresql://auth:auth@localhost:5432/auth_db
```

## 📁 Archivos Creados

| Archivo | Descripción |
|---------|------------|
| `database/init.sql` | ✨ Script SQL para crear schema y tablas |
| `database/README.md` | 📖 Documentación completa |
| `database/.env.database` | ⚙️ Variables de configuración |
| `Dockerfile.postgres` | 🐳 Dockerfile personalizado para PostgreSQL |
| `docker-compose.yml` | ✅ Actualizado con init.sql |
| `docker-compose.extended.yml` | 🔧 Versión avanzada con pgAdmin |
| `scripts/deploy-db.sh` | 🐧 Script de despliegue Linux/macOS |
| `scripts/deploy-db.ps1` | 💻 Script de despliegue Windows |

## 🎯 Próximos Pasos

1. **Verifica la conexión:**
   ```bash
   docker-compose exec postgres psql -U auth -d auth_db -c "SELECT * FROM sessions_user LIMIT 1;"
   ```

2. **Configura tu aplicación:**
   ```
   DATABASE_URL=postgresql://auth:auth@localhost:5432/auth_db
   ```

3. **Detén los servicios cuando no los uses:**
   ```bash
   docker-compose down
   ```

## 🔧 Comandos Útiles

```bash
# Ver logs en tiempo real
docker-compose logs -f postgres

# Ejecutar query SQL
docker-compose exec postgres psql -U auth -d auth_db -c "SELECT version();"

# Crear backup
docker-compose exec postgres pg_dump -U auth auth_db > backup.sql

# Restaurar desde backup
docker-compose exec -T postgres psql -U auth auth_db < backup.sql

# Ver tamaño de la BD
docker-compose exec postgres psql -U auth -d auth_db -c "SELECT pg_size_pretty(pg_database_size('auth_db'));"

# Detener y limpiar
docker-compose down -v
```

## ⚠️ Cambiar Credenciales (Producción)

1. Edita `docker-compose.yml`:
```yaml
environment:
  POSTGRES_DB: auth_db_prod
  POSTGRES_USER: auth_user
  POSTGRES_PASSWORD: TuContraseñaSegura123!@#
```

2. Actualiza tu cadena de conexión
3. Elimina volúmenes antiguos: `docker-compose down -v`
4. Reinicia: `docker-compose up -d`

## 📞 Soporte

Ver `database/README.md` para documentación completa y solución de problemas.
