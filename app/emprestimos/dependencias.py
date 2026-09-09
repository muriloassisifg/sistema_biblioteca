from fastapi import Depends
from sqlalchemy.orm import Session

from ..database import get_db
from .repositorio import RepositorioSQLAlchemy
from .service import EmprestimoService


def obter_service(db: Session = Depends(get_db)):
    """Monta o Service ja' com o repositorio de producao dentro.

    Este e' o unico arquivo do sistema que escolhe QUAL repositorio o Service
    vai usar. Trocar de banco e' trocar a classe que aparece nesta linha.

    A sessao chega pelo mesmo mecanismo que entrega o Service a rota: uma
    dependencia que depende de outra. O FastAPI resolve o `get_db` primeiro,
    entrega o `db` aqui, e so' entao chama a rota com o Service pronto.
    """
    return EmprestimoService(RepositorioSQLAlchemy(db))
