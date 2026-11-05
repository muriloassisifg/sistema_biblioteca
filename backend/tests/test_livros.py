"""Cada teste faz pedidos de verdade à API, sem uvicorn e sem o seu banco."""

LIVRO = {"titulo": "Dom Casmurro", "ano": 1899}


# Cria a conta, faz o login e devolve o cabeçalho com o token.
def entrar(cliente, email):
    cliente.post("/usuarios/", json={"nome": "Teste", "email": email, "senha": "segredo123"})
    dados = {"username": email, "password": "segredo123"}
    resposta = cliente.post("/usuarios/login", data=dados)
    return {"Authorization": "Bearer " + resposta.json()["access_token"]}


def test_criar_um_livro_devolve_201_com_o_titulo(cliente):
    ana = entrar(cliente, "ana@ifg.edu.br")

    resposta = cliente.post("/livros/", json=LIVRO, headers=ana)

    assert resposta.status_code == 201
    assert resposta.json()["titulo"] == "Dom Casmurro"


def test_sem_token_a_api_recusa(cliente):
    resposta = cliente.get("/livros/")

    assert resposta.status_code == 401


def test_o_bruno_nao_ve_o_livro_da_ana(cliente):
    ana = entrar(cliente, "ana@ifg.edu.br")
    bruno = entrar(cliente, "bruno@ifg.edu.br")
    cliente.post("/livros/", json=LIVRO, headers=ana)

    lista_da_ana = cliente.get("/livros/", headers=ana).json()
    lista_do_bruno = cliente.get("/livros/", headers=bruno).json()

    assert len(lista_da_ana) == 1
    assert lista_do_bruno == []


def test_editar_muda_o_titulo(cliente):
    ana = entrar(cliente, "ana@ifg.edu.br")
    livro = cliente.post("/livros/", json=LIVRO, headers=ana).json()

    mudanca = {"titulo": "Vidas Secas"}
    resposta = cliente.patch(f"/livros/{livro['id']}", json=mudanca, headers=ana)

    assert resposta.status_code == 200
    assert resposta.json()["titulo"] == "Vidas Secas"


def test_excluir_tira_o_livro_da_lista(cliente):
    ana = entrar(cliente, "ana@ifg.edu.br")
    livro = cliente.post("/livros/", json=LIVRO, headers=ana).json()

    resposta = cliente.delete(f"/livros/{livro['id']}", headers=ana)

    assert resposta.status_code == 204
    assert cliente.get("/livros/", headers=ana).json() == []


def test_livro_que_nao_existe_devolve_404(cliente):
    ana = entrar(cliente, "ana@ifg.edu.br")

    resposta = cliente.get("/livros/999", headers=ana)

    assert resposta.status_code == 404


def test_o_mesmo_titulo_duas_vezes_devolve_409(cliente):
    ana = entrar(cliente, "ana@ifg.edu.br")
    cliente.post("/livros/", json=LIVRO, headers=ana)

    resposta = cliente.post("/livros/", json=LIVRO, headers=ana)

    assert resposta.status_code == 409


def test_a_busca_devolve_so_o_que_combina(cliente):
    ana = entrar(cliente, "ana@ifg.edu.br")
    cliente.post("/livros/", json=LIVRO, headers=ana)
    cliente.post("/livros/", json={"titulo": "Vidas Secas", "ano": 1938}, headers=ana)

    resposta = cliente.get("/livros/", params={"titulo": "casmurro"}, headers=ana)

    assert len(resposta.json()) == 1
    assert resposta.json()[0]["titulo"] == "Dom Casmurro"


def test_senha_errada_devolve_401(cliente):
    entrar(cliente, "ana@ifg.edu.br")
    dados = {"username": "ana@ifg.edu.br", "password": "senha-errada"}

    resposta = cliente.post("/usuarios/login", data=dados)

    assert resposta.status_code == 401
