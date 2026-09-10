"""Cada teste comeca com o banco zerado e o acervo inicial dentro -- e, no
fixture `client`, ja' com a Ana cadastrada e logada.

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

from app.database import Base, SessionLocal, engine   # noqa: E402
from app.livros.acervo import semear_acervo_inicial   # noqa: E402
from app.main import app                              # noqa: E402

ANA = {"nome": "Ana", "email": "ana@ifg.edu.br", "senha": "segredo1"}


@pytest.fixture
def anonimo():
    """Um cliente HTTP sobre um banco recem-criado, com os cinco livros --
    e SEM token: e' com ele que se prova que a porta esta' trancada."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        semear_acervo_inicial(db)
    finally:
        db.close()
    return TestClient(app)


@pytest.fixture
def client(anonimo):
    """O mesmo cliente, depois de cadastrar a Ana e fazer login: o token vai
    no cabecalho de toda chamada, como o /docs faz depois do Authorize."""
    assert anonimo.post("/usuarios/", json=ANA).status_code == 201
    r = anonimo.post("/usuarios/login", data={"username": ANA["email"], "password": ANA["senha"]})
    assert r.status_code == 200
    anonimo.headers.update({"Authorization": "Bearer " + r.json()["access_token"]})
    return anonimo
