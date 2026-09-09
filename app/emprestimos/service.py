from .erros import (
    LimiteDeEmprestimosAtingido,
    LivroIndisponivel,
    LivroNaoEncontrado,
)


class EmprestimoService:
    MAXIMO_POR_LEITOR = 3

    def __init__(self, repositorio):
        # Nao e a sessao do banco: e qualquer coisa que saiba buscar e salvar.
        self.repositorio = repositorio

    def emprestar(self, livro_id, leitor_id):
        livro = self.repositorio.buscar_livro(livro_id)
        if livro is None:
            raise LivroNaoEncontrado(f"Livro {livro_id} nao esta no acervo")
        if not livro.disponivel:
            raise LivroIndisponivel(f"Livro {livro_id} ja esta emprestado")

        ativos = self.repositorio.contar_ativos(leitor_id)
        if ativos >= self.MAXIMO_POR_LEITOR:
            raise LimiteDeEmprestimosAtingido(
                f"Leitor {leitor_id} ja esta com {ativos} livros"
            )

        return self.repositorio.registrar(livro_id, leitor_id)
