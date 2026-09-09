"""A unica camada que sabe consultar emprestimos e livros no banco.

Terceira implementacao do mesmo repositorio: em memoria (encontro 4 de P3),
SQLite escrito a mao (encontro 5) e agora SQLAlchemy -- o mesmo banco e a
mesma sessao que a funcionalidade de livros usa. O Service continua chamando
os mesmos tres metodos, com os mesmos nomes, e recebendo os mesmos tipos de
volta -- e por isso nao mudou nem um caractere pela terceira vez.

A conexao e a sessao NAO estao aqui: moram em `app/database.py`, porque sao
do projeto inteiro. Aqui ficam so' as consultas desta funcionalidade.
"""
from sqlalchemy.orm import Session

from ..livros.models import Livro
from .models import Emprestimo

ATIVO = "ativo"        # a string que o legado errava em um lugar so'


class RepositorioSQLAlchemy:
    """Recebe a sessao ja' aberta: quem escolhe qual e' o dependencias.py."""

    def __init__(self, db: Session):
        self.db = db

    def buscar_livro(self, livro_id):
        # O que sai daqui e' um objeto (o Livro do SQLAlchemy), nunca a
        # linha crua do banco -- igual ao encontro 5.
        return self.db.query(Livro).filter(Livro.id == livro_id).first()

    def contar_ativos(self, leitor_id):
        return (
            self.db.query(Emprestimo)
            .filter(Emprestimo.leitor_id == leitor_id, Emprestimo.status == ATIVO)
            .count()
        )

    def registrar(self, livro_id, leitor_id):
        # Duas escritas, um commit: ou o emprestimo nasce E o livro fica
        # indisponivel, ou nenhum dos dois. E' a mesma transacao que o
        # encontro 5 fazia com dois execute() e um commit().
        emprestimo = Emprestimo(livro_id=livro_id, leitor_id=leitor_id, status=ATIVO)
        self.db.add(emprestimo)

        livro = self.buscar_livro(livro_id)
        livro.disponivel = False

        self.db.commit()
        self.db.refresh(emprestimo)   # o id nasce no banco; sem isto vem None
        return emprestimo
