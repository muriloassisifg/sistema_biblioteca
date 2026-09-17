class ErroDeEmprestimo(Exception):
    """Qualquer recusa da biblioteca na hora de emprestar um livro."""


class LivroNaoEncontrado(ErroDeEmprestimo):
    """Pediram um livro que nao esta no acervo."""


class LivroIndisponivel(ErroDeEmprestimo):
    """O livro existe, mas ja esta com outra pessoa."""


class LimiteDeEmprestimosAtingido(ErroDeEmprestimo):
    """O leitor ja esta com o maximo de livros permitido para o tipo dele."""


class TipoDeLeitorDesconhecido(ErroDeEmprestimo):
    """Pediram um tipo de leitor que a biblioteca nao conhece."""
