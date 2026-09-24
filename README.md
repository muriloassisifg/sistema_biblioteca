# Biblioteca do Campus

O sistema das duas disciplinas, num repositório só. **Programação para Web
III** construiu o catálogo de livros, o **login** (cadastro, senha em hash,
crachá JWT e a porta trancada), as **migrações** (Alembic) e, agora, o
**dono**: cada bibliotecário tem o seu acervo, com **busca e filtro** na
listagem e um `422` que explica em português o que está errado.
**Programação III** construiu o empréstimo. Aqui tudo mora no mesmo `app/`,
no mesmo banco e na mesma sessão — e um completa o outro: emprestar um livro
é o único jeito de ele ficar indisponível, ninguém empresta sem se
apresentar, e só se empresta livro do próprio acervo.

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
basta o uvicorn: o banco nasce sozinho, já na última migração. E quem já
tinha um `biblioteca.db` não apaga nada: ao subir, a API aplica as migrações
que faltam. O comando no terminal fica para quando você quiser ver o Alembic
trabalhando (ou rodar uma migração sem subir a API). Depois abra
<http://127.0.0.1:8000/docs>.

Os cinco livros iniciais **não** nascem mais quando a API sobe: agora todo
livro tem dono, e livro sem dono ninguém veria. Eles nascem no cadastro da
**primeira** pessoa, no acervo dela. Quem se cadastra depois começa com o
acervo vazio.

Sem Poetry: `pip install fastapi uvicorn "pydantic[email]" sqlalchemy
python-dotenv alembic pyjwt bcrypt python-multipart` e os mesmos comandos.

## O que provar em um minuto, pelo `/docs`

O banco nasce vazio: sem livro e sem usuário. Cadastre-se — **você é a
primeira pessoa**, e é no seu acervo que os cinco livros de exemplo nascem:
**1** Dom Casmurro (livre), **2** Grande Sertão: Veredas (já emprestado),
**3** Memórias Póstumas, **4** Vidas Secas, **5** O Cortiço.

### Entrar — Web III

| pedido | resposta | por quê |
|---|---|---|
| `GET /livros/` sem token | `401` | a porta está trancada |
| `POST /usuarios/ {"nome": "Ana", "email": "ana@ifg.edu.br", "senha": "segredo1"}` | `201` | e a resposta **não** traz a senha |
| o mesmo `POST` de novo | `409` | **RN04** — um e-mail, uma conta |
| `POST /usuarios/login` com a senha errada | `401` | e-mail ou senha incorretos — sem dizer qual |
| **Authorize** no `/docs` (e-mail e senha) | o cadeado fecha | o crachá vai em toda chamada |
| `GET /usuarios/eu` | quem você é | só com token |
| `GET /livros/` | os cinco livros | a Ana chegou primeiro: o acervo inicial é dela |

Cadastre também o Bruno (`bruno@ifg.edu.br`) — ele vai servir para a última
linha da próxima tabela. Ele **não** ganha acervo nenhum: os cinco já têm
dono.

### O catálogo — Web III (com o crachá)

| pedido | resposta | por quê |
|---|---|---|
| `POST /livros/ {"titulo": "Quincas Borba", "ano": 1891}` | `201`, com `"dono_id": 1` | o dono vem do **token**, não do corpo |
| o mesmo `POST` de novo | `409` | **RN01** — o título não entra duas vezes **no seu acervo** |
| `PATCH /livros/6 {"ano": 1892}` | `200` | corrigir o ano é edição de catálogo |
| `PATCH /livros/6 {"disponivel": false}` | `409` | **RN02** — emprestar não é editar |
| `DELETE /livros/6` | `204` | está no acervo e livre |
| `DELETE /livros/2` | `409` | **RN03** — está com um leitor |
| `GET /livros/?titulo=cas` | Dom Cas**mur**ro e Vidas Se**cas** | busca por pedaço do título, sem ligar para maiúsculas |
| `GET /livros/?disponivel=false` | só o 2 | filtro |
| `POST /livros/ {"titulo": "V", "ano": 1938}` | `422` — *o titulo precisa ter pelo menos 2 caracteres* | o **schema** barrou, e a mensagem explica |
| `GET /livros/99` | `404` | não existe |
| **Authorize** como o Bruno e `GET /livros/` | `[]` | **RN05** — cada um enxerga só o seu |
| ainda como o Bruno, `GET /livros/1` | `404` | não `403`: um `403` já contaria que o livro da Ana existe |

`409` é decisão do **service**; `422` vem do **schema**, antes de o seu
código rodar; `404` é do protocolo; `401` é do porteiro.

### O empréstimo — P3 (com o crachá)

Empreste de volta como a Ana: **só se empresta livro do próprio acervo**.
Cada tipo de leitor tem a sua regra — é o Strategy do encontro 7. Os números
moram em `app/emprestimos/regras.json` (Factory Method, encontro 8):

