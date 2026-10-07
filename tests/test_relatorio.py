"""Testes de caracterizacao do relatorio de atrasos (encontro 10 de P3).

Eles NAO dizem como o relatorio DEVERIA ser: dizem como ele e' HOJE. Sao a rede
de seguranca para arrumar o codigo por dentro sem mudar o que ele faz.
Quem refatora o relatorio nao altera nenhuma linha deste arquivo.

Os seis primeiros sao os do material da aula; o setimo e' do repositorio (o
emprestimo de antes do Strategy, sem data de devolucao). A diferenca para o
material esta' so' em como o banco nasce: la' ele e' criado a mao, com sqlite3;
aqui e' o dos demais testes (o fixture `client`: um SQLite descartavel, com os
cinco livros do acervo inicial) e os emprestimos entram pelo modelo
`Emprestimo`. O relatorio recebe o CAMINHO do arquivo e le o banco por conta
propria. A data de "hoje" e' fixa, para o teste nao depender do dia em que roda.

Os numeros esperados sao os do multa.json: R$ 2,50 por dia, no maximo R$ 50,00.
"""
from datetime import date, timedelta

import pytest

from app.database import SessionLocal, engine
from app.emprestimos.models import Emprestimo
from app.emprestimos.relatorio import relatorio_de_atrasos

HOJE = date(2026, 10, 7)

# Todo teste parte do banco do fixture `client`: vazio de emprestimos, com os
# cinco livros da Ana (1 Dom Casmurro, 2 Grande Sertao, 3 Memorias Postumas,
# 4 Vidas Secas, 5 O Cortico).
pytestmark = pytest.mark.usefixtures("client")


def banco_com(*emprestimos):
    """Poe no banco so' os emprestimos dados -- (livro, leitor, tipo, dias de
    atraso, status) -- e devolve o caminho do arquivo, que e' o que o relatorio
    recebe. `None` nos dias e' o emprestimo sem data de devolucao."""
    with SessionLocal() as db:
        for livro_id, leitor_id, tipo, dias, status in emprestimos:
            prazo = HOJE - timedelta(days=dias) if dias is not None else None
            db.add(
                Emprestimo(
                    livro_id=livro_id,
                    leitor_id=leitor_id,
                    tipo_leitor=tipo,
                    devolver_ate=prazo,
                    status=status,
                )
            )
        db.commit()
    return engine.url.database


def test_a_saida_exata_do_relatorio():
    banco = banco_com(
        (1, 7, "aluno", 3, "ativo"),
        (3, 8, "professor", 10, "ativo"),
        (4, 9, "servidor", 40, "ativo"),
        (5, 10, "visitante", 6, "ativo"),
    )
    esperado = (
        "RELATORIO DE ATRASOS - 07/10/2026\n"
        "emprestimo 3 | leitor 9 | Vidas Secas | 40 dias | R$ 50.00 | GRAVE | contato: RH\n"
        "emprestimo 2 | leitor 8 | Memorias Postumas | 10 dias | R$ 25.00 | ATENCAO | contato: coordenacao\n"
        "emprestimo 4 | leitor 10 | O Cortico | 6 dias | R$ 15.00 | RECENTE | contato: atendimento\n"
        "emprestimo 1 | leitor 7 | Dom Casmurro | 3 dias | R$ 7.50 | RECENTE | contato: secretaria\n"
        "4 emprestimos em atraso, R$ 97.50 em multas"
    )
    assert relatorio_de_atrasos(banco, HOJE) == esperado


def test_so_entra_o_emprestimo_aberto_e_vencido():
    banco = banco_com(
        (1, 7, "aluno", 0, "ativo"),       # vence hoje: ainda nao esta atrasado
        (3, 7, "aluno", -5, "ativo"),      # vence daqui a 5 dias
        (4, 7, "aluno", 20, "devolvido"),  # atrasou, mas o livro ja voltou
        (5, 7, "aluno", 4, "ativo"),       # este sim
    )
    esperado = (
        "RELATORIO DE ATRASOS - 07/10/2026\n"
        "emprestimo 4 | leitor 7 | O Cortico | 4 dias | R$ 10.00 | RECENTE | contato: secretaria\n"
        "1 emprestimos em atraso, R$ 10.00 em multas"
    )
    assert relatorio_de_atrasos(banco, HOJE) == esperado


