import os

from dotenv import load_dotenv

load_dotenv()

# Application
APP_TITULO = "ms-autenticacion [AUTH]"
APP_DESCRIPCION = "Microservicio de autenticación y autorización"
APP_VERSION = "1.0.0"

JWT_SECRET = os.getenv("JWT_SECRET", "change_this_super_secret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ISSUER = os.getenv("JWT_ISSUER", "ms-autenticacion")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://auth:auth@localhost:5432/auth_db")
AES256_KEY_B64 = os.getenv("AES256_KEY_B64", "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
USERS_SERVICE_URL = os.getenv("USERS_SERVICE_URL", "")
ROLES_SERVICE_URL = os.getenv("ROLES_SERVICE_URL", "")
HTTP_TIMEOUT_SECONDS = float(os.getenv("HTTP_TIMEOUT_SECONDS", "3"))
AUTH_USE_STUB_FALLBACK = os.getenv("AUTH_USE_STUB_FALLBACK", "true").lower() == "true"
