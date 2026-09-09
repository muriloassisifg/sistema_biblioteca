from pydantic import BaseModel, ConfigDict


class EmprestimoEntrada(BaseModel):    # ENTRA no pedido
    livro_id: int
    leitor_id: int


class EmprestimoPublico(BaseModel):    # SAI na resposta
    # O repositorio agora devolve um objeto do SQLAlchemy, nao mais um
    # dicionario. Sem esta linha o Pydantic so' aceita dicionario.
    model_config = ConfigDict(from_attributes=True)

    id: int
    livro_id: int
    leitor_id: int
    status: str
