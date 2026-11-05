class ErroDeLivro(Exception):
    """Qualquer recusa do acervo. Quem traduz para HTTP e o controller."""


class LivroNaoEncontrado(ErroDeLivro):
    """Pediram um livro que nao esta no acervo."""


class TituloJaCadastrado(ErroDeLivro):
    """Ja existe um livro com esse titulo no acervo."""


class CampoNaoEditavel(ErroDeLivro):
    """Tentaram editar pelo catalogo um campo que nao e do catalogo."""


class LivroEmprestado(ErroDeLivro):
    """Nao se apaga livro que esta com um leitor."""
