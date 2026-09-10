"""As migracoes criam o mesmo esquema que os models declaram.

Roda o `alembic upgrade head` de verdade (num Python novo, como quem clona o
projeto) sobre um banco vazio, e depois o `alembic check`: se um model mudar
sem uma migracao nova, e' aqui que aparece.
"""
import os
import sqlite3
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _alembic(*args, banco):
    env = dict(os.environ, DATABASE_URL="sqlite:///" + banco.replace("\\", "/"),
               SECRET_KEY="chave-so-dos-testes-com-mais-de-trinta-e-dois-caracteres")
    r = subprocess.run([sys.executable, "-m", "alembic", *args], cwd=RAIZ,
                       capture_output=True, text=True, env=env)
    return r.returncode, (r.stdout + r.stderr)[-600:]


def test_upgrade_head_cria_as_tabelas_num_banco_vazio():
    banco = os.path.join(tempfile.mkdtemp(prefix="biblioteca-mig-"), "mig.db")

    codigo, saida = _alembic("upgrade", "head", banco=banco)
    assert codigo == 0, saida

    con = sqlite3.connect(banco)
    try:
        tabelas = sorted(r[0] for r in con.execute(
            "select name from sqlite_master where type='table'"))
    finally:
        con.close()
    assert tabelas == ["alembic_version", "emprestimos", "livros", "usuarios"]

    # models e migracoes dizem a mesma coisa
    codigo, saida = _alembic("check", banco=banco)
    assert codigo == 0, saida

    # rodar de novo nao faz nada -- e nao quebra
    codigo, saida = _alembic("upgrade", "head", banco=banco)
    assert codigo == 0, saida
