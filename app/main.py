from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .database import Base, SessionLocal, engine
from .emprestimos import controller as emprestimos_controller
from .emprestimos.erros import ErroDeEmprestimo
from .emprestimos.erros import LivroNaoEncontrado as LivroNaoEncontradoNoEmprestimo
from .livros import controller as livros_controller
from .livros.acervo import semear_acervo_inicial
from .livros.erros import ErroDeLivro, LivroNaoEncontrado

# So' para a aula: cria as tabelas ao subir, e poe os cinco livros iniciais
# se a biblioteca estiver vazia. Em projeto de verdade quem cria e evolui
# tabelas e' uma ferramenta de migracao (Alembic), assunto de outro dia.
Base.metadata.create_all(bind=engine)

db = SessionLocal()
try:
    semear_acervo_inicial(db)
finally:
    db.close()

app = FastAPI(title="Biblioteca do Campus", version="0.4.0")

# Composite: o app inclui roteadores, e cada roteador guarda as suas rotas.
# Para o app, incluir um roteador com trinta rotas ou com uma e' o mesmo
# gesto -- e' por isso que este arquivo nao cresce quando o sistema cresce.
app.include_router(livros_controller.router)
app.include_router(emprestimos_controller.router)

# Qual recusa vira qual numero. O que nao estiver aqui e' 409: o pedido foi
# entendido, mas a biblioteca nao aceita.
STATUS = {
    LivroNaoEncontrado: 404,
    LivroNaoEncontradoNoEmprestimo: 404,
}


# O UNICO lugar do sistema que transforma recusa em numero HTTP. Registrado
# para as duas familias de recusa: nenhuma rota precisa de try/except.
@app.exception_handler(ErroDeLivro)
@app.exception_handler(ErroDeEmprestimo)
def traduzir_recusa(request: Request, erro: Exception):
    return JSONResponse(
        status_code=STATUS.get(type(erro), 409),
        content={"detail": str(erro)},
    )
