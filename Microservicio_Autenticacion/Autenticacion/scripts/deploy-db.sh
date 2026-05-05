#!/bin/bash

# Script de construcción y despliegue de la base de datos PostgreSQL en Docker
# Microservicio de Autenticación

set -e

echo "=========================================="
echo "MS-Autenticación - Database Deployment"
echo "=========================================="
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar que Docker está disponible
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker no está instalado o no está en el PATH${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose no está instalado o no está en el PATH${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker encontrado${NC}"
echo -e "${GREEN}✓ Docker Compose encontrado${NC}"
echo ""

# Variables
DB_CONTAINER="ms-autenticacion-postgres"
DB_USER="auth"
DB_NAME="auth_db"
NETWORK="ms-autenticacion_default"

# Función para detener contenedores
stop_containers() {
    echo -e "${YELLOW}Deteniendo contenedores existentes...${NC}"
    docker-compose down 2>/dev/null || true
    echo -e "${GREEN}✓ Contenedores detenidos${NC}"
    echo ""
}

# Función para limpiar volúmenes (opcional)
clean_volumes() {
    if [ "$1" == "clean" ]; then
        echo -e "${YELLOW}Eliminando volúmenes antiguos...${NC}"
        docker volume rm pgdata 2>/dev/null || true
        echo -e "${GREEN}✓ Volúmenes eliminados${NC}"
        echo ""
    fi
}

# Función para iniciar servicios
start_services() {
    echo -e "${YELLOW}Iniciando servicios con Docker Compose...${NC}"
    docker-compose up -d
    echo -e "${GREEN}✓ Servicios iniciados${NC}"
    echo ""
}

# Función para esperar a que la BD esté lista
wait_for_db() {
    echo -e "${YELLOW}Esperando a que PostgreSQL esté listo...${NC}"
    
    local maxAttempts=30
    local attempt=0
    
    while [ $attempt -lt $maxAttempts ]; do
        if docker-compose exec -T postgres pg_isready -U $DB_USER -d $DB_NAME &>/dev/null; then
            echo -e "${GREEN}✓ PostgreSQL está listo${NC}"
            echo ""
            return 0
        fi
        
        attempt=$((attempt + 1))
        echo "Intento $attempt/$maxAttempts..."
        sleep 2
    done
    
    echo -e "${RED}Error: PostgreSQL no está respondiendo después de $maxAttempts intentos${NC}"
    return 1
}

# Función para verificar las tablas creadas
verify_tables() {
    echo -e "${YELLOW}Verificando tablas creadas...${NC}"
    
    local tables=$(docker-compose exec -T postgres psql -U $DB_USER -d $DB_NAME -c "\dt" 2>/dev/null | grep -E "sessions_user|app_tokens|access_history|login_attempt_control|invalidated_tokens" | wc -l)
    
    if [ $tables -eq 5 ]; then
        echo -e "${GREEN}✓ Todas las 5 tablas fueron creadas correctamente${NC}"
        echo ""
        return 0
    else
        echo -e "${RED}Error: No se crearon todas las tablas. Encontradas: $tables${NC}"
        return 1
    fi
}

# Función para mostrar información de conexión
show_connection_info() {
    echo -e "${GREEN}=========================================="
    echo "Conexión a la Base de Datos"
    echo "==========================================${NC}"
    echo ""
    echo "Host: postgres (dentro de Docker)"
    echo "Host: localhost (desde el host)"
    echo "Puerto: 5432"
    echo "Usuario: $DB_USER"
    echo "Contraseña: auth"
    echo "Base de datos: $DB_NAME"
    echo ""
    echo "Connection string:"
    echo "postgresql://$DB_USER:auth@postgres:5432/$DB_NAME"
    echo ""
}

# Función principal
main() {
    # Limpiar si se especifica 'clean'
    if [ "$1" == "clean" ]; then
        clean_volumes "clean"
    fi
    
    # Detener contenedores existentes
    stop_containers
    
    # Iniciar servicios
    start_services
    
    # Esperar a que la BD esté lista
    if ! wait_for_db; then
        echo -e "${RED}Error al esperar a PostgreSQL${NC}"
        docker-compose logs postgres
        exit 1
    fi
    
    # Verificar tablas
    if ! verify_tables; then
        echo -e "${RED}Error al verificar tablas${NC}"
        docker-compose logs postgres
        exit 1
    fi
    
    # Mostrar información de conexión
    show_connection_info
    
    echo -e "${GREEN}=========================================="
    echo "¡Base de datos desplegada exitosamente!"
    echo "==========================================${NC}"
    echo ""
    echo "Comandos útiles:"
    echo "  - Ver logs: docker-compose logs -f postgres"
    echo "  - Conectar a BD: docker-compose exec postgres psql -U auth -d auth_db"
    echo "  - Detener servicios: docker-compose down"
    echo "  - Detener y limpiar: docker-compose down -v"
}

# Ejecutar
main "$@"
