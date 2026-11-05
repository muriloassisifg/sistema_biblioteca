"""As regras de conta e de login, e mais nada.

Nenhum HTTP, nenhum SQL e nenhum JWT aqui: o hash e o token vem de
app/seguranca.py; a consulta vem do repository. O service so' decide.
"""
from .. import seguranca
from . import repository
from .erros import CredenciaisInvalidas, EmailJaCadastrado


def cadastrar(db, dados):
    # RN04: um e-mail, uma conta.
    if repository.buscar_por_email(db, dados["email"]):
        raise EmailJaCadastrado(f"Ja existe uma conta com o e-mail {dados['email']}")

    # A senha em texto chega ate' aqui e NAO passa deste ponto: o que vai
    # para o banco e' o hash.
    senha = dados.pop("senha")
    return repository.criar(db, {**dados, "senha_hash": seguranca.gerar_hash(senha)})


def autenticar(db, email, senha):
    usuario = repository.buscar_por_email(db, email)
    if usuario is None or not seguranca.conferir_senha(senha, usuario.senha_hash):
        raise CredenciaisInvalidas("E-mail ou senha incorretos")
    return usuario
