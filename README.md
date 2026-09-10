# Biblioteca do Campus

O sistema das duas disciplinas, num repositório só. **Programação para Web
III** construiu o catálogo de livros e, agora, o **login** (cadastro, senha
em hash, crachá JWT e a porta trancada) e as **migrações** (Alembic).
**Programação III** construiu o empréstimo. Aqui tudo mora no mesmo `app/`,
no mesmo banco e na mesma sessão — e um completa o outro: emprestar um livro
é o único jeito de ele ficar indisponível, e ninguém empresta sem se
apresentar.

> Quem cursa as duas vê a mesma biblioteca dos dois lados: em Web III o foco
> é *como ela funciona*; em P3, *como ela é por dentro*.

## Rodar

```
poetry install
```

Renomeie `env.exemplo` para `.env`. Ele traz a URL do banco (SQLite, sem
instalar nada) e a `SECRET_KEY` que assina os tokens — troque a frase.

```
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload
```

O `upgrade head` cria as tabelas a partir das migrações — não há
`create_all`. A API roda esse mesmo comando ao subir, então num clone novo
basta o uvicorn: o banco nasce sozinho, já na última migração. O comando no
terminal fica para quando você quiser ver o Alembic trabalhando (ou rodar
uma migração sem subir a API). Ao subir, a API também põe os cinco livros
iniciais se a biblioteca estiver vazia. Depois abra
<http://127.0.0.1:8000/docs>.

Sem Poetry: `pip install fastapi uvicorn "pydantic[email]" sqlalchemy
python-dotenv alembic pyjwt bcrypt python-multipart` e os mesmos comandos.

## O que provar em um minuto, pelo `/docs`

A biblioteca nasce com cinco livros: **1** Dom Casmurro (livre), **2** Grande
Sertão: Veredas (já emprestado), **3** Memórias Póstumas, **4** Vidas Secas,
**5** O Cortiço. E com nenhum usuário: o primeiro é você.

### Entrar — Web III

| pedido | resposta | por quê |
|---|---|---|
| `GET /livros/` sem token | `401` | a porta está trancada |
| `POST /usuarios/ {"nome": "Ana", "email": "ana@ifg.edu.br", "senha": "segredo1"}` | `201` | e a resposta **não** traz a senha |
| o mesmo `POST` de novo | `409` | **RN04** — um e-mail, uma conta |
| `POST /usuarios/login` com a senha errada | `401` | e-mail ou senha incorretos — sem dizer qual |
| **Authorize** no `/docs` (e-mail e senha) | o cadeado fecha | o crachá vai em toda chamada |
| `GET /usuarios/eu` | quem você é | só com token |

### O catálogo — Web III (com o crachá)

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
código rodar; `404` é do protocolo; `401` é do porteiro.

### O empréstimo — P3 (com o crachá)

| pedido | resposta |
|---|---|
| `POST /emprestimos/ {"livro_id": 1, "leitor_id": 42}` | `201` |
| o mesmo pedido de novo | `409` — já emprestado |
| `{"livro_id": 99, "leitor_id": 42}` | `404` — não está no acervo |
| `{"livro_id": 2, "leitor_id": 42}` | `409` — nasce indisponível |
| mais dois livros para o leitor 42, e um quarto | `409` — o limite mordeu |

### Onde as duas turmas se encontram

Depois do primeiro `POST /emprestimos/`: `GET /livros/1` mostra
`"disponivel": false`; `PATCH /livros/1 {"disponivel": true}` → `409` (RN02:
quem devolve é o empréstimo, não o catálogo); `DELETE /livros/1` → `409`
(RN03).

Pare o servidor, abra a tabela `usuarios` no seu cliente de banco: a coluna
`senha_hash` começa com `$2b$` e não tem a senha em lugar nenhum.

## Onde cada coisa mora

