"""A multa por atraso: R$ 2,50 por dia, e no maximo R$ 50,00.

Um assunto so' -- a multa -- com as regras dele. Nao sabe de HTTP, de banco
nem de aviso ao leitor.
"""

VALOR_POR_DIA = 2.50
TETO = 50.00


class MultaService:
    def dias_de_atraso(self, devolver_ate, hoje):
        # Os emprestimos de antes da migracao do Strategy nao tem data de
        # devolucao (a coluna e' nula): nao ha prazo a estourar.
        if devolver_ate is None:
            return 0
        return max((hoje - devolver_ate).days, 0)

    def calcular(self, dias_de_atraso):
        return min(dias_de_atraso * VALOR_POR_DIA, TETO)
