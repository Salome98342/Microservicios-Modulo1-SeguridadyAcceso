.PHONY: help up down restart logs logs-app logs-db shell-app shell-db build rebuild clean test

help:
	@echo "Microservicio de Usuarios - Comandos Docker"
	@echo "============================================"
	@echo ""
	@echo "Comandos disponibles:"
	@echo ""
	@echo "  make up              - Inicia los servicios"
	@echo "  make down            - Detiene los servicios"
	@echo "  make restart         - Reinicia los servicios"
	@echo "  make build           - Construye la imagen Docker (sin reiniciar)"
	@echo "  make rebuild         - Reconstruye todo desde cero"
	@echo "  make logs            - Muestra logs de todos los servicios"
	@echo "  make logs-app        - Muestra logs de la aplicación"
	@echo "  make logs-db         - Muestra logs de la base de datos"
	@echo "  make shell-app       - Abre bash dentro del contenedor de la app"
	@echo "  make shell-db        - Abre psql dentro del contenedor de la BD"
	@echo "  make status          - Muestra estado de los contenedores"
	@echo "  make clean           - Detiene servicios y limpia volúmenes"
	@echo "  make ps              - Lista los contenedores en ejecución"
	@echo ""

up:
	@echo "Iniciando servicios..."
	docker-compose up -d
	@echo "✓ Servicios iniciados"
	@echo "API disponible en: http://localhost:8000"
	@echo "Docs en: http://localhost:8000/docs"

down:
	@echo "Deteniendo servicios..."
	docker-compose down
	@echo "✓ Servicios detenidos"

restart: down up
	@echo "✓ Servicios reiniciados"

build:
	@echo "Construyendo imagen Docker..."
	docker-compose build
	@echo "✓ Imagen construida"

rebuild: clean build up
	@echo "✓ Completamente reconstruido"

logs:
	docker-compose logs -f

logs-app:
	docker-compose logs -f app

logs-db:
	docker-compose logs -f db

shell-app:
	docker exec -it ms_usuarios_app /bin/bash

shell-db:
	docker exec -it ms_usuarios_db psql -U postgres -d db_usuarios

status:
	docker-compose ps

ps:
	docker ps --filter "label=com.docker.compose.project"

clean:
	@echo "Limpiando servicios y volúmenes..."
	docker-compose down -v
	@echo "✓ Limpieza completada"

test:
	@echo "Ejecutando pruebas..."
	docker-compose exec app pytest
	@echo "✓ Pruebas completadas"

# Información útil
info:
	@echo "Información de los servicios:"
	@echo ""
	@echo "API FastAPI:"
	@echo "  Puerto: 8000"
	@echo "  URL: http://localhost:8000"
	@echo "  Swagger: http://localhost:8000/docs"
	@echo ""
	@echo "PostgreSQL:"
	@echo "  Host: localhost (desde local) / db (desde contenedor)"
	@echo "  Puerto: 5432"
	@echo "  BD: db_usuarios"
	@echo "  Usuario: postgres"
	@echo ""
