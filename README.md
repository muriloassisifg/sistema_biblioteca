# Biblioteca do Campus

O sistema das duas disciplinas, num repositório só. **Programação para Web
III** construiu o catálogo de livros (o tutorial "da pasta vazia às três
camadas"); **Programação III** construiu o empréstimo (encontros 3 a 6). Aqui
os dois moram no mesmo `app/`, usam o mesmo banco e a mesma sessão — e um
completa o outro: emprestar um livro é o único jeito de ele ficar
indisponível.

> Quem cursa as duas vê a mesma biblioteca dos dois lados: em Web III o foco
> é *como ela funciona*; em P3, *como ela é por dentro*.

## Rodar

```
poetry install
```

Renomeie `env.exemplo` para `.env`. Ele já vem apontando para o SQLite — um
arquivo `biblioteca.db` que nasce sozinho, com cinco livros dentro.

```
poetry run uvicorn app.main:app --reload
```

Depois abra <http://127.0.0.1:8000/docs>.

Sem Poetry: `pip install fastapi uvicorn pydantic sqlalchemy python-dotenv`
e o mesmo `uvicorn`.

## O que provar em um minuto, pelo `/docs`

A biblioteca nasce com cinco livros: **1** Dom Casmurro (livre), **2** Grande
Sertão: Veredas (já emprestado), **3** Memórias Póstumas, **4** Vidas Secas,
**5** O Cortiço.

### O catálogo — Web III

| pedido | resposta | por quê |
|---|---|---|
| `POST /livros/ {"titulo": "Quincas Borba", "ano": 1891}` | `201` | |
| o mesmo `POST` de novo | `409` | **RN01** — o título não entra duas vezes |
| `PATCH /livros/6 {"ano": 1892}` | `200` | corrigir o ano é edição de catálogo |
| `PATCH /livros/6 {"disponivel": false}` | `409` | **RN02** — emprestar não é editar |
| `DELETE /livros/6` | `204` | está no acervo e livre |
| `DELETE /livros/2` | `409` | **RN03** — está com um leitor |
| `POST /livros/ {"titulo": "V", "ano": 1938}` | `422` | o **schema** barrou: título curto |
| `GET /livros/99` | `404` | não existe |

`409` é decisão do **service**; `422` vem do **schema**, antes de o seu
código rodar; `404` é do protocolo.

### O empréstimo — P3

| pedido | resposta |
|---|---|
| `POST /emprestimos/ {"livro_id": 1, "leitor_id": 42}` | `201` |
| o mesmo pedido de novo | `409` — já emprestado |
| `{"livro_id": 99, "leitor_id": 42}` | `404` — não está no acervo |
| `{"livro_id": 2, "leitor_id": 42}` | `409` — nasce indisponível |
| mais dois livros para o leitor 42, e um quarto | `409` — o limite mordeu |

### Onde as duas turmas se encontram

Depois do primeiro `POST /emprestimos/`:

| pedido | resposta | por quê |
|---|---|---|
| `GET /livros/1` | `"disponivel": false` | o catálogo enxerga o empréstimo |
| `PATCH /livros/1 {"disponivel": true}` | `409` | **RN02** — quem devolve é o empréstimo, não o catálogo |
| `DELETE /livros/1` | `409` | **RN03** — está com um leitor |

Pare o servidor, suba de novo e repita o primeiro pedido: continua `409`. Os
dados sobreviveram ao processo — que é o motivo de o banco existir.

## Onde cada coisa mora

```
app/
├── database.py            conexão, sessão, Base e get_db — do projeto INTEIRO
├── main.py                junta os routers, cria as tabelas e traduz recusa em HTTP
├── livros/                                     (Web III — o catálogo)
│   ├── models.py          a entidade como tabela (SQLAlchemy)
│   ├── schemas.py         o que entra e o que sai (Pydantic)
│   ├── erros.py           uma exceção por recusa
│   ├── repository.py      as consultas — o único que fala SQL
│   ├── service.py         as regras RN01, RN02 e RN03
│   ├── controller.py      as rotas: recebe, delega, responde
│   └── acervo.py          os cinco livros iniciais — só para a aula
└── emprestimos/                                (P3 — o empréstimo)
    ├── models.py          a tabela de empréstimos
    ├── schemas.py         contratos de entrada e saída
    ├── erros.py           as três recusas
    ├── repositorio.py     as consultas — uma classe, para poder ser trocada
    ├── service.py         EmprestimoService: as regras, com o repositório injetado
    ├── dependencias.py    escolhe qual repositório o Service recebe
    └── controller.py      a rota
tests/                     as tabelas acima, rodando sozinhas (pytest)
```

Os `__init__.py` podem estar vazios, mas precisam existir: sem eles o import
falha com `ModuleNotFoundError`.

## Dois estilos, de propósito

`livros/` está exatamente como o tutorial de Web III o escreveu: funções, e a
sessão do banco atravessa o service. `emprestimos/` está como P3 o desenhou:
o Service é uma classe que **recebe** o repositório, e `dependencias.py`
decide qual. É o mesmo movimento um andar acima — e
`tests/test_emprestimo_service.py` mostra o que ele compra: as regras do
empréstimo rodam sem FastAPI, sem servidor e sem banco.

O `service.py` de empréstimos é o do encontro 5 de P3, **caractere a
caractere**. Só o repositório mudou — de SQLite escrito à mão para
SQLAlchemy —, pela terceira vez, e pela terceira vez o Service não soube.

## Os padrões que já têm nome

| onde | padrão | visto em |
|---|---|---|
| `controller.py` | Controller — a fronteira da aplicação | P3 e3 · Web III |
| `service.py` | Service — onde mora a regra | P3 e4 · Web III |
| `repository.py` / `repositorio.py` | Repository — quem fala com o banco | P3 e5 · Web III |
| `Depends(...)` | Injeção de Dependência | P3 e6 |
| `@app.exception_handler` | Corrente de Responsabilidade — o elo que traduz recusa | P3 e6 · Web III passo 16 |
| `app.include_router` | Composite | P3 e6 |

## Testes

```
poetry run pytest
```

Pytest é assunto do encontro 12 de P3. Já está aqui porque as tabelas lá de
cima precisam continuar verdadeiras a cada mudança — e porque o teste do
service sem banco é a prova de que a injeção serve para alguma coisa.

## PostgreSQL — os passos 19 e 20 de Web III

Suba o Postgres, crie o banco `biblioteca` e troque a linha do `.env`:

```
DATABASE_URL=postgresql+psycopg://biblioteca:senha_secreta@localhost:5432/biblioteca
```

Nenhum arquivo dentro de `app/` muda. É a prova de que separar as camadas
serviu para alguma coisa.

## Honestidades

- O `db` atravessa o service de livros. Ele não abre conexão, não consulta e
  não importa o SQLAlchemy — só repassa —, mas o parâmetro está lá. Não é o
  desenho mais puro possível; é o que o encontro precisava, e o
  `emprestimos/` mostra o passo seguinte.
- `Base.metadata.create_all()` e o acervo inicial no boot resolvem para a
  aula e não são prática de produção: criam o que falta e não sabem
  **evoluir** o que já existe. Em projeto de verdade isso vira uma ferramenta
  de migração (Alembic).
- O livro 2 nasce indisponível sem um empréstimo registrado. É o acervo do
  encontro 5 de P3, mantido para as tabelas acima continuarem valendo.
- A camada de dados tem dois nomes — `repository.py` em Web III,
  `repositorio.py` em P3. É a mesma camada; cada turma a chamou como aprendeu
  a chamar.
