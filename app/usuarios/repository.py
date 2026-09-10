from sqlalchemy.orm import Session

from .models import Usuario

# Igual ao de livros: a UNICA parte que sabe que existe uma tabela usuarios.


def buscar(db: Session, usuario_id: int):
    return db.query(Usuario).filter(Usuario.id == usuario_id).first()


def buscar_por_email(db: Session, email: str):
    return db.query(Usuario).filter(Usuario.email == email).first()


def criar(db: Session, dados: dict):
    usuario = Usuario(**dados)
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario
