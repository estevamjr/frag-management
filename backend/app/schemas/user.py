from pydantic import BaseModel, EmailStr


# Base (compartilhado)
class UserBase(BaseModel):
    username: str
    email: EmailStr


# Request (Cadastro) - Com senha
class UserCreate(UserBase):
    password: str


# Response (Retorno) - Sem senha
class UserResponse(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True
