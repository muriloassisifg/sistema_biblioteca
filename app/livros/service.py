"""As regras da biblioteca, e mais nada.

Este arquivo decide. Ele nao levanta erro de protocolo, nao monta consulta
e nao abre conexao: quem fala HTTP e o controller, quem fala SQL e o
repository. Um dia essas regras podem ser chamadas por um script de
importacao, sem requisicao nenhuma para responder -- e vao funcionar.

O `db` atravessa este arquivo sem ser aberto: o Service so o repassa para
o repository, que e quem sabe o que fazer com ele.
"""
from . import repository
from .erros import (
    CampoNaoEditavel,
    TituloJaCadastrado,
    LivroEmprestado,
    LivroNaoEncontrado,
)

RN02_PROIBIDO = "disponivel"   # quem empresta e o emprestimo


def listar(db):
    return repository.listar(db)


def buscar(db, livro_id):
    livro = repository.buscar(db, livro_id)
    if livro is None:
        raise LivroNaoEncontrado(f"Livro {livro_id} nao esta no acervo")
    return livro


def criar(db, dados):
    # RN01: o mesmo titulo nao entra duas vezes no acervo.
    if repository.buscar_por_titulo(db, dados["titulo"]):
        raise TituloJaCadastrado(f"Ja existe um livro chamado {dados['titulo']}")
    return repository.criar(db, dados)


def atualizar(db, livro_id, mudancas):
    livro = buscar(db, livro_id)

    novo_titulo = mudancas.get("titulo")
    if novo_titulo and novo_titulo != livro.titulo:
        if repository.buscar_por_titulo(db, novo_titulo):
            raise TituloJaCadastrado(f"Ja existe um livro chamado {novo_titulo}")

    if RN02_PROIBIDO in mudancas:
        raise CampoNaoEditavel("disponivel nao se edita pelo catalogo")

    return repository.atualizar(db, livro, mudancas)


def apagar(db, livro_id):
    livro = buscar(db, livro_id)
    # RN03: livro que esta com um leitor nao some do acervo.
    if not livro.disponivel:
        raise LivroEmprestado(f"Livro {livro_id} esta emprestado")
    repository.apagar(db, livro)
