# Script de despliegue de base de datos - MS-Autenticacion
# Windows PowerShell

Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "MS-Autenticacion - Database Deployment" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Docker
Write-Host "Verificando Docker..." -ForegroundColor Yellow

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Docker no esta instalado" -ForegroundColor Red
    exit 1
}

if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Docker Compose no esta instalado" -ForegroundColor Red
    exit 1
}

Write-Host "Docker OK" -ForegroundColor Green
Write-Host "Docker Compose OK" -ForegroundColor Green
Write-Host ""

# Detener contenedores existentes
Write-Host "Deteniendo contenedores existentes..." -ForegroundColor Yellow
docker-compose down 2>$null
Write-Host "Contenedores detenidos" -ForegroundColor Green
Write-Host ""

# Iniciar servicios
Write-Host "Iniciando servicios con Docker Compose..." -ForegroundColor Yellow
docker-compose up -d
Write-Host "Servicios iniciados" -ForegroundColor Green
Write-Host ""

# Esperar a que PostgreSQL esté listo
Write-Host "Esperando a que PostgreSQL este listo..." -ForegroundColor Yellow

$maxAttempts = 30
$attempt = 0

while ($attempt -lt $maxAttempts) {
    try {
        docker-compose exec -T postgres pg_isready -U auth -d auth_db 2>$null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "PostgreSQL esta listo!" -ForegroundColor Green
            Write-Host ""
            break
        }
    }
    catch {
        # Continuar intentando
    }
    
    $attempt++
    if ($attempt % 5 -eq 0) {
        Write-Host "Intento $attempt/$maxAttempts..." -ForegroundColor Gray
    }
    Start-Sleep -Seconds 2
}

if ($attempt -eq $maxAttempts) {
    Write-Host "Error: PostgreSQL no responde" -ForegroundColor Red
    docker-compose logs postgres
    exit 1
}

# Verificar tablas
Write-Host "Verificando tablas creadas..." -ForegroundColor Yellow

try {
    $tableList = docker-compose exec -T postgres psql -U auth -d auth_db -c "\dt" 2>$null
    
    if ($tableList -match "sessions_user" -and $tableList -match "app_tokens" -and $tableList -match "access_history") {
        Write-Host "Tablas creadas correctamente" -ForegroundColor Green
    }
    else {
        Write-Host "No se detectaron todas las tablas esperadas" -ForegroundColor Red
    }
}
catch {
    Write-Host "No se pudieron verificar las tablas" -ForegroundColor Yellow
}

Write-Host ""

# Mostrar informacion de conexion
Write-Host "===========================================" -ForegroundColor Green
Write-Host "Informacion de Conexion" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Host: postgres (dentro de Docker)"
Write-Host "Host: localhost (desde tu maquina)"
Write-Host "Puerto: 5432"
Write-Host "Usuario: auth"
Write-Host "Contrasena: auth"
Write-Host "Base de datos: auth_db"
Write-Host ""
Write-Host "Connection String:"
Write-Host "postgresql://auth:auth@postgres:5432/auth_db" -ForegroundColor Yellow
Write-Host ""

Write-Host "===========================================" -ForegroundColor Green
Write-Host "Base de datos desplegada exitosamente!" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Comandos utiles:" -ForegroundColor Cyan
Write-Host "  - Ver logs: docker-compose logs -f postgres"
Write-Host "  - Conectar a BD: docker-compose exec postgres psql -U auth -d auth_db"
Write-Host "  - Detener servicios: docker-compose down"
Write-Host "  - Detener y limpiar: docker-compose down -v"
Write-Host ""

Write-Host "Estado de contenedores:" -ForegroundColor Cyan
docker-compose ps
