"""A tabela "o que provar em um minuto pelo /docs" do catalogo (Web III),
rodando sozinha.

Desde o encontro 7 tudo aqui acontece DENTRO do acervo de quem esta' logado:
a Ana nao ve' os livros do Bruno, e o Bruno nao ve' os da Ana.
"""


def test_a_biblioteca_nasce_para_a_primeira_pessoa(client):
    r = client.get("/livros/")
    assert r.status_code == 200
    livros = r.json()

    # os cinco de sempre -- e agora em ordem de titulo, nao de id
    assert [l["titulo"] for l in livros] == [
        "Dom Casmurro",
        "Grande Sertao: Veredas",
        "Memorias Postumas",
        "O Cortico",
        "Vidas Secas",
    ]
    # todos da Ana, que foi quem se cadastrou primeiro
    assert {l["dono_id"] for l in livros} == {client.get("/usuarios/eu").json()["id"]}

    assert client.get("/livros/1").json()["disponivel"] is True
    assert client.get("/livros/2").json()["disponivel"] is False   # o 2 ja' nasce emprestado


def test_a_segunda_pessoa_nao_ganha_acervo_nenhum(do_bruno):
    # a tabela ja' tinha os livros da Ana: o acervo inicial nao nasce de novo
    assert do_bruno.get("/livros/").json() == []


def test_o_dono_vem_do_token_e_nao_do_corpo(client):
    # mesmo mandando dono_id no pedido: o schema de entrada nao tem esse
    # campo, o Pydantic descarta o que sobra, e o dono e' quem esta' logado
    r = client.post("/livros/", json={"titulo": "Quincas Borba", "ano": 1891, "dono_id": 99})
    assert r.status_code == 201
    assert r.json()["dono_id"] == client.get("/usuarios/eu").json()["id"]


def test_cada_um_enxerga_so_o_proprio_acervo(client, do_bruno):
    # RN05, e e' 404 de proposito: um 403 ja' contaria que o livro existe
    assert do_bruno.get("/livros/1").status_code == 404
    assert do_bruno.get("/livros/1").json()["detail"] == "Livro 1 nao esta no seu acervo"
    assert do_bruno.patch("/livros/1", json={"ano": 1900}).status_code == 404
    assert do_bruno.delete("/livros/1").status_code == 404
    assert do_bruno.get("/livros/?titulo=casmurro").json() == []

    # RN01 vale DENTRO de cada acervo: o Bruno cadastra o Dom Casmurro dele
    # sem esbarrar no da Ana
    r = do_bruno.post("/livros/", json={"titulo": "Dom Casmurro", "ano": 1899})
    assert r.status_code == 201 and r.json()["id"] != 1
    assert [l["titulo"] for l in do_bruno.get("/livros/").json()] == ["Dom Casmurro"]

    # ...mas o segundo Dom Casmurro DELE, sim, esbarra
    assert do_bruno.post("/livros/", json={"titulo": "Dom Casmurro", "ano": 1899}).status_code == 409

    # e o acervo da Ana continua inteiro, sem ter visto nada disso
    assert len(client.get("/livros/").json()) == 5


def test_busca_e_filtro_na_listagem(client):
    # ?titulo= procura um PEDACO do titulo, sem diferenciar maiusculas
    procurados = ["Dom Casmurro", "Vidas Secas"]     # "Casmurro" e "Secas"
    assert [l["titulo"] for l in client.get("/livros/?titulo=cas").json()] == procurados
    assert [l["titulo"] for l in client.get("/livros/?titulo=CAS").json()] == procurados
    assert [l["titulo"] for l in client.get("/livros/?titulo=casMURRO").json()] == ["Dom Casmurro"]
    assert client.get("/livros/?titulo=zzz").json() == []

    # ?disponivel= filtra: o 2 e' o unico que nasce emprestado
    assert [l["id"] for l in client.get("/livros/?disponivel=false").json()] == [2]
    assert [l["id"] for l in client.get("/livros/?disponivel=true").json()] == [1, 3, 5, 4]

    # e os dois se somam na mesma consulta
    assert [l["id"] for l in client.get("/livros/?titulo=sertao&disponivel=false").json()] == [2]
    assert client.get("/livros/?titulo=cas&disponivel=false").json() == []


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


def test_o_schema_barra_antes_do_service_e_explica_em_portugues(client):
    # 422 vem do schema: titulo curto demais, ano fora do intervalo
    r = client.post("/livros/", json={"titulo": "V", "ano": 1938})
    assert r.status_code == 422
    assert r.json()["detail"][0]["msg"] == (
        "Value error, o titulo precisa ter pelo menos 2 caracteres"
    )

    r = client.post("/livros/", json={"titulo": "Vidas Secas", "ano": 1200})
    assert r.status_code == 422
    assert r.json()["detail"][0]["msg"] == (
        "Value error, o ano precisa estar entre 1450 e 2100"
    )

    # os mesmos validadores valem na edicao
    assert client.patch("/livros/1", json={"titulo": "V"}).status_code == 422


def test_livro_que_nao_existe(client):
    assert client.get("/livros/99").status_code == 404
    assert client.patch("/livros/99", json={"ano": 1900}).status_code == 404
    assert client.delete("/livros/99").status_code == 404
