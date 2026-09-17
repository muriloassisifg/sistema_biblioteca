from datetime import date

from pydantic import BaseModel, ConfigDict


class EmprestimoEntrada(BaseModel):    # ENTRA no pedido
    livro_id: int
    leitor_id: int
    # Um str qualquer, de proposito: quem sabe quais tipos existem e' o
    # politicas.py. Um Literal aqui seria uma segunda lista de tipos.
    tipo_leitor: str                   # "aluno", "professor", "servidor"...


class EmprestimoPublico(BaseModel):    # SAI na resposta
    # O repositorio agora devolve um objeto do SQLAlchemy, nao mais um
    # dicionario. Sem esta linha o Pydantic so' aceita dicionario.
    model_config = ConfigDict(from_attributes=True)

    id: int
    livro_id: int
    leitor_id: int
    tipo_leitor: str
    devolver_ate: date | None          # AAAA-MM-DD; vazio nos de antes da migracao
    status: str
