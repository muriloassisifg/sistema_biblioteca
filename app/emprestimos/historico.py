"""Uma linha por devolucao, para o relatorio do fim do mes."""
from datetime import date

ARQUIVO = "devolucoes.txt"


class Historico:
    def registrar(self, emprestimo_id, dias_de_atraso, multa):
        with open(ARQUIVO, "a", encoding="utf-8") as arquivo:
            arquivo.write(f"{date.today()};{emprestimo_id};{dias_de_atraso};{multa:.2f}\n")
