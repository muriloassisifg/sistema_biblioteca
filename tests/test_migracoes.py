"""As migracoes criam o mesmo esquema que os models declaram.

Roda o `alembic upgrade head` de verdade (num Python novo, como quem clona o
projeto) sobre um banco vazio, e depois o `alembic check`: se um model mudar
sem uma migracao nova, e' aqui que aparece.

E dois bancos de antes -- um com um emprestimo dentro, outro com livro e
emprestimo -- passam pela migracao seguinte sem perder nada, na subida e na
descida.
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


def _consultar(banco, sql):
    con = sqlite3.connect(banco)
    try:
        return con.execute(sql).fetchall()
    finally:
        con.close()


def _emprestimos(banco):
    return _consultar(banco, "select * from emprestimos")


def _livros(banco):
    return _consultar(banco, "select * from livros")


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


def test_a_terceira_migracao_num_banco_que_ja_tinha_livros():
    banco = os.path.join(tempfile.mkdtemp(prefix="biblioteca-mig-"), "sem_dono.db")

    # o banco como estava antes do dono, com um livro emprestado dentro
    codigo, saida = _alembic("upgrade", "df904534ea10", banco=banco)
    assert codigo == 0, saida
    con = sqlite3.connect(banco)
    try:
        con.execute("insert into usuarios (id, nome, email, senha_hash)"
                    " values (1, 'Ana', 'ana@ifg.edu.br', '$2b$hash')")
        con.execute("insert into livros (id, titulo, ano, disponivel)"
                    " values (1, 'Dom Casmurro', 1899, 0)")
        con.execute("insert into emprestimos (id, livro_id, leitor_id, status, tipo_leitor, devolver_ate)"
                    " values (1, 1, 42, 'ativo', 'aluno', '2026-10-01')")
        con.commit()
    finally:
        con.close()

    # Na subida o livro de antes fica com dono NULO -- ele foi cadastrado
    # quando o acervo era de todos, e nao ha' a quem dar. Consequencia: a
    # partir daqui ninguem o ve', porque a listagem filtra pelo dono. Quem
    # tem um banco assim da' um dono a ele na mao, ou apaga.
    codigo, saida = _alembic("upgrade", "head", banco=banco)
    assert codigo == 0, saida
    assert _livros(banco) == [(1, "Dom Casmurro", 1899, 0, None)]

    # o emprestimo antigo atravessa a recriacao da tabela livros sem se mexer
    assert _emprestimos(banco) == [(1, 1, 42, "ativo", "aluno", "2026-10-01")]

    # na descida, a coluna sai e os dados ficam
    codigo, saida = _alembic("downgrade", "df904534ea10", banco=banco)
    assert codigo == 0, saida
    assert _livros(banco) == [(1, "Dom Casmurro", 1899, 0)]
    assert _emprestimos(banco) == [(1, 1, 42, "ativo", "aluno", "2026-10-01")]
