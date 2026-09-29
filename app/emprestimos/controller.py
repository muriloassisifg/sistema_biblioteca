from fastapi import APIRouter, Depends

from ..seguranca import get_current_user
from .dependencias import obter_devolucao, obter_service
from .devolucao import DevolucaoFacade
from .schemas import ComprovanteDeDevolucao, EmprestimoEntrada, EmprestimoPublico
from .service import EmprestimoService

# A mesma porta de livros: ninguem empresta sem se apresentar.
router = APIRouter(
    prefix="/emprestimos",
    tags=["Emprestimos"],
    dependencies=[Depends(get_current_user)],
)

# Nenhum `try` aqui: as recusas do Service viram HTTP no tradutor registrado
# no main.py, uma vez para todas as rotas (encontro 6 de P3).


@router.post("/", status_code=201, response_model=EmprestimoPublico)
def criar_emprestimo(
    dados: EmprestimoEntrada,
    service: EmprestimoService = Depends(obter_service),
):
    return service.emprestar(dados.livro_id, dados.leitor_id, dados.tipo_leitor)


# A devolucao chama UMA peca, a fachada: quais pecas entram e em que ordem e'
# assunto dela (encontro 9 de P3). O emprestar, que so' mexe num assunto,
# continua indo direto ao Service.
@router.post("/{emprestimo_id}/devolucao", response_model=ComprovanteDeDevolucao)
def devolver_livro(
    emprestimo_id: int,
    devolucao: DevolucaoFacade = Depends(obter_devolucao),
):
    return devolucao.devolver(emprestimo_id)
