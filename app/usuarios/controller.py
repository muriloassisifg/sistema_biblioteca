from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..database import get_db
from ..seguranca import criar_token, get_current_user
from . import service
from .models import Usuario
from .schemas import Token, UsuarioCriar, UsuarioPublico

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.post("/", response_model=UsuarioPublico, status_code=201)
def cadastrar(dados: UsuarioCriar, db: Session = Depends(get_db)):
    return service.cadastrar(db, dados.model_dump())


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # O formulario padrao do OAuth2 chama o campo de "username"; aqui ele
    # carrega o e-mail. E' esse formulario que o botao Authorize do /docs envia.
    usuario = service.autenticar(db, form.username, form.password)
    return Token(access_token=criar_token(usuario.id))


@router.get("/eu", response_model=UsuarioPublico)
def eu(usuario: Usuario = Depends(get_current_user)):
    """Quem sou eu? So' responde com um token valido -- e' o teste da porta."""
    return usuario