def test_a_multa_e_2_50_por_dia_com_teto_de_50():
    banco = banco_com(
        (1, 7, "aluno", 1, "ativo"),
        (1, 7, "aluno", 10, "ativo"),
        (1, 7, "aluno", 20, "ativo"),
        (1, 7, "aluno", 21, "ativo"),
        (1, 7, "aluno", 40, "ativo"),
    )
    relatorio = relatorio_de_atrasos(banco, HOJE)
    assert "| 1 dias | R$ 2.50 |" in relatorio
    assert "| 10 dias | R$ 25.00 |" in relatorio
    assert "| 20 dias | R$ 50.00 |" in relatorio
    assert "| 21 dias | R$ 50.00 |" in relatorio   # 52.50 passaria do teto
    assert "| 40 dias | R$ 50.00 |" in relatorio


def test_a_situacao_pelos_dias_de_atraso():
    banco = banco_com(
        (1, 7, "aluno", 7, "ativo"),
        (1, 7, "aluno", 8, "ativo"),
        (1, 7, "aluno", 30, "ativo"),
        (1, 7, "aluno", 31, "ativo"),
    )
    relatorio = relatorio_de_atrasos(banco, HOJE)
    assert "| 7 dias | R$ 17.50 | RECENTE |" in relatorio
    assert "| 8 dias | R$ 20.00 | ATENCAO |" in relatorio
    assert "| 30 dias | R$ 50.00 | ATENCAO |" in relatorio
    assert "| 31 dias | R$ 50.00 | GRAVE |" in relatorio


def test_o_contato_por_tipo_de_leitor():
    banco = banco_com(
        (1, 7, "aluno", 2, "ativo"),
        (1, 7, "professor", 3, "ativo"),
        (1, 7, "servidor", 4, "ativo"),
        (1, 7, "visitante", 5, "ativo"),
        (1, 7, "estagiario", 6, "ativo"),
    )
    relatorio = relatorio_de_atrasos(banco, HOJE)
    assert "| 2 dias | R$ 5.00 | RECENTE | contato: secretaria" in relatorio
    assert "| 3 dias | R$ 7.50 | RECENTE | contato: coordenacao" in relatorio
    assert "| 4 dias | R$ 10.00 | RECENTE | contato: RH" in relatorio
    assert "| 5 dias | R$ 12.50 | RECENTE | contato: atendimento" in relatorio
    assert "| 6 dias | R$ 15.00 | RECENTE | contato: atendimento" in relatorio


def test_sem_atrasos():
    banco = banco_com()
    esperado = (
        "RELATORIO DE ATRASOS - 07/10/2026\n"
        "0 emprestimos em atraso, R$ 0.00 em multas"
    )
    assert relatorio_de_atrasos(banco, HOJE) == esperado


def test_o_emprestimo_de_antes_do_strategy_nao_tem_prazo_e_nao_entra():
    # So' o repositorio tem este caso: a coluna `devolver_ate` e' nula nos
    # emprestimos anteriores a segunda migracao (o MultaService tambem os trata
    # como sem atraso). Sem prazo nao ha o que estourar -- e o relatorio nao cai.
    banco = banco_com(
        (1, 7, "aluno", None, "ativo"),
        (3, 7, "aluno", 4, "ativo"),
    )
    esperado = (
        "RELATORIO DE ATRASOS - 07/10/2026\n"
        "emprestimo 2 | leitor 7 | Memorias Postumas | 4 dias | R$ 10.00 | RECENTE | contato: secretaria\n"
        "1 emprestimos em atraso, R$ 10.00 em multas"
    )
    assert relatorio_de_atrasos(banco, HOJE) == esperado
