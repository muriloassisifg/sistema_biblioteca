"""Os cinco livros com que a biblioteca nasce -- so' para a aula.

Sao os mesmos do encontro 5 de Programacao III, para que as tabelas de
"o que provar pelo /docs" dos dois README continuem valendo: o livro 1 esta'
livre, o livro 2 ja' nasce emprestado, o 99 nao existe.

Isto NAO e' o database.py: la' mora a infraestrutura (conexao, sessao,
Base), que e' do projeto inteiro. Dados de exemplo sao assunto da
funcionalidade que os entende -- livros.
"""
from sqlalchemy.orm import Session

from .models import Livro

ACERVO_INICIAL = [
    {"id": 1, "titulo": "Dom Casmurro", "ano": 1899, "disponivel": True},
    {"id": 2, "titulo": "Grande Sertao: Veredas", "ano": 1956, "disponivel": False},
    {"id": 3, "titulo": "Memorias Postumas", "ano": 1881, "disponivel": True},
    {"id": 4, "titulo": "Vidas Secas", "ano": 1938, "disponivel": True},
    {"id": 5, "titulo": "O Cortico", "ano": 1890, "disponivel": True},
]


def semear_acervo_inicial(db: Session):
    """Poe o acervo inicial se a tabela estiver vazia; senao, nao toca nela."""
    if db.query(Livro).count() > 0:
        return
    db.add_all(Livro(**dados) for dados in ACERVO_INICIAL)
    db.commit()
