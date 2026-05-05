# ms-autenticacion

Microservicio base de autenticacion para ERP universitario.

Incluye:
- Documentacion de requisitos, arquitectura y firmas.
- Contratos OpenAPI de exposicion y dependencias.
- Implementacion inicial en FastAPI + SQLite para pruebas locales.

## Estructura

- docs/01-requisitos-ms-autenticacion.md: Requisitos funcionales y no funcionales.
- docs/02-arquitectura-ms-autenticacion.md: Arquitectura logica y tecnica.
- docs/03-firmas-integracion.md: Firmas (contratos) para integracion con otros modulos.
- contracts/openapi-ms-autenticacion.yaml: API principal del microservicio.
- contracts/dependencies/ms-usuarios-signature.yaml: Firma consumida de ms-usuarios.
- contracts/dependencies/ms-roles-signature.yaml: Firma consumida de ms-roles.
- database/schema.postgres.sql: Esquema PostgreSQL del microservicio.
- app/main.py: Punto de arranque de FastAPI.
- app/api/: Controladores y rutas HTTP.
- app/schemas/: Modelos Pydantic del dominio.
- app/services/: Logica de negocio.
- app/core/: Configuracion y acceso a datos.

## Estructura MVC por carpetas

- Model: `app/schemas/` + `app/core/database.py`.
- View: respuestas JSON de la API y Swagger `/docs`.
- Controller: `app/api/`.
- Service: `app/services/`.

## Requisitos previos

- Python 3.11 o superior.
- Entorno virtual activo (recomendado).

## Configuracion

1. Copiar variables de entorno:
	- Copia .env.example a .env
2. Instalar dependencias:
	- pip install -r requirements.txt

Variables para integracion real:
- USERS_SERVICE_URL: URL base de ms-usuarios (ejemplo: http://localhost:8001).
- ROLES_SERVICE_URL: URL base de ms-roles (ejemplo: http://localhost:8002).
- HTTP_TIMEOUT_SECONDS: timeout de llamadas HTTP entre servicios.
- AUTH_USE_STUB_FALLBACK: true/false para permitir fallback a datos demo si un servicio externo falla.

## Ejecutar local

- uvicorn app.main:app --reload --port 8000

Documentacion Swagger:
- http://127.0.0.1:8000/docs

## Ejecutar con Docker

Construir la imagen:
- docker build -t ms-autenticacion .

Levantar con Docker Compose:
- docker compose up --build

La API quedara disponible en:
- http://127.0.0.1:8000/docs

La base SQLite se persistira en el volumen `auth_data` usando `DB_PATH=/data/auth.db`.

## Usuarios demo de prueba

- admin / enc_admin123
- maria / enc_maria123

Nota: el campo encrypted_password representa la credencial cifrada que normalmente vendria desde el cliente.

## Flujo rapido de prueba

1. Login:
	- POST /v1/auth/login
2. Copiar access_token de la respuesta.
3. Consultar sesiones activas con token ADMIN:
	- GET /v1/sessions
4. Validar sesion:
	- POST /v1/auth/session/validate
5. Cerrar sesion:
	- POST /v1/auth/logout

## Alcance de esta implementacion

- Base funcional para desarrollo academico y validacion temprana.
- Soporta integracion HTTP real con ms-usuarios y ms-roles por variables de entorno.
- Mantiene stubs internos (DEMO_USERS y DEMO_ROLES) como fallback opcional para no bloquear pruebas locales.
- La implementacion actual usa PostgreSQL; el archivo `database/schema.postgres.sql` permite recrear la estructura en limpio.
