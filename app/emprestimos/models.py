from sqlalchemy import Column, Date, ForeignKey, Integer, String

from ..database import Base


class Emprestimo(Base):
    """A TABELA de emprestimos. No encontro 5 de P3 ela era um CREATE TABLE
    escrito a mao; aqui ela e' declarada do mesmo jeito que o Livro, e o
    SQLAlchemy escreve o SQL -- para o SQLite hoje, para o PostgreSQL no
    dia em que a URL do .env mudar.
    """

    __tablename__ = "emprestimos"

    id = Column(Integer, primary_key=True, index=True)
    livro_id = Column(Integer, ForeignKey("livros.id"), nullable=False)
    leitor_id = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False)    # "ativo" ou "devolvido"

    # As duas do encontro 7 (Strategy), acrescentadas pela segunda migracao.
    # Os emprestimos feitos antes dela seguiam a regra unica de antes, cujo
    # limite de 3 e' o do aluno, e nenhum tinha data de devolucao. Por isso o
    # tipo ja' nasce "aluno" no banco, e a data pode ficar vazia.
    tipo_leitor = Column(String(20), nullable=False, server_default="aluno")
    devolver_ate = Column(Date, nullable=True)
