from fastapi import APIRouter, Depends

from .dependencias import obter_service
from .schemas import EmprestimoEntrada, EmprestimoPublico
from .service import EmprestimoService

router = APIRouter(prefix="/emprestimos", tags=["Emprestimos"])

# Nenhum `try` aqui: as recusas do Service viram HTTP no tradutor registrado
# no main.py, uma vez para todas as rotas (encontro 6 de P3).


@router.post("/", status_code=201, response_model=EmprestimoPublico)
def criar_emprestimo(
    dados: EmprestimoEntrada,
    service: EmprestimoService = Depends(obter_service),
):
    return service.emprestar(dados.livro_id, dados.leitor_id)
