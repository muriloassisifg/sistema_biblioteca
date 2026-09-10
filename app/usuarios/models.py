from sqlalchemy import Column, Integer, String

from ..database import Base


class Usuario(Base):
    """A TABELA de usuarios.

    Repare no que NAO existe aqui: uma coluna `senha`. O que se guarda e' o
    hash -- e ninguem, nem quem administra o banco, consegue ler a senha de
    volta a partir dele.
    """

    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(80), nullable=False)
    email = Column(String(120), nullable=False, unique=True, index=True)
    senha_hash = Column(String(100), nullable=False)
