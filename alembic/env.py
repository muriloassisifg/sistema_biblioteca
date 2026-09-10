import os
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

from alembic import context

# AS TABELAS DO PROJETO. Importar os models e' o que os registra na Base:
# sem estas linhas o autogenerate acha que o projeto nao tem tabela nenhuma
# -- e gera uma migracao que apaga tudo.
from app.database import Base
import app.livros.models        # noqa: F401
import app.emprestimos.models   # noqa: F401
import app.usuarios.models      # noqa: F401

config = context.config

# A URL vem do .env, o mesmo que a aplicacao usa. (O `%` dobrado e' porque o
# arquivo .ini trata `%` como caractere especial.)
load_dotenv()
config.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"].replace("%", "%%"))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# E' com isto que o autogenerate compara o banco: o que os models declaram.
target_metadata = Base.metadata

# O SQLite quase nao sabe alterar tabela (o ALTER TABLE dele e' minimo). Em
# modo batch o Alembic recria a tabela por baixo dos panos -- e a mesma
# migracao que funciona no SQLite funciona igual no PostgreSQL.
BATCH = True


def run_migrations_offline() -> None:
    """Gera o SQL sem conectar no banco (`alembic upgrade head --sql`)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=BATCH,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Conecta no banco e aplica as migracoes -- o caso de sempre."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=BATCH,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
