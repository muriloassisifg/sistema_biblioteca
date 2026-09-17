import logging
from contextlib import asynccontextmanager
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .database import SessionLocal
from .emprestimos import controller as emprestimos_controller
from .emprestimos.erros import ErroDeEmprestimo, TipoDeLeitorDesconhecido
from .emprestimos.erros import LivroNaoEncontrado as LivroNaoEncontradoNoEmprestimo
from .livros import controller as livros_controller
from .livros.acervo import semear_acervo_inicial
from .livros.erros import ErroDeLivro, LivroNaoEncontrado
from .usuarios import controller as usuarios_controller
from .usuarios.erros import CredenciaisInvalidas, ErroDeUsuario

# A pasta do projeto: onde moram alembic.ini e alembic/.
RAIZ = Path(__file__).resolve().parent.parent

# Nao ha' create_all aqui. Quem cria -- e MUDA -- tabelas e' o Alembic:
#     poetry run alembic upgrade head
# Uma vez ao clonar o projeto, e de novo a cada migracao nova. Para ninguem
# subir a API com o banco vazio e tomar "no such table", a aplicacao roda
# esse mesmo comando ao subir (a funcao `migrar`, logo abaixo).


def migrar():
    """O `alembic upgrade head`, chamado pelo codigo.

    Num clone novo as tabelas nascem daqui -- e com a tabela alembic_version
    marcando a versao, o que o create_all nao faria. Num banco ja' migrado
    nao faz nada; quando chega uma migracao nova, aplica. E' exatamente o que
    o comando no terminal faz. Sem passar o alembic.ini, de proposito: o
    env.py ja' sabe a URL do banco (pelo .env), e a configuracao de log do
    .ini calaria os logs do uvicorn.
    """
    cfg = Config()
    cfg.set_main_option("script_location", str(RAIZ / "alembic"))
    command.upgrade(cfg, "head")
    logging.getLogger("uvicorn.error").info("Banco na ultima migracao (alembic upgrade head).")


@asynccontextmanager
async def ciclo_de_vida(app: FastAPI):
    migrar()
    # So' para a aula: os cinco livros iniciais entram quando a aplicacao
    # sobe, se a biblioteca estiver vazia.
    db = SessionLocal()
    try:
        semear_acervo_inicial(db)
    finally:
        db.close()
    yield


app = FastAPI(title="Biblioteca do Campus", version="0.5.0", lifespan=ciclo_de_vida)

# Composite: o app inclui roteadores, e cada roteador guarda as suas rotas.
app.include_router(usuarios_controller.router)
app.include_router(livros_controller.router)
app.include_router(emprestimos_controller.router)

# Qual recusa vira qual numero. O que nao estiver aqui e' 409: o pedido foi
# entendido, mas a biblioteca nao aceita.
STATUS = {
    LivroNaoEncontrado: 404,
    LivroNaoEncontradoNoEmprestimo: 404,
    TipoDeLeitorDesconhecido: 422,   # como os 422 do schema: o pedido e' que nao serve
    CredenciaisInvalidas: 401,
}


# O UNICO lugar do sistema que transforma recusa em numero HTTP. Registrado
# para as tres familias de recusa: nenhuma rota precisa de try/except.
@app.exception_handler(ErroDeLivro)
@app.exception_handler(ErroDeEmprestimo)
@app.exception_handler(ErroDeUsuario)
def traduzir_recusa(request: Request, erro: Exception):
    codigo = STATUS.get(type(erro), 409)
    # 401 e' "nao sei quem voce e'"; o cabecalho diz como se apresentar.
    cabecalhos = {"WWW-Authenticate": "Bearer"} if codigo == 401 else None
    return JSONResponse(
        status_code=codigo, content={"detail": str(erro)}, headers=cabecalhos
    )
