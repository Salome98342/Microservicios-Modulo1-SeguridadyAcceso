from pydantic import BaseModel, Field, field_validator


class LoginRequest(BaseModel):
    username: str
    password: str | None = None
    encrypted_password: str | None = None
    ip: str = Field(default="0.0.0.0")
    user_agent: str = Field(default="unknown")
    request_trace_id: str = Field(default="")
    
    @field_validator('encrypted_password', mode='before')
    @classmethod
    def use_password_if_no_encrypted(cls, v, info):
        if v is None and info.data.get('password'):
            return info.data.get('password')
        return v


class ValidateSessionRequest(BaseModel):
    token: str


class CreateAppTokenRequest(BaseModel):
    name_service: str
    token_value: str
    description: str = ""
    updated_by: str


class UpdateAppTokenRequest(BaseModel):
    token_value: str | None = None
    description: str | None = None
    status: str | None = None
    updated_by: str


class ForceCloseRequest(BaseModel):
    reason: str = "admin_force_close"
