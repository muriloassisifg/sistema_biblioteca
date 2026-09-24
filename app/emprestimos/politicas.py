"""As politicas de emprestimo: Strategy para decidir, Factory Method para criar.

Os numeros moram em `regras.json`, ao lado deste arquivo. Com eles do lado de
fora, cada politica precisa receber os seus dados ao nascer -- e quais dados,
depende da classe. Quem sabe criar cada politica e' a propria classe, no
metodo `criar`: e' o Factory Method. `politica_para` so' escolhe a classe e
pede a ela que se crie; nenhuma chave do regras.json aparece la'.
"""
import json
from datetime import date
from pathlib import Path

from .erros import TipoDeLeitorDesconhecido

ARQUIVO_DE_REGRAS = Path(__file__).with_name("regras.json")


class PoliticaDeEmprestimo:
    """O contrato: toda politica responde a estas duas perguntas -- e sabe se criar."""

    @classmethod
    def criar(cls, regras):
        """O Factory Method: monta a politica a partir do trecho dela no regras.json."""
        raise NotImplementedError

    def prazo_em_dias(self, hoje):
        """Por quantos dias o livro fica com o leitor, contando de hoje."""
        raise NotImplementedError

    def limite_de_livros(self):
        """Quantos livros o leitor pode ter emprestados ao mesmo tempo."""
        raise NotImplementedError


class PoliticaPadrao(PoliticaDeEmprestimo):
    """Um prazo e um limite, e nada mais: aluno, servidor, visitante."""

    def __init__(self, dias, livros):
        self.dias = dias
        self.livros = livros

    @classmethod
    def criar(cls, regras):
        return cls(dias=regras["dias"], livros=regras["livros"])

    def prazo_em_dias(self, hoje):
        return self.dias

    def limite_de_livros(self):
        return self.livros


class PoliticaProfessor(PoliticaDeEmprestimo):
    """O prazo muda no recesso -- e o recesso vem do regras.json."""

    def __init__(self, dias, livros, dias_no_recesso, inicio_do_recesso, fim_do_recesso):
        self.dias = dias
        self.livros = livros
        self.dias_no_recesso = dias_no_recesso
        self.inicio_do_recesso = inicio_do_recesso
        self.fim_do_recesso = fim_do_recesso

    @classmethod
    def criar(cls, regras):
        # No JSON a data e' texto; quem transforma em date e' quem sabe precisar dela.
        return cls(
            dias=regras["dias"],
            livros=regras["livros"],
            dias_no_recesso=regras["dias_no_recesso"],
            inicio_do_recesso=date.fromisoformat(regras["inicio_do_recesso"]),
            fim_do_recesso=date.fromisoformat(regras["fim_do_recesso"]),
        )

    def prazo_em_dias(self, hoje):
        if self.inicio_do_recesso <= hoje <= self.fim_do_recesso:
            return self.dias_no_recesso
        return self.dias

    def limite_de_livros(self):
        return self.livros


# So' os tipos que nascem de um jeito PROPRIO. Os outros usam a PoliticaPadrao.
CLASSES = {
    "professor": PoliticaProfessor,
}


def carregar_regras():
    """Le o regras.json a cada pedido: mudar um numero nao exige reiniciar."""
    with open(ARQUIVO_DE_REGRAS, encoding="utf-8") as arquivo:
        return json.load(arquivo)


def politica_para(tipo_leitor):
    """Escolhe a classe e pede a ela que se crie. Nao sabe quais dados cada uma usa."""
    regras = carregar_regras()
    if tipo_leitor not in regras:
        aceitos = ", ".join(regras)
        raise TipoDeLeitorDesconhecido(
            f"Tipo de leitor desconhecido: {tipo_leitor!r} (aceitos: {aceitos})"
        )
    classe = CLASSES.get(tipo_leitor, PoliticaPadrao)
    return classe.criar(regras[tipo_leitor])
