"""Avisa o leitor. Aqui o "e-mail" e' uma linha no terminal do servidor."""


class Notificador:
    def devolucao_registrada(self, leitor_id, livro_id, multa=0.0):
        texto = f"Livro {livro_id} devolvido."
        if multa > 0:
            texto += f" Multa: R$ {multa:.2f}."
        print(f"[aviso para o leitor {leitor_id}] {texto}")
        return texto
