"""O relatorio de atrasos, na tela (encontro 10 de P3).

    python ver_relatorio.py             # mostra o relatorio de hoje
    python ver_relatorio.py saida.txt   # mostra e tambem guarda no arquivo

Ferramenta de sala de aula: so' chama o relatorio e imprime. Nao ha rota para
ele, de proposito -- e' um relatorio da biblioteca INTEIRA, e as rotas daqui
sao do acervo de cada bibliotecario.

O relatorio le o banco com sqlite3, direto, pelo CAMINHO do arquivo: este
script o tira da DATABASE_URL do .env. Com PostgreSQL ele nao roda.
"""
import sys
from datetime import date
from pathlib import Path

from app.database import engine
from app.emprestimos.relatorio import relatorio_de_atrasos

banco = engine.url.database
if engine.url.get_backend_name() != "sqlite" or not Path(banco).exists():
    sys.exit(
        "O relatorio le o arquivo de um banco SQLite que ja existe: suba a API "
        "uma vez (uvicorn app.main:app) para ele nascer."
    )

texto = relatorio_de_atrasos(banco, date.today())
print(texto)
if len(sys.argv) > 1:
    Path(sys.argv[1]).write_text(texto + "\n", encoding="utf-8")
