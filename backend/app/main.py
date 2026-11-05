import os

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .livros import controller as livros_controller
from .livros.erros import ErroDeLivro, LivroNaoEncontrado
from .usuarios import controller as usuarios_controller
from .usuarios.erros import CredenciaisInvalidas, ErroDeUsuario

# Nao ha' mais create_all aqui. Quem cria -- e MUDA -- tabelas agora e' o
# Alembic:  poetry run alembic upgrade head
# Uma vez ao clonar o projeto, e de novo a cada migracao nova.

app = FastAPI(title="API do Meu Projeto", version="0.4.0")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("ENDERECO_DO_APP", "")],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(usuarios_controller.router)
app.include_router(livros_controller.router)


@app.exception_handler(ErroDeLivro)
def traduzir_recusa(request: Request, erro: ErroDeLivro):
    """O unico lugar do sistema que transforma recusa em numero HTTP."""
    codigo = 404 if isinstance(erro, LivroNaoEncontrado) else 409
    return JSONResponse(status_code=codigo, content={"detail": str(erro)})


@app.exception_handler(ErroDeUsuario)
def traduzir_recusa_de_usuario(request: Request, erro: ErroDeUsuario):
    if isinstance(erro, CredenciaisInvalidas):
        # 401 e' "nao sei quem voce e'". O cabecalho diz como se apresentar.
        return JSONResponse(
            status_code=401,
            content={"detail": str(erro)},
            headers={"WWW-Authenticate": "Bearer"},
        )
    return JSONResponse(status_code=409, content={"detail": str(erro)})
