from sqlalchemy.orm import Session

from .models import Livro

# A UNICA parte do sistema que sabe que existe um banco. Se aparecer um
# `db.query` fora daqui, a camada vazou.


def listar(db: Session, dono_id: int, titulo: str | None = None, disponivel: bool | None = None):
    # A consulta vai sendo montada: o filtro do dono sempre entra; os outros,
    # so' quando quem chamou pediu. Nada vai ao banco ate' o .all().
    consulta = db.query(Livro).filter(Livro.dono_id == dono_id)
    if titulo:
        consulta = consulta.filter(Livro.titulo.ilike(f"%{titulo}%"))
    if disponivel is not None:
        consulta = consulta.filter(Livro.disponivel == disponivel)
    return consulta.order_by(Livro.titulo).all()


def buscar(db: Session, livro_id: int):
    return db.query(Livro).filter(Livro.id == livro_id).first()


def criar(db: Session, dados: dict):
    livro = Livro(**dados)
    db.add(livro)
    db.commit()
    db.refresh(livro)   # o id nasce no banco; sem isto ele vem None
    return livro


def buscar_por_titulo(db: Session, dono_id: int, titulo: str):
    # O titulo e' unico DENTRO do acervo de cada pessoa, nao no mundo.
    return db.query(Livro).filter(Livro.dono_id == dono_id, Livro.titulo == titulo).first()


def atualizar(db: Session, livro: Livro, mudancas: dict):
    for campo, valor in mudancas.items():
        setattr(livro, campo, valor)
    db.commit()
    db.refresh(livro)
    return livro


def apagar(db: Session, livro: Livro):
    db.delete(livro)
    db.commit()
