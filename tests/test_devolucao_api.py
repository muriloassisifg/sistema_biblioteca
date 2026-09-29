"""A devolucao (encontro 9 de P3): uma fachada, `DevolucaoFacade`, que chama o
Service, a multa, o aviso e o historico numa ordem so' -- e a rota que so' fala
com ela.
"""
from datetime import date, timedelta

import pytest

from app.database import SessionLocal
from app.emprestimos import historico
from app.emprestimos.devolucao import DevolucaoFacade
from app.emprestimos.erros import EmprestimoNaoEncontrado
from app.emprestimos.models import Emprestimo


@pytest.fixture(autouse=True)
def historico_na_pasta_temporaria(tmp_path, monkeypatch):
    """O historico escreve num arquivo; nos testes, numa pasta descartavel."""
    arquivo = tmp_path / "devolucoes.txt"
    monkeypatch.setattr(historico, "ARQUIVO", str(arquivo))
    return arquivo


def emprestar(client, livro_id, leitor_id=42):
    r = client.post(
        "/emprestimos/",
        json={"livro_id": livro_id, "leitor_id": leitor_id, "tipo_leitor": "aluno"},
    )
    assert r.status_code == 201
    return r.json()["id"]


def atrasar(emprestimo_id, dias):
    """Empurra o prazo para tras -- o que o `atrasado.py` do material faz."""
    with SessionLocal() as db:
        emprestimo = db.get(Emprestimo, emprestimo_id)
        emprestimo.devolver_ate = date.today() - timedelta(days=dias) if dias is not None else None
        db.commit()


def devolver(client, emprestimo_id):
    return client.post(f"/emprestimos/{emprestimo_id}/devolucao")


def test_devolver_no_prazo_nao_tem_multa_e_libera_o_livro(client):
    emprestimo_id = emprestar(client, 1)

    r = devolver(client, emprestimo_id)
    assert r.status_code == 200
    assert r.json() == {
        "emprestimo_id": emprestimo_id, "livro_id": 1, "dias_de_atraso": 0,
        "multa": 0.0, "aviso": "Livro 1 devolvido.",
    }

    # o livro voltou: outro leitor consegue emprestar
    assert client.post(
        "/emprestimos/", json={"livro_id": 1, "leitor_id": 7, "tipo_leitor": "aluno"}
    ).status_code == 201


def test_devolver_com_atraso_cobra_2_50_por_dia(client):
    emprestimo_id = emprestar(client, 1)
    atrasar(emprestimo_id, 6)

    r = devolver(client, emprestimo_id)
    assert r.status_code == 200
    assert r.json()["dias_de_atraso"] == 6
    assert r.json()["multa"] == 15.0
    assert r.json()["aviso"] == "Livro 1 devolvido. Multa: R$ 15.00."


def test_a_multa_tem_teto_de_50_reais(client):
    emprestimo_id = emprestar(client, 1)
    atrasar(emprestimo_id, 30)

    r = devolver(client, emprestimo_id)
    assert r.json()["dias_de_atraso"] == 30
    assert r.json()["multa"] == 50.0


def test_emprestimo_de_antes_da_migracao_nao_tem_data_e_nao_tem_multa(client):
    emprestimo_id = emprestar(client, 1)
    atrasar(emprestimo_id, None)

    r = devolver(client, emprestimo_id)
    assert r.status_code == 200
    assert r.json()["dias_de_atraso"] == 0 and r.json()["multa"] == 0.0


def test_devolver_duas_vezes_e_409(client):
    emprestimo_id = emprestar(client, 1)
    assert devolver(client, emprestimo_id).status_code == 200

    r = devolver(client, emprestimo_id)
    assert r.status_code == 409
    assert r.json()["detail"] == f"Emprestimo {emprestimo_id} ja foi devolvido"


def test_emprestimo_que_nao_existe_e_404(client):
    r = devolver(client, 999)
    assert r.status_code == 404
    assert r.json()["detail"] == "Emprestimo 999 nao existe"


def test_o_emprestimo_de_outro_bibliotecario_nao_existe_daqui(client, do_bruno):
    emprestimo_id = emprestar(client, 1)          # o livro 1 e' da Ana

    r = devolver(do_bruno, emprestimo_id)
    assert r.status_code == 404
    assert r.json()["detail"] == f"Emprestimo {emprestimo_id} nao existe"

    # e nada aconteceu: o emprestimo da Ana continua aberto
    assert devolver(client, emprestimo_id).status_code == 200


def test_a_devolucao_precisa_de_token(anonimo):
    assert anonimo.post("/emprestimos/1/devolucao").status_code == 401


def test_cada_devolucao_deixa_uma_linha_no_historico(client, historico_na_pasta_temporaria):
    primeiro = emprestar(client, 1)
    atrasar(primeiro, 6)
    segundo = emprestar(client, 3)
    devolver(client, primeiro)
    devolver(client, segundo)

    linhas = historico_na_pasta_temporaria.read_text(encoding="utf-8").strip().split("\n")
    assert [l.split(";")[1:] for l in linhas] == [[str(primeiro), "6", "15.00"], [str(segundo), "0", "0.00"]]


# ---- a fachada sozinha, sem banco e sem HTTP -----------------------------------
class Chamadas:
    """Peca falsa: so' anota o que foi chamado, e em que ordem."""

    def __init__(self):
        self.ordem = []


def fachada_com_pecas_falsas(registro):
    chamadas = Chamadas()

    class Emprestimos:
        def devolver(self, emprestimo_id):
            chamadas.ordem.append("devolver")
            registro(chamadas)
            return type("E", (), {"id": emprestimo_id, "livro_id": 1, "leitor_id": 7,
                                  "devolver_ate": date.today() - timedelta(days=2)})()

    class Multas:
        def dias_de_atraso(self, prazo, hoje):
            chamadas.ordem.append("dias")
            return (hoje - prazo).days

        def calcular(self, dias):
            chamadas.ordem.append("multa")
            return dias * 2.5

    class Notificador:
        def devolucao_registrada(self, leitor_id, livro_id, multa):
            chamadas.ordem.append("aviso")
            return f"aviso {multa}"

    class Historico:
        def registrar(self, emprestimo_id, dias, multa):
            chamadas.ordem.append("historico")

    return DevolucaoFacade(Emprestimos(), Multas(), Notificador(), Historico()), chamadas


def test_a_fachada_chama_as_pecas_na_ordem():
    fachada, chamadas = fachada_com_pecas_falsas(lambda c: None)
    comprovante = fachada.devolver(5)

    assert chamadas.ordem == ["devolver", "dias", "multa", "aviso", "historico"]
    assert comprovante == {"emprestimo_id": 5, "livro_id": 1, "dias_de_atraso": 2, "multa": 5.0,
                           "aviso": "aviso 5.0"}


def test_se_o_registro_falha_ninguem_e_avisado():
    def falha(chamadas):
        raise EmprestimoNaoEncontrado("x")

    fachada, chamadas = fachada_com_pecas_falsas(falha)
    with pytest.raises(EmprestimoNaoEncontrado):
        fachada.devolver(5)
    assert chamadas.ordem == ["devolver"]
