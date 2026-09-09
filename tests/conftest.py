"""Cada teste comeca com o banco zerado e o acervo inicial dentro.

A URL do banco e' definida ANTES de importar o app: o `database.py` le
DATABASE_URL na hora do import e, sem valor, se recusa a subir -- de
proposito (passo 5 do tutorial de Web III). Aqui ela aponta para um SQLite
descartavel numa pasta temporaria, para nenhum teste encostar no
`biblioteca.db` de verdade.
"""
import os
import tempfile

_PASTA = tempfile.mkdtemp(prefix="biblioteca-teste-")
os.environ["DATABASE_URL"] = "sqlite:///" + os.path.join(_PASTA, "teste.db").replace("\\", "/")

import pytest                                   # noqa: E402
from fastapi.testclient import TestClient       # noqa: E402

from app.database import Base, SessionLocal, engine   # noqa: E402
from app.livros.acervo import semear_acervo_inicial   # noqa: E402
from app.main import app                              # noqa: E402


@pytest.fixture
def client():
    """Um cliente HTTP sobre um banco recem-criado, com os cinco livros."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        semear_acervo_inicial(db)
    finally:
        db.close()
    return TestClient(app)
