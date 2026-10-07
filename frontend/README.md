# Biblioteca do Campus — o app

O app em Flutter da biblioteca (Programação para Web III, a partir do
encontro 8): o salão, enquanto a API, na pasta `app/` da raiz, é a cozinha. Ele
roda no navegador e fala com a API pela rede.

Até aqui ele tem o **login**, o **cadastro**, as telas com nome (início, livros
e perfil), um menu lateral e a **sessão**, que fica guardada no aparelho. A
tela de livros é um lugar reservado: a listagem vem adiante.

## Rodar

Suba a API antes, na porta 8000, na raiz do repositório:

```
uvicorn app.main:app --reload
```

O app a procura em `http://127.0.0.1:8000`, no
`lib/repositories/usuario_repository.dart`. Depois, aqui em `frontend/`:

```
flutter pub get
flutter run -d chrome
```

Precisa do Flutter e do Chrome. Na primeira vez o app abre no login: clique em
**Criar uma conta**.

## Testar

```
flutter analyze
flutter test
```

São 22 testes, e nenhum precisa do uvicorn: a API é de mentira (um
`MockClient`) e o aparelho também (o `SharedPreferences.setMockInitialValues`).

## As camadas

O app segue as mesmas camadas da API, cada uma na sua pasta, com nome em
inglês:

| pasta | o que faz |
|---|---|
| `main.dart` | monta o app: o repositório entra no service, e o service fica no topo, no Provider; restaura a sessão antes da primeira tela |
| `routes.dart` | o nome de cada tela (`AppRoutes`) |
| `screens/` e `widgets/` | a apresentação: recebem o clique, pedem ao service e mostram a resposta (`widgets/` tem o menu e o guarda de rotas) |
| `services/` | as regras: `sessao_service.dart` — entrar, cadastrar, restaurar e sair, e quem está logado |
| `repositories/` | falam com o mundo de fora: `usuario_repository.dart` com a API, `token_repository.dart` com o aparelho |
| `models/` | o formato dos dados (`usuario.dart`) |

A tela nunca faz HTTP, e o repositório nunca mostra mensagem na tela.

## O cadastro de verdade

A tela de cadastro faz o mesmo caminho da de login: recebe o clique, pede ao
`SessaoService.cadastrar` e mostra a resposta. O repositório manda
`POST /usuarios/` com os dados **em JSON** (o login, ao contrário, manda um
formulário) e espera `201`. Quando a API recusa:

| resposta da API | o que o app mostra |
|---|---|
| `409` (o e-mail já tem conta) | *Já existe uma conta com este e-mail* |
| `422` (campo inválido) | `campo: mensagem` do primeiro erro que a API listou |
| a API não responde | *Não consegui falar com a API. O uvicorn está rodando?* |

Deu certo, o service **entra com a conta nova** pelo mesmo caminho do login, e o
app abre a tela inicial já logado.

## A sessão guardada

O token que o login devolve agora fica no aparelho, e não só na memória. O
`TokenRepository` é o único que sabe onde: usa o `shared_preferences`, que no
navegador é o **`localStorage`** do Chrome (na chave `flutter.token`) e, num
celular, um arquivo do app. O service pede só *ler*, *salvar* e *apagar*.

- **entrar** (e cadastrar) guarda o token;
- **ao abrir**, o `main` chama `restaurar()` antes de mostrar a primeira tela: se há
  token guardado e a API ainda o aceita (`GET /usuarios/eu`), a sessão volta e o
  app abre logado;
- **o token que a API recusa** (venceu — ele vale 60 minutos — ou não vale mais) é
  apagado, e o app abre no login;
- **com a API parada**, o token fica guardado: o app abre no login, e quando a
  API voltar a sessão volta no próximo F5;
- **sair** apaga o token e a sessão.

## Honestidades

- O token fica no `localStorage` do navegador: qualquer script que rode nessa
  página o lê. Para um app de aula serve; num produto de verdade o cuidado é
  outro (um cookie `HttpOnly`, ou o armazenamento seguro do celular).
- A sessão sobrevive ao **F5**, ao `r` e ao `R` do terminal do `flutter run`, mas
  **não** a um novo `flutter run`: a porta do app muda a cada execução, e o
  `localStorage` é de cada endereço — o app novo é outro endereço, sem token.
- O `WidgetsFlutterBinding.ensureInitialized()` do `main` existe para o celular
  (o Flutter o exige de quem usa um pacote do aparelho antes do `runApp`); no
  Chrome o app abriria sem ele. Isto não foi testado num celular.
- O `422` do cadastro chega em inglês, com as mensagens padrão do Pydantic
  (*String should have at least 6 characters*); o do cadastro de livros é que foi
  traduzido na API.
- O app e a API vivem no mesmo repositório mas não têm nada em comum além do
  contrato HTTP: o endereço `127.0.0.1:8000` está escrito em
  `usuario_repository.dart`.
