"""Cadastro, login e a porta trancada -- o que o /docs prova em um minuto."""
import sqlite3

from app.database import engine

ANA = {"nome": "Ana", "email": "ana@ifg.edu.br", "senha": "segredo1"}


def test_cadastro_guarda_hash_e_nao_devolve_a_senha(anonimo):
    r = anonimo.post("/usuarios/", json=ANA)
    assert r.status_code == 201
    assert "senha" not in r.json() and "senha_hash" not in r.json()

    # RN04: um e-mail, uma conta.
    assert anonimo.post("/usuarios/", json=ANA).status_code == 409

    # o que esta' no banco e' um hash bcrypt, nao a senha
    con = sqlite3.connect(engine.url.database)
    try:
        (senha_hash,) = con.execute("select senha_hash from usuarios").fetchone()
    finally:
        con.close()
    assert senha_hash.startswith("$2b$") and senha_hash != ANA["senha"]


def test_o_schema_barra_antes_do_service(anonimo):
    assert anonimo.post("/usuarios/", json={**ANA, "email": "abc"}).status_code == 422
    assert anonimo.post("/usuarios/", json={**ANA, "senha": "123"}).status_code == 422


def test_login_certo_e_errado(anonimo):
    anonimo.post("/usuarios/", json=ANA)

    r = anonimo.post("/usuarios/login", data={"username": ANA["email"], "password": "errada"})
    assert r.status_code == 401
    assert r.headers.get("www-authenticate") == "Bearer"
    assert r.json()["detail"] == "E-mail ou senha incorretos"

    r = anonimo.post("/usuarios/login", data={"username": ANA["email"], "password": ANA["senha"]})
    assert r.status_code == 200
    assert r.json()["token_type"] == "bearer" and r.json()["access_token"]


def test_a_porta_esta_trancada(anonimo):
    # sem token, nenhuma rota de livros ou emprestimos roda
    assert anonimo.get("/livros/").status_code == 401
    assert anonimo.post("/livros/", json={"titulo": "Quincas Borba", "ano": 1891}).status_code == 401
    assert anonimo.post("/emprestimos/", json={"livro_id": 1, "leitor_id": 42, "tipo_leitor": "aluno"}).status_code == 401
    assert anonimo.get("/usuarios/eu").status_code == 401


def test_com_o_cracha_a_porta_abre(client):
    assert client.get("/livros/").status_code == 200
    r = client.get("/usuarios/eu")
    assert r.status_code == 200 and r.json()["email"] == ANA["email"]


def test_token_forjado_e_recusado(client):
    import jwt

    forjado = jwt.encode({"sub": "1"}, "outra-chave-tambem-longa-o-bastante-para-o-teste", algorithm="HS256")
    r = client.get("/usuarios/eu", headers={"Authorization": "Bearer " + forjado})
    assert r.status_code == 401


def test_o_app_no_navegador_pode_falar_com_a_api(anonimo):
    # O CORS (Web III, encontro 8): o navegador pergunta antes (OPTIONS) se o app,
    # que roda noutra porta, pode mandar o token no cabecalho. A API responde que sim.
    pergunta = {
        "Origin": "http://localhost:53999",
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "authorization",
    }
    r = anonimo.options("/usuarios/eu", headers=pergunta)
    assert r.status_code == 200
    assert r.headers["access-control-allow-origin"] == "http://localhost:53999"

    # um site qualquer, fora desta maquina, nao recebe a permissao
    r = anonimo.options("/usuarios/eu", headers={**pergunta, "Origin": "http://exemplo.com"})
    assert "access-control-allow-origin" not in r.headers
