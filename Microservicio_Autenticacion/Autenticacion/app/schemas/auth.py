from pydantic import BaseModel, Field, model_validator


class LoginRequest(BaseModel):
    username: str
    password: str | None = None
    encrypted_password: str | None = None
    ip: str = Field(default="0.0.0.0")
    user_agent: str = Field(default="unknown")
    request_trace_id: str = Field(default="")
    
    @model_validator(mode="after")
    def use_password_if_no_encrypted(self) -> "LoginRequest":
        if self.encrypted_password is None and self.password:
            self.encrypted_password = self.password
        return self


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
