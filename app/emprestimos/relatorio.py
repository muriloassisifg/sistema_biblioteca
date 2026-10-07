"""O relatorio de atrasos: os emprestimos que ja passaram do prazo.

Escrito com pressa, na vespera da reuniao da coordenacao. Funciona -- os
testes em tests/ confirmam -- mas ninguem quer mexer nele.
"""
import sqlite3
from datetime import date


def relatorio_de_atrasos(banco, hoje):
    # --- busca no banco ---
    conexao = sqlite3.connect(banco)
    conexao.row_factory = sqlite3.Row
    emprestimos = conexao.execute(
        "SELECT e.id, e.leitor_id, e.tipo_leitor, e.devolver_ate, l.titulo "
        "FROM emprestimos e JOIN livros l ON l.id = e.livro_id "
        "WHERE e.status = 'ativo' AND e.devolver_ate IS NOT NULL "  # sem prazo, sem atraso
        "ORDER BY e.devolver_ate, e.id"
    ).fetchall()
    conexao.close()

    # --- dias, multa, situacao e contato ---
    linhas = []
    total = 0
    for emprestimo in emprestimos:
        dias = (hoje - date.fromisoformat(emprestimo["devolver_ate"])).days
        if dias <= 0:
            continue
        multa = dias * 2.5
        if multa > 50:
            multa = 50
        if dias > 30:
            situacao = "GRAVE"
        elif dias > 7:
            situacao = "ATENCAO"
        else:
            situacao = "RECENTE"
        if emprestimo["tipo_leitor"] == "aluno":
            contato = "secretaria"
        elif emprestimo["tipo_leitor"] == "professor":
            contato = "coordenacao"
        elif emprestimo["tipo_leitor"] == "servidor":
            contato = "RH"
        else:
            contato = "atendimento"
        linhas.append(
            f"emprestimo {emprestimo['id']} | leitor {emprestimo['leitor_id']} | "
            f"{emprestimo['titulo']} | {dias} dias | R$ {multa:.2f} | "
            f"{situacao} | contato: {contato}"
        )
        total += multa

    # --- monta o texto ---
    texto = f"RELATORIO DE ATRASOS - {hoje.strftime('%d/%m/%Y')}\n"
    for linha in linhas:
        texto += linha + "\n"
    texto += f"{len(linhas)} emprestimos em atraso, R$ {total:.2f} em multas"
    return texto
