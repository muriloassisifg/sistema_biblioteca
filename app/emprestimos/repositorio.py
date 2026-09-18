"""A unica camada que sabe consultar emprestimos e livros no banco.

Terceira implementacao do mesmo repositorio: em memoria (encontro 4 de P3),
SQLite escrito a mao (encontro 5) e agora SQLAlchemy -- o mesmo banco e a
mesma sessao que a funcionalidade de livros usa. O Service continua chamando
os mesmos tres metodos, com os mesmos nomes, e recebendo os mesmos tipos de
volta -- e por isso nao mudou nem um caractere pela terceira vez.

No encontro 7 (Strategy) o `registrar` ganhou dois campos: o tipo do leitor
e a data de devolucao. Repare no que ele NAO sabe: como essa data foi
calculada. Ele recebe a data pronta (um `date`) e guarda -- regra de prazo
nao e' assunto de quem fala com o banco.

No encontro 7 de Web III ele passou a nascer com um dono: o `buscar_livro`
so' enxerga o acervo de quem esta' logado. De novo sem abrir o `service.py`
-- pedir o livro de outro bibliotecario cai no mesmo "livro nao encontrado"
de sempre.

A conexao e a sessao NAO estao aqui: moram em `app/database.py`, porque sao
do projeto inteiro. Aqui ficam so' as consultas desta funcionalidade.
"""
from sqlalchemy.orm import Session

from ..livros.models import Livro
from .models import Emprestimo

ATIVO = "ativo"        # a string que o legado errava em um lugar so'


class RepositorioSQLAlchemy:
    """Recebe a sessao ja' aberta e o dono do acervo: quem escolhe os dois
    e' o dependencias.py."""

    def __init__(self, db: Session, dono_id):
        self.db = db
        self.dono_id = dono_id      # so' se empresta livro do proprio acervo

    def buscar_livro(self, livro_id):
        # O que sai daqui e' um objeto (o Livro do SQLAlchemy), nunca a
        # linha crua do banco -- igual ao encontro 5.
        #
        # O filtro do dono e' do encontro 7 de Web III: daqui de dentro, o
        # livro de outro bibliotecario simplesmente nao existe. Quem levanta
        # o LivroNaoEncontrado (404) continua sendo o Service, com o mesmo
        # `if livro is None` de sempre -- ele nunca soube de dono nenhum.
        return (
            self.db.query(Livro)
            .filter(Livro.id == livro_id, Livro.dono_id == self.dono_id)
            .first()
        )

    def contar_ativos(self, leitor_id):
        return (
            self.db.query(Emprestimo)
            .filter(Emprestimo.leitor_id == leitor_id, Emprestimo.status == ATIVO)
            .count()
        )

    def registrar(self, livro_id, leitor_id, tipo_leitor, devolver_ate):
        # Duas escritas, um commit: ou o emprestimo nasce E o livro fica
        # indisponivel, ou nenhum dos dois. E' a mesma transacao que o
        # encontro 5 fazia com dois execute() e um commit().
        emprestimo = Emprestimo(
            livro_id=livro_id,
            leitor_id=leitor_id,
            tipo_leitor=tipo_leitor,
            devolver_ate=devolver_ate,
            status=ATIVO,
        )
        self.db.add(emprestimo)

        livro = self.buscar_livro(livro_id)
        livro.disponivel = False

        self.db.commit()
        self.db.refresh(emprestimo)   # o id nasce no banco; sem isto vem None
        return emprestimo
