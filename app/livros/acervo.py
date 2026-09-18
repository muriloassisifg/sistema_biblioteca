"""Os cinco livros com que a biblioteca nasce -- so' para a aula.

Sao os mesmos do encontro 5 de Programacao III, para que as tabelas de
"o que provar pelo /docs" dos dois README continuem valendo: o livro 1 esta'
livre, o livro 2 ja' nasce emprestado, o 99 nao existe.

Desde o encontro 7 de Web III todo livro tem dono, e acervo sem dono nao e'
visto por ninguem. Por isso estes cinco nao nascem mais quando a aplicacao
sobe: nascem para a PRIMEIRA pessoa que se cadastra.

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


def semear_acervo_inicial(db: Session, dono_id: int):
    """Poe o acervo inicial no nome de `dono_id`, se a tabela estiver vazia.

    Quem chama e' o cadastro de usuario: quem se cadastra primeiro encontra a
    biblioteca montada; do segundo em diante a tabela ja' tem livro, e esta
    funcao nao toca nela -- cada um comeca o proprio acervo do zero.

    E' MATERIAL DE AULA, nao regra de producao: numa biblioteca de verdade o
    acervo entra por importacao ou pelas maos de quem cataloga, nunca de
    brinde para quem chegou primeiro.
    """
    if db.query(Livro).count() > 0:
        return
    db.add_all(Livro(**dados, dono_id=dono_id) for dados in ACERVO_INICIAL)
    db.commit()
