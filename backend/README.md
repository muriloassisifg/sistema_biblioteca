# Biblioteca do Campus — o livro tem dono

O projeto com login e migrações, mais o que o checkpoint pede: o livro
ganha **dono** (um usuário tem muitos livros), cada pessoa enxerga e mexe só
no próprio acervo, a listagem tem **busca e filtro**, e o `422` explica o
que está errado em português. A coluna nova entrou por uma **migração** —
o `create_all` não existe mais.

> É o mesmo sistema de Programação III, de propósito. Quem cursa as duas vê a
> mesma biblioteca dos dois lados: lá o foco é *como ele é por dentro*; aqui,
> *como ele funciona*.

## Rodar

```
poetry install
```

Renomeie `env.exemplo` para `.env` (URL do banco e `SECRET_KEY`).

```
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload
```

O `upgrade head` aplica as **duas** migrações: a que cria `livros` e
`usuarios`, e a que acrescenta `livros.dono_id`. Depois abra
<http://127.0.0.1:8000/docs>.

## O que provar em um minuto, pelo `/docs`

Cadastre duas pessoas (`ana@ifg.edu.br` e `bruno@ifg.edu.br`) e faça
**Authorize** como a Ana.

| pedido | resposta | por quê |
|---|---|---|
| `POST /livros/ {"titulo": "Dom Casmurro", "ano": 1899}` | `201`, com `"dono_id": 1` | o dono veio do token, não do pedido |
| `GET /livros/` | só os livros da Ana | **RN05** — cada um enxerga só o que é seu |
| `GET /livros/?titulo=cas` | os que têm "cas" no título | busca |
| `GET /livros/?disponivel=false` | os emprestados | filtro |
| `POST /livros/ {"titulo": "V", "ano": 3000}` | `422` com "o titulo precisa ter…" e "o ano precisa estar…" | mensagens que explicam |
| Authorize como o Bruno, `GET /livros/` | `[]` | o acervo é dele — vazio |
| como o Bruno, `GET /livros/1` | `404` | não `403`: não se revela que o livro da Ana existe |

## Os testes

```
poetry run pytest
```

Não precisa da API no ar nem do `.env`: o `conftest.py` manda o teste usar um
banco só dele, o `teste.db`, que nasce vazio a cada teste. O seu banco nem é
aberto. O resultado esperado é `9 passed`.

## Onde cada coisa mora

```
conftest.py                    o banco do teste e o cliente, para todo teste
tests/test_livros.py           os nove testes de endpoint
alembic/versions/
├── …_livros_e_usuarios.py     a primeira migração: o ponto de partida
└── …_dono_id_em_livros.py     a segunda: a coluna nova, em modo batch (SQLite)
app/
├── livros/
│   ├── models.py          + dono_id (ForeignKey) e dono (relationship)
│   ├── schemas.py         + dono_id na saída; validadores com mensagens em português
│   ├── repository.py      listar(db, dono_id, titulo, disponivel) — a consulta montada aos poucos
│   ├── service.py         toda regra recebe o usuário; RN05 é 404
│   └── controller.py      cada rota recebe o usuário; ?titulo= e ?disponivel= são parâmetros de consulta
└── usuarios/models.py     + livros (o outro lado do relacionamento)
```

## Honestidades

- Os livros cadastrados **antes** do dono ficaram com `dono_id` nulo — e
  ninguém os vê. Dê um dono pelo cliente de banco (`UPDATE livros SET
  dono_id = 1`) ou apague-os.
- A chave estrangeira tem nome (`fk_livros_dono`) porque o SQLite, em
  migração, só cria constraint com nome. No PostgreSQL o nome é opcional —
  mas não faz mal.
- "Só o dono" é a forma mais simples de autorização. Papéis (um
  administrador que vê tudo) são outra camada, e outro dia.
