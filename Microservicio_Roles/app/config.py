from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    aes_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_secret_key: str
    ms_autenticacion_url: str
    ms_auditoria_url: str
    app_name: str = "ms-roles"
    app_version: str = "0.1.0"
    app_port: int = 8003
    debug: bool = False
    timeout_ms_autenticacion: int  = 3000    # ← NUEVA
    timeout_ms_auditoria:     int  = 1500

    class Config:
        env_file = ".env"

settings = Settings()