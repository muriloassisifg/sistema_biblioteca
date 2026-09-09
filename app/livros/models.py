from sqlalchemy import Boolean, Column, Integer, String

from ..database import Base


class Livro(Base):
    """A TABELA. Nao confunda com os schemas: aquilo atravessa a
    fronteira da API, isto vira linha no banco.
    """

    __tablename__ = "livros"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(120), nullable=False)
    ano = Column(Integer, nullable=False)
    disponivel = Column(Boolean, nullable=False, default=True)