```
alembic.ini                o Alembic gerou; a URL vem do .env
alembic/
├── env.py                 ensina o Alembic a achar o banco e os três models
└── versions/              uma migração por mudança de tabela — o histórico do banco
app/
├── database.py            conexão, sessão, Base e get_db — do projeto INTEIRO
├── seguranca.py           hash da senha, token JWT e get_current_user — do projeto INTEIRO
├── main.py                junta os routers, semeia o acervo ao subir e traduz recusa em HTTP
├── livros/                                     (Web III — o catálogo, atrás da porta)
│   ├── models.py          a entidade como tabela (SQLAlchemy)
│   ├── schemas.py         o que entra e o que sai (Pydantic)
│   ├── erros.py           uma exceção por recusa
│   ├── repository.py      as consultas — o único que fala SQL
│   ├── service.py         as regras RN01, RN02 e RN03
│   ├── controller.py      as rotas: recebe, delega, responde
│   └── acervo.py          os cinco livros iniciais — só para a aula
├── usuarios/                                   (Web III — quem entra)
│   ├── models.py          a tabela usuarios (com senha_hash, nunca senha)
│   ├── schemas.py         o que entra (com senha) e o que sai (sem)
│   ├── erros.py           e-mail repetido, credenciais inválidas
│   ├── repository.py      as consultas
│   ├── service.py         cadastrar e autenticar — o hash nasce aqui
│   └── controller.py      POST /usuarios/, POST /usuarios/login, GET /usuarios/eu
└── emprestimos/                                (P3 — o empréstimo, atrás da porta)
    ├── models.py          a tabela de empréstimos
    ├── schemas.py         contratos de entrada e saída
    ├── erros.py           as três recusas
    ├── repositorio.py     as consultas — uma classe, para poder ser trocada
    ├── service.py         EmprestimoService: as regras, com o repositório injetado
    ├── dependencias.py    escolhe qual repositório o Service recebe
    └── controller.py      a rota
tests/                     as tabelas acima, rodando sozinhas (pytest)
```

`seguranca.py` fica em `app/`, e não em `usuarios/`, pelo mesmo motivo do
`database.py`: livros e empréstimos também usam o `get_current_user`. O que
é de todos mora no andar de cima.

## A porta, em uma linha

```python
router = APIRouter(prefix="/livros", tags=["Livros"],
                   dependencies=[Depends(get_current_user)])
```

Todas as rotas do router passam a exigir token — em `livros/` e em
`emprestimos/`. Quando uma rota precisar **saber quem** é o usuário (o livro
ganhar dono), ela pede o `Depends(get_current_user)` como parâmetro — é o
que `GET /usuarios/eu` já faz.

## Dois estilos, de propósito

`livros/` e `usuarios/` estão como o tutorial de Web III os escreveu:
funções, e a sessão do banco atravessa o service. `emprestimos/` está como P3
o desenhou: o Service é uma classe que **recebe** o repositório, e
`dependencias.py` decide qual. É o mesmo movimento um andar acima — e
`tests/test_emprestimo_service.py` mostra o que ele compra: as regras do
empréstimo rodam sem FastAPI, sem servidor e sem banco.

## Os padrões que já têm nome

| onde | padrão |
|---|---|
| `controller.py` | Controller — a fronteira da aplicação |
| `service.py` | Service — onde mora a regra |
| `repository.py` / `repositorio.py` | Repository — quem fala com o banco |
| `Depends(...)` | Injeção de Dependência |
| `@app.exception_handler` | Corrente de Responsabilidade — o elo que traduz recusa |
| `app.include_router` | Composite |
| a `Session` (`add`, `commit`) | Unit of Work |

## Testes

```
poetry run pytest
```

Os testes criam um banco descartável, cadastram a Ana e fazem login antes de
cada caso; `test_migracoes.py` roda o `alembic upgrade head` de verdade num
banco vazio e confere que o esquema é o mesmo dos models.

## PostgreSQL

Suba o Postgres, crie o banco `biblioteca` e troque a linha do `.env`:

```
DATABASE_URL=postgresql+psycopg://biblioteca:senha_secreta@localhost:5432/biblioteca
```

Depois `poetry run alembic upgrade head`: o banco novo nasce com todas as
migrações. Nenhum arquivo dentro de `app/` muda.

## Honestidades

- O `db` atravessa o service de livros e de usuários. Não é o desenho mais
  puro possível; `emprestimos/` mostra o passo seguinte.
- O acervo inicial no boot resolve para a aula e não é prática de produção.
  Quem cria e evolui tabelas agora é o Alembic — o `create_all` saiu.
- O token vale por 60 minutos e não há "sair": logout, em JWT, é o token
  vencer (ou o cliente jogá-lo fora).
- O cadastro é aberto (auto-cadastro). Num sistema em que só um
  administrador cria contas, `POST /usuarios/` também vai atrás do porteiro,
  com uma checagem de papel — e a primeira conta nasce por uma migração de
  dados.
- A camada de dados tem dois nomes — `repository.py` em Web III,
  `repositorio.py` em P3. É a mesma camada; cada turma a chamou como aprendeu
  a chamar.
