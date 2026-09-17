"""O Service funciona sem FastAPI, sem servidor e sem banco (encontro 4 de P3).

E' isto que a injecao do repositorio compra: as regras do emprestimo rodam
aqui com um repositorio de mentira, em memoria, e o `service.py` nao sabe a
diferenca -- e' o mesmo arquivo que em producao recebe o SQLAlchemy.

Desde o encontro 7 (Strategy) o Service recebe tambem o tipo do leitor, e
quantos livros e quantos dias vem da politica desse tipo. Os quatro primeiros
testes sao os do encontro 5, com um aluno: o limite de 3 e' o dele.
"""
import inspect
from datetime import date, timedelta

import pytest

from app.emprestimos import service as service_py
from app.emprestimos.erros import (
    LimiteDeEmprestimosAtingido,
    LivroIndisponivel,
    LivroNaoEncontrado,
)
from app.emprestimos.politicas import POLITICAS, politica_para
from app.emprestimos.service import EmprestimoService


class Livro:
    """O que o repositorio devolve: um objeto com id, titulo e disponivel."""

    def __init__(self, id, titulo, disponivel=True):
        self.id = id
        self.titulo = titulo
        self.disponivel = disponivel


class RepositorioEmMemoria:
    """O repositorio do encontro 4: duas linhas de estado dentro do processo."""

    def __init__(self):
        self.livros = {
            1: Livro(1, "Dom Casmurro"),
            2: Livro(2, "Grande Sertao", disponivel=False),
            3: Livro(3, "Memorias Postumas"),
            4: Livro(4, "Vidas Secas"),
            5: Livro(5, "O Cortico"),
        }
        self.emprestimos = []

    def buscar_livro(self, livro_id):
        return self.livros.get(livro_id)

    def contar_ativos(self, leitor_id):
        return sum(
            1
            for e in self.emprestimos
            if e["leitor_id"] == leitor_id and e["status"] == "ativo"
        )

    def registrar(self, livro_id, leitor_id, tipo_leitor, devolver_ate):
        self.livros[livro_id].disponivel = False
        emprestimo = {
            "id": len(self.emprestimos) + 1,
            "livro_id": livro_id,
            "leitor_id": leitor_id,
            "tipo_leitor": tipo_leitor,
            "devolver_ate": devolver_ate,
            "status": "ativo",
        }
        self.emprestimos.append(emprestimo)
        return emprestimo


def test_empresta_um_livro_livre():
    repositorio = RepositorioEmMemoria()
    service = EmprestimoService(repositorio)

    emprestimo = service.emprestar(1, 42, "aluno")

    assert emprestimo["status"] == "ativo"
    assert repositorio.livros[1].disponivel is False


def test_recusa_livro_que_nao_existe():
    service = EmprestimoService(RepositorioEmMemoria())
    with pytest.raises(LivroNaoEncontrado):
        service.emprestar(99, 42, "aluno")


def test_recusa_livro_que_ja_esta_com_alguem():
    service = EmprestimoService(RepositorioEmMemoria())
    with pytest.raises(LivroIndisponivel):
        service.emprestar(2, 42, "aluno")


def test_recusa_o_quarto_livro_do_mesmo_leitor():
    service = EmprestimoService(RepositorioEmMemoria())
    for livro_id in (1, 3, 4):
        service.emprestar(livro_id, 42, "aluno")

    with pytest.raises(LimiteDeEmprestimosAtingido):
        service.emprestar(5, 42, "aluno")

    # o limite e' por leitor: outro leitor ainda leva o 5
    assert service.emprestar(5, 7, "aluno")["leitor_id"] == 7


# O quadro do encontro 7: tipo de leitor, livros ao mesmo tempo, dias de prazo.
HOJE = date.today()
QUADRO = [
    ("aluno", 3, 14),
    ("professor", 5, 60 if HOJE.month in (7, 12) else 30),
    ("servidor", 4, 21),
    ("visitante", 1, 7),
]


@pytest.mark.parametrize("tipo_leitor, limite, prazo", QUADRO)
def test_cada_tipo_tem_o_seu_limite_e_o_seu_prazo(tipo_leitor, limite, prazo):
    repositorio = RepositorioEmMemoria()
    for livro_id in range(6, 12):              # seis livros novos, todos livres
        repositorio.livros[livro_id] = Livro(livro_id, f"Livro {livro_id}")
    service = EmprestimoService(repositorio)

    for livro_id in range(6, 6 + limite):
        emprestimo = service.emprestar(livro_id, 42, tipo_leitor)
        assert emprestimo["tipo_leitor"] == tipo_leitor
        assert emprestimo["devolver_ate"] == HOJE + timedelta(days=prazo)

    # um livro a mais que o limite do tipo
    with pytest.raises(LimiteDeEmprestimosAtingido):
        service.emprestar(6 + limite, 42, tipo_leitor)


def test_no_recesso_o_prazo_do_professor_dobra():
    # A politica recebe o `hoje` de fora: por isso da' para testar julho em setembro.
    professor = politica_para("professor")
    assert professor.prazo_em_dias(date(2026, 6, 30)) == 30
    assert professor.prazo_em_dias(date(2026, 7, 1)) == 60
    assert professor.prazo_em_dias(date(2026, 12, 31)) == 60
    assert professor.prazo_em_dias(date(2027, 1, 1)) == 30


def test_o_service_nao_conhece_nenhum_tipo_de_leitor():
    # Nem "aluno" nem PoliticaAluno: quem sabe dos tipos e' o politicas.py.
    codigo = inspect.getsource(service_py).lower()
    for tipo_leitor in POLITICAS:
        assert tipo_leitor not in codigo
