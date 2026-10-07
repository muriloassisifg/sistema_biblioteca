"""O relatorio de atrasos: os emprestimos que ja passaram do prazo.

Cada funcao tem um motivo so' para mudar: buscar no banco, decidir a situacao
ou o contato, ou escrever a linha. A multa nao e' calculada aqui: mora no
MultaService, que le o multa.json.
"""
import sqlite3
from datetime import date

from .dependencias import obter_multas

LIMITE_GRAVE = 30      # acima de quantos dias de atraso a situacao e' GRAVE
LIMITE_ATENCAO = 7     # e acima de quantos ela deixa de ser so' RECENTE

CONTATOS = {
    "aluno": "secretaria",
    "professor": "coordenacao",
    "servidor": "RH",
}
CONTATO_PADRAO = "atendimento"


def buscar_emprestimos_ativos(banco):
    conexao = sqlite3.connect(banco)
    conexao.row_factory = sqlite3.Row
    emprestimos = conexao.execute(
        "SELECT e.id, e.leitor_id, e.tipo_leitor, e.devolver_ate, l.titulo "
        "FROM emprestimos e JOIN livros l ON l.id = e.livro_id "
        "WHERE e.status = 'ativo' AND e.devolver_ate IS NOT NULL "  # sem prazo, sem atraso
        "ORDER BY e.devolver_ate, e.id"
    ).fetchall()
    conexao.close()
    return emprestimos


def situacao_do_atraso(dias):
    if dias > LIMITE_GRAVE:
        return "GRAVE"
    if dias > LIMITE_ATENCAO:
        return "ATENCAO"
    return "RECENTE"


def contato_para(tipo_leitor):
    return CONTATOS.get(tipo_leitor, CONTATO_PADRAO)


def linha_do_atraso(emprestimo, dias, multa):
    return (
        f"emprestimo {emprestimo['id']} | leitor {emprestimo['leitor_id']} | "
        f"{emprestimo['titulo']} | {dias} dias | R$ {multa:.2f} | "
        f"{situacao_do_atraso(dias)} | "
        f"contato: {contato_para(emprestimo['tipo_leitor'])}"
    )


def relatorio_de_atrasos(banco, hoje):
    multas = obter_multas()
    linhas = []
    total = 0
    for emprestimo in buscar_emprestimos_ativos(banco):
        prazo = date.fromisoformat(emprestimo["devolver_ate"])
        dias = multas.dias_de_atraso(prazo, hoje)
        if dias == 0:
            continue
        multa = multas.calcular(dias)
        linhas.append(linha_do_atraso(emprestimo, dias, multa))
        total += multa

    texto = f"RELATORIO DE ATRASOS - {hoje.strftime('%d/%m/%Y')}\n"
    for linha in linhas:
        texto += linha + "\n"
    texto += f"{len(linhas)} emprestimos em atraso, R$ {total:.2f} em multas"
    return texto
