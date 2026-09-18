"""As regras de conta e de login, e mais nada.

Nenhum HTTP, nenhum SQL e nenhum JWT aqui: o hash e o token vem de
app/seguranca.py; a consulta vem do repository. O service so' decide.
"""
from .. import seguranca
from ..livros.acervo import semear_acervo_inicial
from . import repository
from .erros import CredenciaisInvalidas, EmailJaCadastrado


def cadastrar(db, dados):
    # RN04: um e-mail, uma conta.
    if repository.buscar_por_email(db, dados["email"]):
        raise EmailJaCadastrado(f"Ja existe uma conta com o e-mail {dados['email']}")

    # A senha em texto chega ate' aqui e NAO passa deste ponto: o que vai
    # para o banco e' o hash.
    senha = dados.pop("senha")
    usuario = repository.criar(db, {**dados, "senha_hash": seguranca.gerar_hash(senha)})

    # A UNICA linha deste arquivo que olha para outra funcionalidade, e ela e'
    # MATERIAL DE AULA: quem se cadastra primeiro encontra os cinco livros de
    # exemplo ja' no proprio acervo; do segundo em diante, nada -- a tabela
    # ja' tem livro. Antes do dono isso acontecia quando a aplicacao subia;
    # agora precisa de alguem para ser o dono. Num sistema de verdade esta
    # linha nao existe: cada um cataloga o proprio acervo.
    semear_acervo_inicial(db, usuario.id)
    return usuario


def autenticar(db, email, senha):
    usuario = repository.buscar_por_email(db, email)
    if usuario is None or not seguranca.conferir_senha(senha, usuario.senha_hash):
        raise CredenciaisInvalidas("E-mail ou senha incorretos")
    return usuario
