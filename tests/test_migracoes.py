"""As migracoes criam o mesmo esquema que os models declaram.

Roda o `alembic upgrade head` de verdade (num Python novo, como quem clona o
projeto) sobre um banco vazio, e depois o `alembic check`: se um model mudar
sem uma migracao nova, e' aqui que aparece.

E um banco de antes do encontro 7, com um emprestimo dentro, passa pela
segunda migracao sem perder o emprestimo -- na subida e na descida.
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


def _emprestimos(banco):
    con = sqlite3.connect(banco)
    try:
        return con.execute("select * from emprestimos").fetchall()
    finally:
        con.close()


def test_a_segunda_migracao_num_banco_que_ja_tinha_emprestimos():
    banco = os.path.join(tempfile.mkdtemp(prefix="biblioteca-mig-"), "antigo.db")

    # o banco como estava antes do encontro 7, com um emprestimo dentro
    codigo, saida = _alembic("upgrade", "1ee353fc967a", banco=banco)
    assert codigo == 0, saida
    con = sqlite3.connect(banco)
    try:
        con.execute("insert into livros (id, titulo, ano, disponivel) values (1, 'Dom Casmurro', 1899, 0)")
        con.execute("insert into emprestimos (id, livro_id, leitor_id, status) values (1, 1, 42, 'ativo')")
        con.commit()
    finally:
        con.close()

    # na subida, o emprestimo antigo vira de aluno (a regra de antes) e fica sem data
    codigo, saida = _alembic("upgrade", "df904534ea10", banco=banco)
    assert codigo == 0, saida
    assert _emprestimos(banco) == [(1, 1, 42, "ativo", "aluno", None)]

    # na descida, as duas colunas saem e o emprestimo fica
    codigo, saida = _alembic("downgrade", "1ee353fc967a", banco=banco)
    assert codigo == 0, saida
    assert _emprestimos(banco) == [(1, 1, 42, "ativo")]
