# Script de construcción y despliegue de la base de datos PostgreSQL en Docker
# Microservicio de Autenticación - Windows/PowerShell

param(
    [Parameter(Mandatory=$false)]
    [string]$Action = "deploy",
    
    [Parameter(Mandatory=$false)]
    [switch]$Clean = $false
)

# Línea de colores
function Write-Success {
    Write-Host "✓ $args" -ForegroundColor Green
}

function Write-Warning {
    Write-Host "! $args" -ForegroundColor Yellow
}

function Write-Error-Custom {
    Write-Host "✗ $args" -ForegroundColor Red
}

# Verificar Docker
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "MS-Autenticación - Database Deployment" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error-Custom "Docker no está instalado o no está en el PATH"
    exit 1
}

if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Error-Custom "Docker Compose no está instalado o no está en el PATH"
    exit 1
}

Write-Success "Docker encontrado"
Write-Success "Docker Compose encontrado"
Write-Host ""

# Variables
$DB_USER = "auth"
$DB_NAME = "auth_db"

# Detener contenedores existentes
function Stop-Containers {
    Write-Warning "Deteniendo contenedores existentes..."
    docker-compose down 2>$null
    Write-Success "Contenedores detenidos"
    Write-Host ""
}

# Limpiar volúmenes
function Clean-Volumes {
    if ($Clean) {
        Write-Warning "Eliminando volúmenes antiguos..."
        docker volume rm pgdata 2>$null
        Write-Success "Volúmenes eliminados"
        Write-Host ""
    }
}

# Iniciar servicios
function Start-Services {
    Write-Warning "Iniciando servicios con Docker Compose..."
    docker-compose up -d
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Custom "Error al iniciar servicios"
        exit 1
    }
    
    Write-Success "Servicios iniciados"
    Write-Host ""
}

# Esperar a que PostgreSQL esté listo
function Wait-ForDatabase {
    Write-Warning "Esperando a que PostgreSQL esté listo..."
    
    $maxAttempts = 30
    $attempt = 0
    
    while ($attempt -lt $maxAttempts) {
        try {
            $result = docker-compose exec -T postgres pg_isready -U $DB_USER -d $DB_NAME 2>$null
            
            if ($LASTEXITCODE -eq 0) {
                Write-Success "PostgreSQL está listo"
                Write-Host ""
                return $true
            }
        }
        catch {
            # Continuar intentando
        }
        
        $attempt++
        Write-Host "Intento $attempt/$maxAttempts..."
        Start-Sleep -Seconds 2
    }
    
    Write-Error-Custom "PostgreSQL no está respondiendo después de $maxAttempts intentos"
    return $false
}

# Verificar tablas creadas
function Verify-Tables {
    Write-Warning "Verificando tablas creadas..."
    
    try {
        $tables = docker-compose exec -T postgres psql -U $DB_USER -d $DB_NAME -c "\dt" 2>$null | `
                  Select-String -Pattern "sessions_user|app_tokens|access_history|login_attempt_control|invalidated_tokens" | `
                  Measure-Object -Line
        
        if ($tables.Lines -ge 5) {
            Write-Success "Todas las 5 tablas fueron creadas correctamente"
            Write-Host ""
            return $true
        }
        else {
            Write-Error-Custom "No se crearon todas las tablas. Se encontraron: $($tables.Lines)"
            return $false
        }
    }
    catch {
        Write-Error-Custom "Error al verificar tablas: $_"
        return $false
    }
}

# Mostrar información de conexión
function Show-ConnectionInfo {
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "Conexión a la Base de Datos" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Host: postgres (dentro de Docker)"
    Write-Host "Host: localhost (desde el host)"
    Write-Host "Puerto: 5432"
    Write-Host "Usuario: $DB_USER"
    Write-Host "Contraseña: auth"
    Write-Host "Base de datos: $DB_NAME"
    Write-Host ""
    Write-Host "Connection string:"
    Write-Host "postgresql://$DB_USER`:auth@postgres:5432/$DB_NAME" -ForegroundColor Yellow
    Write-Host ""
}

# Función principal
function Main {
    # Limpiar si se especifica
    if ($Clean) {
        Clean-Volumes
    }
    
    # Detener contenedores existentes
    Stop-Containers
    
    # Iniciar servicios
    Start-Services
    
    # Esperar a que la BD esté lista
    if (-not (Wait-ForDatabase)) {
        Write-Error-Custom "Error al esperar a PostgreSQL"
        docker-compose logs postgres
        exit 1
    }
    
    # Verificar tablas
    if (-not (Verify-Tables)) {
        Write-Error-Custom "Error al verificar tablas"
        docker-compose logs postgres
        exit 1
    }
    
    # Mostrar información de conexión
    Show-ConnectionInfo
    
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "¡Base de datos desplegada exitosamente!" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Comandos útiles:" -ForegroundColor Cyan
    Write-Host "  - Ver logs: docker-compose logs -f postgres"
    Write-Host "  - Conectar a BD: docker-compose exec postgres psql -U auth -d auth_db"
    Write-Host "  - Detener servicios: docker-compose down"
    Write-Host "  - Detener y limpiar: docker-compose down -v"
    Write-Host ""
}

# Ejecutar
Main
