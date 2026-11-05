from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

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

    # O DONO. Uma coluna que guarda o id de um usuario -- a chave estrangeira
    # -- e a ligacao que o SQLAlchemy monta em cima dela: `livro.dono` e' o
    # objeto Usuario inteiro, sem voce escrever a consulta. A constraint tem
    # nome porque o SQLite, em migracao, exige constraint com nome.
    dono_id = Column(Integer, ForeignKey("usuarios.id", name="fk_livros_dono"), nullable=True)
    dono = relationship("Usuario", back_populates="livros")
