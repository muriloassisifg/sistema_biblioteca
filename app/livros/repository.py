from sqlalchemy.orm import Session

from .models import Livro

# A UNICA parte do sistema que sabe que existe um banco. Se aparecer um
# `db.query` fora daqui, a camada vazou.


def listar(db: Session):
    return db.query(Livro).all()


def buscar(db: Session, livro_id: int):
    return db.query(Livro).filter(Livro.id == livro_id).first()


def criar(db: Session, dados: dict):
    livro = Livro(**dados)
    db.add(livro)
    db.commit()
    db.refresh(livro)   # o id nasce no banco; sem isto ele vem None
    return livro


def buscar_por_titulo(db: Session, titulo: str):
    return db.query(Livro).filter(Livro.titulo == titulo).first()


def atualizar(db: Session, livro: Livro, mudancas: dict):
    for campo, valor in mudancas.items():
        setattr(livro, campo, valor)
    db.commit()
    db.refresh(livro)
    return livro


def apagar(db: Session, livro: Livro):
    db.delete(livro)
    db.commit()