| tipo de leitor | livros ao mesmo tempo | prazo |
|---|---|---|
| `aluno` | 3 | 14 dias |
| `professor` | 5 | 30 dias — 60 no recesso, de 18/12 a 01/02 |
| `servidor` | 4 | 21 dias |
| `visitante` | 1 | 7 dias |

| pedido | resposta |
|---|---|
| `POST /emprestimos/ {"livro_id": 1, "leitor_id": 42, "tipo_leitor": "aluno"}` | `201` — `devolver_ate` daqui a 14 dias |
| o mesmo pedido de novo | `409` — já emprestado |
| `{"livro_id": 99, "leitor_id": 42, "tipo_leitor": "aluno"}` | `404` — não está no acervo |
| `{"livro_id": 2, "leitor_id": 42, "tipo_leitor": "aluno"}` | `409` — nasce indisponível |
| mais dois livros para o leitor 42, e um quarto | `409` — o limite do aluno mordeu |
| `{"livro_id": 5, "leitor_id": 9, "tipo_leitor": "egresso"}` | `422` — tipo desconhecido, e a mensagem lista os aceitos |
| `{"livro_id": 5, "leitor_id": 9, "tipo_leitor": "professor"}` | `201` — daqui a 30 dias (60 no recesso) |
| cadastre dois livros e peça os dois com `"leitor_id": 7, "tipo_leitor": "visitante"` | `201` no primeiro (7 dias), `409` no segundo — visitante leva um só |
| **Authorize** como o Bruno e peça o livro 1 | `404` — não está *no acervo dele* |

Esse `422` não vem do schema: `tipo_leitor` é um `str` qualquer, de
propósito. Quem conhece os tipos é o `politicas.py`; um `Literal` no schema
seria uma segunda lista para manter.

**Mudar um número não abre nenhum `.py`.** Troque os dias do aluno no
`regras.json` e salve: o arquivo é lido a cada pedido, e o servidor nem
precisa reiniciar. Um tipo novo só com prazo e limite (um `"egresso": {"dias":
10, "livros": 2}`) também entra só no JSON: quem o cria é a `PoliticaPadrao`.
Cada política sabe **se criar** a partir do trecho dela, no `@classmethod
criar(cls, regras)` — o professor transforma as datas do recesso, que chegam
como texto, em `date`. `politica_para` só escolhe a classe e pede
`classe.criar(...)`: não lê chave nenhuma.

E repare onde coube o acervo por dono: no `dependencias.py`, que agora monta
`RepositorioSQLAlchemy(db, usuario.id)`. O `service.py` do empréstimo não
mudou uma linha — ele continua com o mesmo `if livro is None`, e nunca ouviu
falar em dono.

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
    ├── 1ee353fc967a_…     a primeira: livros, emprestimos e usuarios
    ├── df904534ea10_…     a segunda: tipo_leitor e devolver_ate em emprestimos (P3, encontro 7)
    └── 79cbc6acad0d_…     a terceira: dono_id em livros (Web III, encontro 7)
app/
├── database.py            conexão, sessão, Base e get_db — do projeto INTEIRO
├── seguranca.py           hash da senha, token JWT e get_current_user — do projeto INTEIRO
├── main.py                junta os routers, migra o banco ao subir e traduz recusa em HTTP
├── livros/                                     (Web III — o catálogo, atrás da porta)
│   ├── models.py          a entidade como tabela — com dono_id e o relacionamento
│   ├── schemas.py         o que entra e o que sai; os validadores explicam em português
│   ├── erros.py           uma exceção por recusa
│   ├── repository.py      as consultas — o único que fala SQL; a listagem filtra dono, título e disponível
│   ├── service.py         as regras RN01, RN02, RN03 e RN05 — todas recebem o usuário
│   ├── controller.py      as rotas: recebe (o usuário e os ?filtros=), delega, responde
│   └── acervo.py          os cinco livros iniciais — só para a aula
├── usuarios/                                   (Web III — quem entra)
│   ├── models.py          a tabela usuarios (com senha_hash, nunca senha) e os livros dela
│   ├── schemas.py         o que entra (com senha) e o que sai (sem)
│   ├── erros.py           e-mail repetido, credenciais inválidas
│   ├── repository.py      as consultas
│   ├── service.py         cadastrar e autenticar — o hash nasce aqui, e o acervo da primeira pessoa
│   └── controller.py      POST /usuarios/, POST /usuarios/login, GET /usuarios/eu
└── emprestimos/                                (P3 — o empréstimo, atrás da porta)
    ├── models.py          a tabela de empréstimos
    ├── schemas.py         contratos de entrada e saída
    ├── erros.py           as quatro recusas
    ├── politicas.py       Strategy e Factory Method: as políticas, e cada uma sabe se criar
    ├── regras.json        os números: prazos, limites e o recesso do professor
    ├── repositorio.py     as consultas — uma classe, que só enxerga o acervo do dono
    ├── service.py         EmprestimoService: as regras, com o repositório injetado
    ├── dependencias.py    escolhe qual repositório o Service recebe, e com qual dono
    └── controller.py      a rota
