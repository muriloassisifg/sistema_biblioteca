"""As regras da biblioteca, e mais nada.

Este arquivo decide. Ele nao levanta erro de protocolo, nao monta consulta
e nao abre conexao: quem fala HTTP e o controller, quem fala SQL e o
repository. Um dia essas regras podem ser chamadas por um script de
importacao, sem requisicao nenhuma para responder -- e vao funcionar.

Agora toda regra recebe o `usuario` -- quem esta' pedindo. Cada pessoa
enxerga e mexe so' no proprio acervo.
"""
from . import repository
from .erros import (
    CampoNaoEditavel,
    TituloJaCadastrado,
    LivroEmprestado,
    LivroNaoEncontrado,
)

RN02_PROIBIDO = "disponivel"   # quem empresta e o emprestimo


def listar(db, usuario, titulo=None, disponivel=None):
    return repository.listar(db, usuario.id, titulo, disponivel)


def buscar(db, usuario, livro_id):
    livro = repository.buscar(db, livro_id)
    # RN05: cada um enxerga so' o que e' seu. E' 404, e nao 403, de
    # proposito: dizer "existe, mas nao e' seu" ja' revela que existe.
    if livro is None or livro.dono_id != usuario.id:
        raise LivroNaoEncontrado(f"Livro {livro_id} nao esta no seu acervo")
    return livro


def criar(db, usuario, dados):
    # RN01: o mesmo titulo nao entra duas vezes no acervo -- no SEU acervo.
    if repository.buscar_por_titulo(db, usuario.id, dados["titulo"]):
        raise TituloJaCadastrado(f"Ja existe um livro chamado {dados['titulo']}")
    # O dono nao vem do pedido: vem de quem esta' logado.
    return repository.criar(db, {**dados, "dono_id": usuario.id})


def atualizar(db, usuario, livro_id, mudancas):
    livro = buscar(db, usuario, livro_id)

    novo_titulo = mudancas.get("titulo")
    if novo_titulo and novo_titulo != livro.titulo:
        if repository.buscar_por_titulo(db, usuario.id, novo_titulo):
            raise TituloJaCadastrado(f"Ja existe um livro chamado {novo_titulo}")

    if RN02_PROIBIDO in mudancas:
        raise CampoNaoEditavel("disponivel nao se edita pelo catalogo")

    return repository.atualizar(db, livro, mudancas)


def apagar(db, usuario, livro_id):
    livro = buscar(db, usuario, livro_id)
    # RN03: livro que esta com um leitor nao some do acervo.
    if not livro.disponivel:
        raise LivroEmprestado(f"Livro {livro_id} esta emprestado")
    repository.apagar(db, livro)
