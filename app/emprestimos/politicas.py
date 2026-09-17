"""As politicas de emprestimo: o padrao Strategy dentro da biblioteca.

Cada tipo de leitor tem um jeito proprio de decidir duas coisas -- por quantos
dias leva o livro e quantos pode levar ao mesmo tempo. Aqui cada jeito vira
um objeto, e todos respondem as MESMAS duas perguntas. O Service recebe um
deles e pergunta; com qual esta' falando, ele nao sabe nem precisa saber.

A pergunta "que tipo de leitor e'?" existe no sistema inteiro uma vez so':
em `politica_para`, no fim deste arquivo.
"""
from .erros import TipoDeLeitorDesconhecido


class PoliticaDeEmprestimo:
    """O contrato: toda politica responde a estas duas perguntas.

    O Service so' conhece esta classe. As de baixo existem para ele sem nome.
    """

    def prazo_em_dias(self, hoje):
        """Por quantos dias o livro fica com o leitor, contando de hoje."""
        raise NotImplementedError

    def limite_de_livros(self):
        """Quantos livros o leitor pode ter emprestados ao mesmo tempo."""
        raise NotImplementedError


class PoliticaAluno(PoliticaDeEmprestimo):
    def prazo_em_dias(self, hoje):
        return 14

    def limite_de_livros(self):
        return 3            # o MAXIMO_POR_LEITOR do encontro 4 morava aqui


class PoliticaProfessor(PoliticaDeEmprestimo):
    def prazo_em_dias(self, hoje):
        if hoje.month in (7, 12):      # recesso: o prazo dobra
            return 60
        return 30

    def limite_de_livros(self):
        return 5


class PoliticaServidor(PoliticaDeEmprestimo):
    def prazo_em_dias(self, hoje):
        return 21

    def limite_de_livros(self):
        return 4


class PoliticaVisitante(PoliticaDeEmprestimo):
    """Entrou depois das outras tres -- e nenhum outro arquivo foi aberto."""

    def prazo_em_dias(self, hoje):
        return 7

    def limite_de_livros(self):
        return 1


# O unico lugar do sistema que sabe quais tipos de leitor existem.
POLITICAS = {
    "aluno": PoliticaAluno(),
    "professor": PoliticaProfessor(),
    "servidor": PoliticaServidor(),
    "visitante": PoliticaVisitante(),
}


def politica_para(tipo_leitor):
    """Troca o nome do tipo pela politica dele. A escolha acontece aqui, e so' aqui."""
    if tipo_leitor not in POLITICAS:
        aceitos = ", ".join(POLITICAS)
        raise TipoDeLeitorDesconhecido(
            f"Tipo de leitor desconhecido: {tipo_leitor!r} (aceitos: {aceitos})"
        )
    return POLITICAS[tipo_leitor]
