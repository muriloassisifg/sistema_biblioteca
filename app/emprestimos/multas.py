"""A multa por atraso: um valor por dia e um teto, que vem do multa.json.

Um assunto so' -- a multa -- com as regras dele. Os numeros moram em
`multa.json`, como os do emprestimo moram em `regras.json`: a classe recebe os
seus ao nascer, no `criar` (o Factory Method do encontro 8). Nao sabe de HTTP,
de banco nem de aviso ao leitor.
"""
import json
from pathlib import Path

ARQUIVO_DA_MULTA = Path(__file__).with_name("multa.json")


class MultaService:
    def __init__(self, por_dia, teto):
        self.por_dia = por_dia
        self.teto = teto

    @classmethod
    def criar(cls, regras):
        return cls(por_dia=regras["por_dia"], teto=regras["teto"])

    def dias_de_atraso(self, devolver_ate, hoje):
        # Os emprestimos de antes da migracao do Strategy nao tem data de
        # devolucao (a coluna e' nula): nao ha prazo a estourar.
        if devolver_ate is None:
            return 0
        return max((hoje - devolver_ate).days, 0)

    def calcular(self, dias_de_atraso):
        return min(dias_de_atraso * self.por_dia, self.teto)


def carregar_multa():
    """Le o multa.json a cada uso: mudar um numero nao exige reiniciar."""
    with open(ARQUIVO_DA_MULTA, encoding="utf-8") as arquivo:
        return json.load(arquivo)
