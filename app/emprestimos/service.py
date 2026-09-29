"""As regras de negocio do emprestimo -- sem nenhum `if tipo_leitor == ...`.

O Service pergunta a politica quantos livros e quantos dias; quem e' a
politica, ele nao sabe. Acrescentar um tipo de leitor nao abre este arquivo.

Ele tambem sabe registrar a devolucao. So' isso: a multa e o aviso ao leitor
sao outros assuntos, e moram em outros arquivos.
"""
from datetime import date, timedelta

from .erros import (
    EmprestimoJaDevolvido,
    EmprestimoNaoEncontrado,
    LimiteDeEmprestimosAtingido,
    LivroIndisponivel,
    LivroNaoEncontrado,
)
from .politicas import politica_para


class EmprestimoService:
    def __init__(self, repositorio):
        # Nao e a sessao do banco: e qualquer coisa que saiba buscar e salvar.
        self.repositorio = repositorio

    def emprestar(self, livro_id, leitor_id, tipo_leitor):
        politica = politica_para(tipo_leitor)   # a escolha, feita em outro lugar

        livro = self.repositorio.buscar_livro(livro_id)
        if livro is None:
            raise LivroNaoEncontrado(f"Livro {livro_id} nao esta no acervo")
        if not livro.disponivel:
            raise LivroIndisponivel(f"Livro {livro_id} ja esta emprestado")

        ativos = self.repositorio.contar_ativos(leitor_id)
        if ativos >= politica.limite_de_livros():
            raise LimiteDeEmprestimosAtingido(
                f"Leitor {leitor_id} ja esta com {ativos} livros"
            )

        hoje = date.today()
        devolver_ate = hoje + timedelta(days=politica.prazo_em_dias(hoje))
        return self.repositorio.registrar(
            livro_id, leitor_id, tipo_leitor, devolver_ate
        )

    def devolver(self, emprestimo_id):
        emprestimo = self.repositorio.buscar_emprestimo(emprestimo_id)
        if emprestimo is None:
            raise EmprestimoNaoEncontrado(f"Emprestimo {emprestimo_id} nao existe")
        if not emprestimo.ativo:
            raise EmprestimoJaDevolvido(f"Emprestimo {emprestimo_id} ja foi devolvido")

        self.repositorio.marcar_devolvido(emprestimo.id, emprestimo.livro_id)
        return emprestimo
