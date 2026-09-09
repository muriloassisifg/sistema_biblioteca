"""A tabela "o que provar em um minuto pelo /docs" do catalogo (Web III),
rodando sozinha.
"""


def test_a_biblioteca_nasce_com_cinco_livros(client):
    r = client.get("/livros/")
    assert r.status_code == 200
    livros = r.json()
    assert [l["id"] for l in livros] == [1, 2, 3, 4, 5]
    assert livros[0]["titulo"] == "Dom Casmurro" and livros[0]["disponivel"] is True
    assert livros[1]["disponivel"] is False       # o 2 ja' nasce emprestado


def test_cadastro_e_as_tres_regras(client):
    r = client.post("/livros/", json={"titulo": "Quincas Borba", "ano": 1891})
    assert r.status_code == 201
    novo = r.json()["id"]

    # RN01: o mesmo titulo nao entra duas vezes -- e o detail e' a frase do service.
    r = client.post("/livros/", json={"titulo": "Quincas Borba", "ano": 1891})
    assert r.status_code == 409
    assert r.json()["detail"] == "Ja existe um livro chamado Quincas Borba"

    # corrigir o ano e' edicao de catalogo
    r = client.patch(f"/livros/{novo}", json={"ano": 1892})
    assert r.status_code == 200 and r.json()["ano"] == 1892

    # RN02: emprestar nao e' editar
    assert client.patch(f"/livros/{novo}", json={"disponivel": False}).status_code == 409

    # esta' no acervo e livre: pode sair
    assert client.delete(f"/livros/{novo}").status_code == 204
    assert client.get(f"/livros/{novo}").status_code == 404

    # um livro cadastrado ja' emprestado...
    r = client.post("/livros/", json={"titulo": "Quincas Borba", "ano": 1891, "disponivel": False})
    assert r.status_code == 201
    # RN03: ...nao some do acervo enquanto estiver com um leitor
    assert client.delete(f"/livros/{r.json()['id']}").status_code == 409


def test_o_schema_barra_antes_do_service(client):
    # 422 vem do schema: titulo curto demais, ano fora do intervalo
    assert client.post("/livros/", json={"titulo": "V", "ano": 1938}).status_code == 422
    assert client.post("/livros/", json={"titulo": "Vidas Secas", "ano": 1200}).status_code == 422


def test_livro_que_nao_existe(client):
    assert client.get("/livros/99").status_code == 404
    assert client.patch("/livros/99", json={"ano": 1900}).status_code == 404
    assert client.delete("/livros/99").status_code == 404
