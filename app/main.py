from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import inspect

from .database import SessionLocal, engine
from .emprestimos import controller as emprestimos_controller
from .emprestimos.erros import ErroDeEmprestimo
from .emprestimos.erros import LivroNaoEncontrado as LivroNaoEncontradoNoEmprestimo
from .livros import controller as livros_controller
from .livros.acervo import semear_acervo_inicial
from .livros.erros import ErroDeLivro, LivroNaoEncontrado
from .usuarios import controller as usuarios_controller
from .usuarios.erros import CredenciaisInvalidas, ErroDeUsuario

# Nao ha' mais create_all aqui. Quem cria -- e MUDA -- tabelas e' o Alembic:
#     poetry run alembic upgrade head
# Uma vez ao clonar o projeto, e de novo a cada migracao nova.


@asynccontextmanager
async def ciclo_de_vida(app: FastAPI):
    # So' para a aula: os cinco livros iniciais entram quando a aplicacao
    # sobe -- se as tabelas ja' existirem. Sem o upgrade head, nada e' criado
    # por baixo dos panos: a API sobe vazia e o /docs avisa ao primeiro pedido.
    if inspect(engine).has_table("livros"):
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
