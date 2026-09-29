"""A fachada da devolucao: uma chamada so' para uma sequencia de pecas.

Quem quer devolver um livro chama `devolver` e pronto. Quais pecas entram, e
em que ordem, e' assunto desta classe -- e so' dela.

Ela NAO tem regra nenhuma: a multa mora no MultaService, o texto do aviso no
Notificador. A fachada so' chama cada peca, na ordem, e junta o resultado.
"""
from datetime import date


class DevolucaoFacade:
    def __init__(self, service, multas, notificador, historico):
        self.service = service
        self.multas = multas
        self.notificador = notificador
        self.historico = historico

    def devolver(self, emprestimo_id):
        emprestimo = self.service.devolver(emprestimo_id)
        dias = self.multas.dias_de_atraso(emprestimo.devolver_ate, date.today())
        multa = self.multas.calcular(dias)
        aviso = self.notificador.devolucao_registrada(
            emprestimo.leitor_id, emprestimo.livro_id, multa
        )
        self.historico.registrar(emprestimo.id, dias, multa)
        return {
            "emprestimo_id": emprestimo.id,
            "livro_id": emprestimo.livro_id,
            "dias_de_atraso": dias,
            "multa": multa,
            "aviso": aviso,
        }
