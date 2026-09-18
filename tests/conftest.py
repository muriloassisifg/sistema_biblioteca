"""Cada teste comeca com o banco zerado -- vazio mesmo, sem usuario e sem
livro. Quem traz os cinco livros e' o cadastro da Ana, no fixture `client`:
desde que o livro tem dono, o acervo inicial nasce para a PRIMEIRA pessoa
que se cadastra, e nao quando a aplicacao sobe.

A URL do banco e a SECRET_KEY sao definidas ANTES de importar o app: o
`database.py` e o `seguranca.py` as leem na hora do import e, sem valor, se
recusam a subir -- de proposito. Aqui apontam para um SQLite descartavel numa
pasta temporaria, para nenhum teste encostar no `biblioteca.db` de verdade.

As tabelas dos testes nascem do create_all, e nao das migracoes: e' mais
rapido, e o test_migracoes.py e' quem prova que o `alembic upgrade head`
produz o mesmo esquema.
"""
import os
import tempfile

_PASTA = tempfile.mkdtemp(prefix="biblioteca-teste-")
os.environ["DATABASE_URL"] = "sqlite:///" + os.path.join(_PASTA, "teste.db").replace("\\", "/")
os.environ["SECRET_KEY"] = "chave-so-dos-testes-com-mais-de-trinta-e-dois-caracteres"

import pytest                                   # noqa: E402
from fastapi.testclient import TestClient       # noqa: E402

from app.database import Base, engine           # noqa: E402
from app.main import app                        # noqa: E402

ANA = {"nome": "Ana", "email": "ana@ifg.edu.br", "senha": "segredo1"}
BRUNO = {"nome": "Bruno", "email": "bruno@ifg.edu.br", "senha": "segredo2"}


def entrar(cliente, pessoa):
    """Cadastra e faz login: o token passa a ir no cabecalho de toda chamada
    desse cliente, como o /docs faz depois do Authorize."""
    assert cliente.post("/usuarios/", json=pessoa).status_code == 201
    r = cliente.post(
        "/usuarios/login",
        data={"username": pessoa["email"], "password": pessoa["senha"]},
    )
    assert r.status_code == 200
    cliente.headers.update({"Authorization": "Bearer " + r.json()["access_token"]})
    return cliente


@pytest.fixture
def anonimo():
    """Um cliente HTTP sobre um banco recem-criado e vazio, SEM token: e' com
    ele que se prova que a porta esta' trancada."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    return TestClient(app)


@pytest.fixture
def client(anonimo):
    """O mesmo cliente, depois de cadastrar a Ana e fazer login. Por ser a
    primeira, ela recebe os cinco livros do acervo inicial."""
    return entrar(anonimo, ANA)


@pytest.fixture
def do_bruno(client):
    """A SEGUNDA pessoa, no mesmo banco: acervo vazio e o 404 no livro da Ana.

    E' um TestClient novo, e nao o da Ana com outro cabecalho, para os dois
    cracha's valerem ao mesmo tempo -- e' assim que se enxerga a fronteira.
    """
    return entrar(TestClient(app), BRUNO)