tests/                     as tabelas acima, rodando sozinhas (pytest)
```

`seguranca.py` fica em `app/`, e não em `usuarios/`, pelo mesmo motivo do
`database.py`: livros e empréstimos também usam o `get_current_user`. O que
é de todos mora no andar de cima.

## A porta, e quem está do outro lado

```python
router = APIRouter(prefix="/livros", tags=["Livros"],
                   dependencies=[Depends(get_current_user)])
```

Essa linha tranca todas as rotas do router — em `livros/` e em
`emprestimos/`. Ela só diz *se* a pessoa entra; para saber **quem** é, a rota
pede o mesmo porteiro como parâmetro:

```python
def listar(titulo: str | None = None, disponivel: bool | None = None,
           usuario: Usuario = Depends(get_current_user),
           db: Session = Depends(get_db)):
    return service.listar(db, usuario, titulo, disponivel)
```

É a mesma dependência, nos dois papéis. E é por isso que o `dono_id` **não**
precisa (nem pode) vir no corpo do pedido: ele vem do token.

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
| `politicas.py` | Strategy — uma política por tipo de leitor (P3, encontro 7) |
| `criar(cls, regras)` | Factory Method — cada política se cria a partir do `regras.json` (P3, encontro 8) |
| `repository.py` / `repositorio.py` | Repository — quem fala com o banco |
| `Depends(...)` | Injeção de Dependência |
| `@app.exception_handler` | Corrente de Responsabilidade — o elo que traduz recusa |
| `app.include_router` | Composite |
| a `Session` (`add`, `commit`) | Unit of Work |

## Testes

```
poetry run pytest
```

Os testes criam um banco descartável e **vazio**; o fixture `client` cadastra
a Ana e faz login antes de cada caso — e é o cadastro dela, por ser o
primeiro, que traz os cinco livros. O fixture `do_bruno` faz o mesmo com uma
segunda pessoa: é com ele que se prova a fronteira entre os acervos (`[]` na
lista, `404` no livro da Ana, `404` ao tentar emprestá-lo).
`test_migracoes.py` roda o `alembic upgrade head` de verdade num banco vazio
e confere que o esquema é o mesmo dos models — e passa dois bancos antigos,
com dados dentro, pela migração seguinte, na subida e na descida.

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
- O acervo inicial de brinde para quem se cadastra primeiro resolve para a
  aula e não é prática de produção — numa biblioteca de verdade o acervo
  entra por importação, ou pelas mãos de quem cataloga. Quem cria e evolui
  tabelas é o Alembic — o `create_all` saiu.
- Os livros cadastrados **antes** do dono ficaram com `dono_id` nulo, e
  ninguém os vê: a listagem filtra pelo dono. Quem já tinha um
  `biblioteca.db` dá um dono a eles pelo cliente de banco (`UPDATE livros SET
  dono_id = 1`) ou apaga. Num banco novo isso não acontece.
- A chave estrangeira tem nome (`fk_livros_dono`) porque o SQLite, em
  migração, só cria constraint com nome. No PostgreSQL o nome é opcional —
  mas não faz mal.
- "Só o dono" é a forma mais simples de autorização. Papéis (um
  administrador que vê tudo) são outra camada, e outro dia.
- O acervo é de cada bibliotecário, mas o **leitor** ainda é de todos: o
  limite de empréstimos conta por `leitor_id`, e o leitor 42 é o mesmo para
  a Ana e para o Bruno. Separar os leitores por biblioteca seria a próxima
  coluna — e não é a desta aula.
- O token vale por 60 minutos e não há "sair": logout, em JWT, é o token
  vencer (ou o cliente jogá-lo fora).
- O cadastro é aberto (auto-cadastro). Num sistema em que só um
  administrador cria contas, `POST /usuarios/` também vai atrás do porteiro,
  com uma checagem de papel — e a primeira conta nasce por uma migração de
  dados.
- O `tipo_leitor` vem no corpo do pedido, e qualquer um se declara professor.
  Num sistema de verdade ele viria do cadastro de quem está logado — uma
  coluna `tipo` em `usuarios` —, e não do corpo. Aqui fica no corpo para
  bater com a aula.
- A camada de dados tem dois nomes — `repository.py` em Web III,
  `repositorio.py` em P3. É a mesma camada; cada turma a chamou como aprendeu
  a chamar.
