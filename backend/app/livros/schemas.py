from pydantic import BaseModel, ConfigDict, field_validator


def _titulo_legivel(titulo):
    # A mensagem e' para quem le a resposta 422: diz o que fazer, nao o que
    # o validador se chama.
    if len(titulo.strip()) < 2:
        raise ValueError("o titulo precisa ter pelo menos 2 caracteres")
    return titulo.strip()


def _ano_plausivel(ano):
    if not 1450 <= ano <= 2100:
        raise ValueError("o ano precisa estar entre 1450 e 2100")
    return ano


class LivroCriar(BaseModel):        # ENTRA no cadastro
    titulo: str
    ano: int
    disponivel: bool = True

    @field_validator("titulo")
    @classmethod
    def titulo_legivel(cls, v):
        return _titulo_legivel(v)

    @field_validator("ano")
    @classmethod
    def ano_plausivel(cls, v):
        return _ano_plausivel(v)


class LivroPublico(BaseModel):      # SAI na resposta
    model_config = ConfigDict(from_attributes=True)

    id: int
    titulo: str
    ano: int
    disponivel: bool
    dono_id: int | None          # de quem e' -- None nos livros de antes do dono


class LivroAtualizar(BaseModel):    # ENTRA na edicao, tudo opcional
    titulo: str | None = None
    ano: int | None = None
    disponivel: bool | None = None

    @field_validator("titulo")
    @classmethod
    def titulo_legivel(cls, v):
        return v if v is None else _titulo_legivel(v)

    @field_validator("ano")
    @classmethod
    def ano_plausivel(cls, v):
        return v if v is None else _ano_plausivel(v)
