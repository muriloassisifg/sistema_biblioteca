from pydantic import BaseModel, ConfigDict, Field


class LivroCriar(BaseModel):        # ENTRA no cadastro
    titulo: str = Field(min_length=2)
    ano: int = Field(ge=1450, le=2100)
    disponivel: bool = True


class LivroPublico(BaseModel):      # SAI na resposta
    # A novidade do encontro 4: sem esta linha o Pydantic so' aceita
    # dicionario, e agora quem chega e' um objeto do SQLAlchemy.
    model_config = ConfigDict(from_attributes=True)

    id: int
    titulo: str
    ano: int
    disponivel: bool


class LivroAtualizar(BaseModel):    # ENTRA na edicao, tudo opcional
    titulo: str | None = None
    ano: int | None = None
    disponivel: bool | None = None
