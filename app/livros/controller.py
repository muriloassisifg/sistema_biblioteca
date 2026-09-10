from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..seguranca import get_current_user
from . import service
from .schemas import LivroAtualizar, LivroCriar, LivroPublico

# A porta trancada: UMA linha, e todas as rotas de livros passam a exigir um
# token valido. Sem ele, o FastAPI responde 401 antes de a rota rodar.
router = APIRouter(
    prefix="/livros",
    tags=["Livros"],
    dependencies=[Depends(get_current_user)],
)

# Nenhum `if` de regra e nenhum `try` aqui: as recusas do Service viram
# HTTP no tradutor registrado no main.py, uma vez para todas as rotas.


@router.get("/", response_model=list[LivroPublico])
def listar(db: Session = Depends(get_db)):
    return service.listar(db)


@router.post("/", response_model=LivroPublico, status_code=201)
def criar(dados: LivroCriar, db: Session = Depends(get_db)):
    return service.criar(db, dados.model_dump())


@router.get("/{livro_id}", response_model=LivroPublico)
def buscar(livro_id: int, db: Session = Depends(get_db)):
    return service.buscar(db, livro_id)


@router.patch("/{livro_id}", response_model=LivroPublico)
def atualizar(
    livro_id: int,
    dados: LivroAtualizar,
    db: Session = Depends(get_db),
):
    return service.atualizar(
        db, livro_id, dados.model_dump(exclude_unset=True)
    )


@router.delete("/{livro_id}", status_code=204)
def apagar(livro_id: int, db: Session = Depends(get_db)):
    service.apagar(db, livro_id)
