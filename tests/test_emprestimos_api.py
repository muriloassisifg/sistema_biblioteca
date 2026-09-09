"""A tabela "o que provar em um minuto pelo /docs" do emprestimo (P3), e o
lugar onde as duas turmas se encontram: emprestar e' o unico jeito de um
livro ficar indisponivel.
"""
from app.database import SessionLocal
from app.emprestimos.models import Emprestimo


def emprestar(client, livro_id, leitor_id):
    return client.post("/emprestimos/", json={"livro_id": livro_id, "leitor_id": leitor_id})


def test_a_tabela_do_encontro_5(client):
    r = emprestar(client, 1, 42)
    assert r.status_code == 201
    assert r.json()["status"] == "ativo" and r.json()["livro_id"] == 1

    # o mesmo livro de novo, para qualquer leitor: ja' esta' emprestado
    r = emprestar(client, 1, 7)
    assert r.status_code == 409
    assert r.json()["detail"] == "Livro 1 ja esta emprestado"

    # nao esta' no acervo
    assert emprestar(client, 99, 42).status_code == 404

    # o 2 nasce indisponivel
    assert emprestar(client, 2, 42).status_code == 409

    # o leitor 42 ja' tem o 1; leva mais dois, e o quarto e' recusado
    assert emprestar(client, 3, 42).status_code == 201
    assert emprestar(client, 4, 42).status_code == 201
    r = emprestar(client, 5, 42)
    assert r.status_code == 409
    assert r.json()["detail"] == "Leitor 42 ja esta com 3 livros"

    # outro leitor ainda consegue o 5: o limite e' por leitor
    assert emprestar(client, 5, 7).status_code == 201


def test_onde_as_duas_turmas_se_encontram(client):
    assert emprestar(client, 1, 42).status_code == 201

    # o catalogo enxerga o emprestimo
    r = client.get("/livros/1")
    assert r.status_code == 200 and r.json()["disponivel"] is False

    # RN02: quem devolve e' o emprestimo, nao o catalogo
    assert client.patch("/livros/1", json={"disponivel": True}).status_code == 409
    # RN03: livro com leitor nao sai do acervo
    assert client.delete("/livros/1").status_code == 409
    # editar o catalogo continua permitido
    assert client.patch("/livros/1", json={"ano": 1900}).status_code == 200


def test_o_emprestimo_esta_no_banco_e_nao_na_memoria(client):
    assert emprestar(client, 1, 42).status_code == 201

    db = SessionLocal()
    try:
        registros = db.query(Emprestimo).all()
    finally:
        db.close()
    assert len(registros) == 1
    assert (registros[0].livro_id, registros[0].leitor_id, registros[0].status) == (1, 42, "ativo")
