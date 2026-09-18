from fastapi import Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..seguranca import get_current_user
from ..usuarios.models import Usuario
from .repositorio import RepositorioSQLAlchemy
from .service import EmprestimoService


def obter_service(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Monta o Service ja' com o repositorio de producao dentro.

    Este e' o unico arquivo do sistema que escolhe QUAL repositorio o Service
    vai usar. Trocar de banco e' trocar a classe que aparece nesta linha.

    A sessao chega pelo mesmo mecanismo que entrega o Service a rota: uma
    dependencia que depende de outra. O FastAPI resolve o `get_db` primeiro,
    entrega o `db` aqui, e so' entao chama a rota com o Service pronto.

    Desde que o livro tem dono (encontro 7 de Web III), o repositorio recebe
    tambem QUEM esta' logado: so' se empresta livro do proprio acervo. Repare
    onde essa mudanca coube -- nesta montagem, e nao no `service.py`, que
    continua pedindo `buscar_livro` sem saber o que esse metodo enxerga.
    """
    return EmprestimoService(RepositorioSQLAlchemy(db, usuario.id))
