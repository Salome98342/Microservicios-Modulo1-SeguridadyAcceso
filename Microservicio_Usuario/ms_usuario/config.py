import os
from dotenv import load_dotenv

load_dotenv()

# Application
APP_TITULO = "ms-usuarios [USR]"
APP_DESCRIPCION = "Microservicio de gestion de usuarios - Modulo 1: Seguridad y Acceso"
APP_VERSION = "1.0.0"
APP_PREFIX = "/api/v1"

# Database
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "db_usuarios")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Crypto and auth
AES_SECRET_KEY = os.getenv("AES_SECRET_KEY", "")
BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", "12"))
USR_APP_TOKEN = os.getenv("USR_APP_TOKEN", "")

# External service tokens
AUTH_APP_TOKEN = os.getenv("AUTH_APP_TOKEN", "")
ROL_APP_TOKEN = os.getenv("ROL_APP_TOKEN", "")
NOT_APP_TOKEN = os.getenv("NOT_APP_TOKEN", "")
AUD_APP_TOKEN = os.getenv("AUD_APP_TOKEN", "")

# External service URLs
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://ms-autenticacion:8000")
ROL_SERVICE_URL = os.getenv("ROL_SERVICE_URL", "http://ms-roles:8000")
NOT_SERVICE_URL = os.getenv("NOT_SERVICE_URL", "http://ms-notificaciones:8000")
AUD_SERVICE_URL = os.getenv("AUD_SERVICE_URL", "http://ms-auditoria:8000")

# Timeouts
TIMEOUT_AUTH = float(os.getenv("TIMEOUT_AUTH", "3"))
TIMEOUT_ROL = float(os.getenv("TIMEOUT_ROL", "3"))
TIMEOUT_NOT = float(os.getenv("TIMEOUT_NOT", "1"))
TIMEOUT_AUD = float(os.getenv("TIMEOUT_AUD", "0.5"))

# Pagination
PAGINA_DEFAULT = 1
ITEMS_POR_PAGINA_DEFAULT = 10
ITEMS_POR_PAGINA_MAX = 100

# Debug Mode (desactiva autenticación para testing)
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

# Bypass de roles para pruebas de integración
SKIP_ROLE_VALIDATION = os.getenv("SKIP_ROLE_VALIDATION", "false").lower() == "true"
