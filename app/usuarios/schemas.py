from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UsuarioCriar(BaseModel):        # ENTRA no cadastro
    nome: str = Field(min_length=2)
    email: EmailStr                   # "abc" nem chega ao seu codigo: 422
    senha: str = Field(min_length=6)


class UsuarioPublico(BaseModel):      # SAI na resposta -- sem senha, sem hash
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    email: EmailStr


class Token(BaseModel):               # SAI no login
    access_token: str
    token_type: str = "bearer"
