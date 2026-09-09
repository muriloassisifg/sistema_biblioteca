"""O Service funciona sem FastAPI, sem servidor e sem banco (encontro 4 de P3).

E' isto que a injecao do repositorio compra: as regras do emprestimo rodam
aqui com um repositorio de mentira, em memoria, e o `service.py` nao sabe a
diferenca -- e' o mesmo arquivo que em producao recebe o SQLAlchemy.
"""
import pytest

from app.emprestimos.erros import (
    LimiteDeEmprestimosAtingido,
    LivroIndisponivel,
    LivroNaoEncontrado,
)
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

    def registrar(self, livro_id, leitor_id):
        self.livros[livro_id].disponivel = False
        emprestimo = {
            "id": len(self.emprestimos) + 1,
            "livro_id": livro_id,
            "leitor_id": leitor_id,
            "status": "ativo",
        }
        self.emprestimos.append(emprestimo)
        return emprestimo


def test_empresta_um_livro_livre():
    repositorio = RepositorioEmMemoria()
    service = EmprestimoService(repositorio)

    emprestimo = service.emprestar(1, 42)

    assert emprestimo["status"] == "ativo"
    assert repositorio.livros[1].disponivel is False


def test_recusa_livro_que_nao_existe():
    service = EmprestimoService(RepositorioEmMemoria())
    with pytest.raises(LivroNaoEncontrado):
        service.emprestar(99, 42)


def test_recusa_livro_que_ja_esta_com_alguem():
    service = EmprestimoService(RepositorioEmMemoria())
    with pytest.raises(LivroIndisponivel):
        service.emprestar(2, 42)


def test_recusa_o_quarto_livro_do_mesmo_leitor():
    service = EmprestimoService(RepositorioEmMemoria())
    for livro_id in (1, 3, 4):
        service.emprestar(livro_id, 42)

    with pytest.raises(LimiteDeEmprestimosAtingido):
        service.emprestar(5, 42)

    # o limite e' por leitor: outro leitor ainda leva o 5
    assert service.emprestar(5, 7)["leitor_id"] == 7
