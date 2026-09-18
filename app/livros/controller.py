from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..seguranca import get_current_user
from ..usuarios.models import Usuario
from . import service
from .schemas import LivroAtualizar, LivroCriar, LivroPublico

# A porta continua no router: nenhuma rota roda sem token. A novidade e' que
# cada rota agora tambem RECEBE o usuario -- porque precisa saber quem e'.
router = APIRouter(
    prefix="/livros",
    tags=["Livros"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/", response_model=list[LivroPublico])
def listar(
    titulo: str | None = None,          # ?titulo=casmurro  -- parametro de consulta
    disponivel: bool | None = None,     # ?disponivel=true
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.listar(db, usuario, titulo, disponivel)


@router.post("/", response_model=LivroPublico, status_code=201)
def criar(
    dados: LivroCriar,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.criar(db, usuario, dados.model_dump())


@router.get("/{livro_id}", response_model=LivroPublico)
def buscar(
    livro_id: int,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.buscar(db, usuario, livro_id)


@router.patch("/{livro_id}", response_model=LivroPublico)
def atualizar(
    livro_id: int,
    dados: LivroAtualizar,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.atualizar(db, usuario, livro_id, dados.model_dump(exclude_unset=True))


@router.delete("/{livro_id}", status_code=204)
def apagar(
    livro_id: int,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service.apagar(db, usuario, livro_id)
