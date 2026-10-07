"""O relatorio de atrasos: os emprestimos que ja passaram do prazo.

Escrito com pressa, na vespera da reuniao da coordenacao. Funciona -- os
testes em tests/ confirmam -- mas ninguem quer mexer nele.
"""
import sqlite3
from datetime import date


def relatorio_de_atrasos(b, h):
    # --- busca no banco ---
    c = sqlite3.connect(b)
    c.row_factory = sqlite3.Row
    rs = c.execute(
        "SELECT e.id, e.leitor_id, e.tipo_leitor, e.devolver_ate, l.titulo "
        "FROM emprestimos e JOIN livros l ON l.id = e.livro_id "
        "WHERE e.status = 'ativo' AND e.devolver_ate IS NOT NULL "  # sem prazo, sem atraso
        "ORDER BY e.devolver_ate, e.id"
    ).fetchall()
    c.close()

    # --- dias, multa, situacao e contato ---
    x = []
    t = 0
    for r in rs:
        d = (h - date.fromisoformat(r["devolver_ate"])).days
        if d <= 0:
            continue
        m = d * 2.5
        if m > 50:
            m = 50
        if d > 30:
            s = "GRAVE"
        elif d > 7:
            s = "ATENCAO"
        else:
            s = "RECENTE"
        if r["tipo_leitor"] == "aluno":
            q = "secretaria"
        elif r["tipo_leitor"] == "professor":
            q = "coordenacao"
        elif r["tipo_leitor"] == "servidor":
            q = "RH"
        else:
            q = "atendimento"
        x.append(
            f"emprestimo {r['id']} | leitor {r['leitor_id']} | {r['titulo']} | "
            f"{d} dias | R$ {m:.2f} | {s} | contato: {q}"
        )
        t += m

    # --- monta o texto ---
    o = f"RELATORIO DE ATRASOS - {h.strftime('%d/%m/%Y')}\n"
    for l in x:
        o += l + "\n"
    o += f"{len(x)} emprestimos em atraso, R$ {t:.2f} em multas"
    return o
