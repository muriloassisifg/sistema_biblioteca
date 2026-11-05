import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:frontend/main.dart';
import 'package:frontend/models/livro.dart';
import 'package:frontend/repositories/livro_repository.dart';
import 'package:frontend/repositories/usuario_repository.dart';
import 'package:frontend/routes.dart';
import 'package:frontend/screens/cadastro_screen.dart';
import 'package:frontend/screens/formulario_screen.dart';
import 'package:frontend/screens/inicio_screen.dart';
import 'package:frontend/screens/livro_screen.dart';
import 'package:frontend/screens/livros_screen.dart';
import 'package:frontend/screens/login_screen.dart';
import 'package:frontend/screens/perfil_screen.dart';
import 'package:frontend/services/livro_service.dart';
import 'package:frontend/services/sessao_service.dart';

// Uma API de mentira, com um banco de mentira (o Map contas): responde como a
// de verdade, sem precisar do uvicorn. A Ana já tem conta, com a senha
// 'segredo123'. O token de cada conta é 'token-de-' e o e-mail dela.
// Ela conta quantos pedidos recebeu, para o teste do service conferir.
int pedidos = 0;

// O parâmetro guardado é o aparelho de mentira: o que o app tinha guardado da
// última vez que rodou. Por padrão, nada.
SessaoService sessaoDeMentira({Map<String, Object> guardado = const {}}) {
  SharedPreferences.setMockInitialValues(guardado);
  final contas = {
    'ana@biblioteca.com': {'nome': 'Ana', 'senha': 'segredo123'},
  };
  final cliente = MockClient((pedido) async {
    pedidos++;
    if (pedido.url.path == '/usuarios/' && pedido.method == 'POST') {
      final dados = jsonDecode(pedido.body);
      if (contas.containsKey(dados['email'])) {
        return http.Response(
          '{"detail": "Ja existe uma conta com o e-mail ${dados['email']}"}',
          409,
        );
      }
      if (dados['senha'].length < 6) {
        return http.Response(
          jsonEncode({
            'detail': [
              {
                'loc': ['body', 'senha'],
                'msg': 'String should have at least 6 characters',
              },
            ],
          }),
          422,
        );
      }
      contas[dados['email']] = {'nome': dados['nome'], 'senha': dados['senha']};
      return http.Response(
        jsonEncode({'id': 2, 'nome': dados['nome'], 'email': dados['email']}),
        201,
      );
    }
    if (pedido.url.path == '/usuarios/login') {
      final email = pedido.bodyFields['username'];
      if (contas[email]?['senha'] == pedido.bodyFields['password']) {
        return http.Response(
          jsonEncode({'access_token': 'token-de-$email', 'token_type': 'bearer'}),
          200,
        );
      }
      return http.Response('{"detail": "E-mail ou senha incorretos"}', 401);
    }
    if (pedido.url.path == '/usuarios/eu') {
      final email = (pedido.headers['Authorization'] ?? '').replaceFirst(
        'Bearer token-de-',
        '',
      );
      if (contas.containsKey(email)) {
        return http.Response(
          jsonEncode({'id': 1, 'nome': contas[email]!['nome'], 'email': email}),
          200,
        );
      }
    }
    return http.Response('{"detail": "Token invalido ou vencido"}', 401);
  });
  return SessaoService(UsuarioRepository(cliente: cliente));
}

// Dois livros da Ana, na forma do LivroPublico que a API devolve.
const doisLivros = [
  {'id': 1, 'titulo': 'Dom Casmurro', 'ano': 1899, 'disponivel': true, 'dono_id': 1},
  {'id': 2, 'titulo': 'Vidas Secas', 'ano': 1938, 'disponivel': false, 'dono_id': 1},
];

// A API de livros de mentira: o GET /livros/ responde com este status e este
// corpo. Como a de verdade, sem o token no cabeçalho ela responde 401. O
// GET /livros/{id} procura o livro nos dois da Ana; outro id, 404.
http.Client apiDeLivros(int status, Object corpo) {
  return MockClient((pedido) async {
    pedidos++;
    if (pedido.headers['Authorization'] == null) {
      return http.Response('{"detail": "Not authenticated"}', 401);
    }
    final id = pedido.url.pathSegments.last; // '' em /livros/, '2' em /livros/2
    if (id.isNotEmpty) {
      for (final livro in doisLivros) {
        if ('${livro['id']}' == id) {
          return http.Response(jsonEncode(livro), 200);
        }
      }
      return http.Response('{"detail": "Livro $id nao esta no seu acervo"}', 404);
    }
    return http.Response(jsonEncode(corpo), status);
  });
}

// O último endereço que o acervo de mentira recebeu: os testes da busca e do
// filtro conferem o ?titulo= e o ?disponivel= que o app mandou.
Uri? ultimoEndereco;

// O acervo de mentira, para criar, editar e excluir: ele guarda o que recebe,
// e responde como a API de verdade, com as recusas dela (o título repetido e
// o livro emprestado, 409). Começa com os dois livros da Ana. Como a API, o
// GET /livros/?titulo=... devolve só os livros com aquele pedaço no título, e o
// ?disponivel=true, só os que não estão emprestados.
http.Client acervoDeMentira() {
  final List<Map<String, dynamic>> acervo = [
    {'id': 1, 'titulo': 'Dom Casmurro', 'ano': 1899, 'disponivel': true, 'dono_id': 1},
    {'id': 2, 'titulo': 'Vidas Secas', 'ano': 1938, 'disponivel': false, 'dono_id': 1},
  ];
  return MockClient((pedido) async {
    pedidos++;
    ultimoEndereco = pedido.url;
    final id = int.tryParse(pedido.url.pathSegments.last); // null em /livros/
    if (pedido.method == 'POST' || pedido.method == 'PATCH') {
      final dados = jsonDecode(pedido.body);
      for (final livro in acervo) {
        if (livro['titulo'] == dados['titulo'] && livro['id'] != id) {
          return http.Response('{"detail": "Ja existe um livro chamado ${dados['titulo']}"}', 409);
        }
      }
      if (pedido.method == 'POST') {
        final novo = {'id': 3, 'titulo': dados['titulo'], 'ano': dados['ano'], 'disponivel': true, 'dono_id': 1};
        acervo.add(novo);
        return http.Response(jsonEncode(novo), 201);
      }
    }
    if (id == null) {
      final busca = (pedido.url.queryParameters['titulo'] ?? '').toLowerCase();
      final soDisponiveis = pedido.url.queryParameters['disponivel'] == 'true';
      final achados = [
        for (final livro in acervo)
          if ('${livro['titulo']}'.toLowerCase().contains(busca) && (!soDisponiveis || livro['disponivel'] == true))
            livro,
      ];
      return http.Response(jsonEncode(achados), 200);
    }
    for (final livro in acervo) {
      if (livro['id'] == id) {
        if (pedido.method == 'DELETE') {
          if (livro['disponivel'] == false) {
            return http.Response('{"detail": "Livro $id esta emprestado"}', 409);
          }
          acervo.remove(livro);
          return http.Response('', 204);
        }
        if (pedido.method == 'PATCH') {
          livro.addAll(jsonDecode(pedido.body));
        }
        return http.Response(jsonEncode(livro), 200);
      }
    }
    return http.Response('{"detail": "Livro $id nao esta no seu acervo"}', 404);
  });
}

// O app de verdade, com os services de mentira no topo, como o main.dart faz.
// O .value entrega ao Provider um objeto que já existe, em vez de criá-lo.
// Sem a API de livros, a de mentira responde uma lista vazia.
Widget appDeMentira(SessaoService sessao, {http.Client? livros}) {
  final repositorio = LivroRepository(cliente: livros ?? apiDeLivros(200, []));
  return MultiProvider(
    providers: [
      ChangeNotifierProvider.value(value: sessao),
      Provider.value(value: LivroService(repositorio, sessao)),
    ],
    child: const BibliotecaApp(),
  );
}

Future<void> preencherEEntrar(WidgetTester tester, String senha) async {
  await tester.enterText(find.byType(TextField).at(0), 'ana@biblioteca.com');
  await tester.enterText(find.byType(TextField).at(1), senha);
  await tester.tap(find.widgetWithText(ElevatedButton, 'Entrar'));
  await tester.pumpAndSettle();
}

Future<void> abrirOMenu(WidgetTester tester) async {
  await tester.tap(find.byIcon(Icons.menu));
  await tester.pumpAndSettle();
}

// Abre o cadastro pelo link do login e preenche os três campos.
Future<void> preencherECadastrar(WidgetTester tester, String email, String senha) async {
  await tester.tap(find.text('Criar uma conta'));
  await tester.pumpAndSettle();
  await tester.enterText(find.byType(TextField).at(0), 'Bia');
  await tester.enterText(find.byType(TextField).at(1), email);
  await tester.enterText(find.byType(TextField).at(2), senha);
  await tester.tap(find.widgetWithText(ElevatedButton, 'Cadastrar'));
  await tester.pumpAndSettle();
}

// Na lista aberta, toca no + e preenche o formulário com o título e o ano.
Future<void> preencherOFormulario(WidgetTester tester, String titulo, String ano) async {
  await tester.tap(find.byTooltip('Novo livro'));
  await tester.pumpAndSettle();
  await tester.enterText(find.byType(TextFormField).at(0), titulo);
  await tester.enterText(find.byType(TextFormField).at(1), ano);
}

// No detalhe aberto, toca em Excluir e responde ao diálogo com este botão.
Future<void> excluirRespondendo(WidgetTester tester, String resposta) async {
  await tester.tap(find.text('Excluir'));
  await tester.pumpAndSettle();
  await tester.tap(find.descendant(of: find.byType(AlertDialog), matching: find.text(resposta)));
  await tester.pumpAndSettle();
}

// Na lista aberta, digita no campo de busca e aperta o Enter.
Future<void> buscar(WidgetTester tester, String texto) async {
  await tester.enterText(find.byType(TextField).first, texto);
  await tester.testTextInput.receiveAction(TextInputAction.search);
  await tester.pumpAndSettle();
}

// A Ana já entrou (a sessão restaurada, como o main faz) e toca em Ver os livros.
Future<void> abrirOsLivros(WidgetTester tester, http.Client livros) async {
  final sessao = sessaoDeMentira(guardado: {'token': 'token-de-ana@biblioteca.com'});
  await sessao.restaurar();
  await tester.pumpWidget(appDeMentira(sessao, livros: livros));
  await tester.tap(find.text('Ver os livros'));
  await tester.pumpAndSettle();
}

// O que o aparelho de mentira tem guardado como token (ou null).
Future<String?> tokenGuardado() async {
  final prefs = await SharedPreferences.getInstance();
  return prefs.getString('token');
}

// Confere que o cadastro foi recusado, com esta frase para a tela.
Matcher recusadoCom(String frase) {
  return throwsA(isA<ErroDeCadastro>().having((e) => e.mensagem, 'mensagem', frase));
}

void main() {
  testWidgets('a tela de login tem e-mail, senha e o botão Entrar', (tester) async {
    await tester.pumpWidget(appDeMentira(sessaoDeMentira()));

    expect(find.byType(TextField), findsNWidgets(2));
    expect(find.widgetWithText(ElevatedButton, 'Entrar'), findsOneWidget);
    expect(find.text('Criar uma conta'), findsOneWidget);
  });

  testWidgets('a tela de cadastro tem nome, e-mail e senha', (tester) async {
    await tester.pumpWidget(const MaterialApp(home: CadastroScreen()));

    expect(find.byType(TextField), findsNWidgets(3));
    expect(find.widgetWithText(ElevatedButton, 'Cadastrar'), findsOneWidget);
  });

  testWidgets('com a senha certa, a rota /inicio abre a tela inicial', (tester) async {
    await tester.pumpWidget(appDeMentira(sessaoDeMentira()));

    await preencherEEntrar(tester, 'segredo123');

    expect(find.byType(InicioScreen), findsOneWidget);
    expect(find.text('Olá, Ana!'), findsOneWidget);
    expect(find.byType(LoginScreen), findsNothing);
  });

  testWidgets('com a senha errada, fica no login e mostra o erro', (tester) async {
    await tester.pumpWidget(appDeMentira(sessaoDeMentira()));

    await preencherEEntrar(tester, 'senha-errada');

    expect(find.text('E-mail ou senha incorretos'), findsOneWidget);
    expect(find.byType(LoginScreen), findsOneWidget);
  });

  testWidgets('o link Criar uma conta abre o cadastro pelo nome da rota', (tester) async {
    await tester.pumpWidget(appDeMentira(sessaoDeMentira()));

    await tester.tap(find.text('Criar uma conta'));
    await tester.pumpAndSettle();

    expect(find.byType(CadastroScreen), findsOneWidget);
  });

  testWidgets('cadastrar pela tela cria a conta e abre a tela inicial', (tester) async {
    await tester.pumpWidget(appDeMentira(sessaoDeMentira()));

    await preencherECadastrar(tester, 'bia@biblioteca.com', 'segredo456');

    expect(find.byType(InicioScreen), findsOneWidget);
    expect(find.text('Olá, Bia!'), findsOneWidget);
    expect(find.byType(CadastroScreen), findsNothing);
  });

  testWidgets('e-mail repetido: a tela mostra o erro e fica no cadastro', (tester) async {
    await tester.pumpWidget(appDeMentira(sessaoDeMentira()));

    await preencherECadastrar(tester, 'ana@biblioteca.com', 'segredo456');

    expect(find.text('Já existe uma conta com este e-mail'), findsOneWidget);
    expect(find.byType(CadastroScreen), findsOneWidget);
    expect(find.byType(InicioScreen), findsNothing);
  });

  testWidgets('o link Já tenho conta leva ao login', (tester) async {
    await tester.pumpWidget(appDeMentira(sessaoDeMentira()));
    await tester.tap(find.text('Criar uma conta'));
    await tester.pumpAndSettle();

    await tester.tap(find.text('Já tenho conta'));
    await tester.pumpAndSettle();

    expect(find.byType(LoginScreen), findsOneWidget);
    expect(find.byType(CadastroScreen), findsNothing);
  });

  testWidgets('o guarda: sem sessão, a rota /inicio mostra o login', (tester) async {
    await tester.pumpWidget(appDeMentira(sessaoDeMentira()));

    Navigator.of(tester.element(find.byType(LoginScreen))).pushNamed(AppRoutes.inicio);
    await tester.pumpAndSettle();

    expect(find.byType(InicioScreen), findsNothing);
    expect(find.byType(LoginScreen), findsOneWidget);
  });

  testWidgets('o menu mostra o nome sem receber nada pelo construtor', (tester) async {
    await tester.pumpWidget(appDeMentira(sessaoDeMentira()));
    await preencherEEntrar(tester, 'segredo123');

    await abrirOMenu(tester);
    final menu = find.byType(Drawer);
    expect(find.descendant(of: menu, matching: find.text('Ana')), findsOneWidget);
    expect(find.descendant(of: menu, matching: find.text('ana@biblioteca.com')), findsOneWidget);

    await tester.tap(find.descendant(of: menu, matching: find.text('Perfil')));
    await tester.pumpAndSettle();

    expect(find.byType(PerfilScreen), findsOneWidget);
    await abrirOMenu(tester);
    expect(find.descendant(of: find.byType(Drawer), matching: find.text('Ana')), findsOneWidget);
  });

  testWidgets('sair volta ao login, limpa a pilha e apaga a sessão', (tester) async {
    final sessao = sessaoDeMentira();
    await tester.pumpWidget(appDeMentira(sessao));
    await preencherEEntrar(tester, 'segredo123');
    await tester.tap(find.text('Ver os livros'));
    await tester.pumpAndSettle();
    expect(find.byType(LivrosScreen), findsOneWidget);
    expect(await tokenGuardado(), 'token-de-ana@biblioteca.com');

    await abrirOMenu(tester);
    await tester.tap(find.text('Sair'));
    await tester.pumpAndSettle();

    expect(find.byType(LoginScreen), findsOneWidget);
    expect(find.byType(LivrosScreen), findsNothing);
    expect(Navigator.of(tester.element(find.byType(LoginScreen))).canPop(), isFalse);
    expect(sessao.logado, isFalse);
    expect(await tokenGuardado(), isNull);
  });

  testWidgets('com a sessão restaurada, o app abre direto na tela inicial', (tester) async {
    final sessao = sessaoDeMentira(guardado: {'token': 'token-de-ana@biblioteca.com'});
    await sessao.restaurar();

    await tester.pumpWidget(appDeMentira(sessao));

    expect(find.byType(InicioScreen), findsOneWidget);
    expect(find.text('Olá, Ana!'), findsOneWidget);
    expect(find.byType(LoginScreen), findsNothing);
  });

  testWidgets('o watch redesenha a tela quando o service avisa', (tester) async {
    final sessao = sessaoDeMentira();
    await tester.pumpWidget(
      ChangeNotifierProvider.value(
        value: sessao,
        child: MaterialApp(
          home: Builder(
            builder: (context) {
              final nome = context.watch<SessaoService>().usuario?.nome;
              return Text(nome ?? 'ninguém');
            },
          ),
        ),
      ),
    );
    expect(find.text('ninguém'), findsOneWidget);

    await sessao.entrar('ana@biblioteca.com', 'segredo123');
    await tester.pump();

    expect(find.text('Ana'), findsOneWidget);
  });

  // Os quatro estados da tela de livros: a lista, a vazia, o erro e o carregando.
  testWidgets('a tela de livros mostra a lista: um ListTile por livro', (tester) async {
    await abrirOsLivros(tester, apiDeLivros(200, doisLivros));

    expect(find.byType(ListTile), findsNWidgets(2));
    expect(find.text('Dom Casmurro'), findsOneWidget);
    expect(find.text('1938'), findsOneWidget);
  });

  testWidgets('sem livro nenhum, a tela diz que a lista está vazia', (tester) async {
    await abrirOsLivros(tester, apiDeLivros(200, []));

    expect(find.text('Nenhum livro ainda.'), findsOneWidget);
    expect(find.byType(ListTile), findsNothing);
  });

  testWidgets('com a API parada, o erro; o Tentar de novo pede outra vez', (tester) async {
    var noAr = false;
    final livros = MockClient((pedido) async {
      if (!noAr) {
        throw http.ClientException('Failed to fetch');
      }
      return http.Response(jsonEncode(doisLivros), 200);
    });
    await abrirOsLivros(tester, livros);
    expect(find.text('Não consegui carregar os livros'), findsOneWidget);
    expect(find.text('Não consegui falar com a API. O uvicorn está rodando?'), findsOneWidget);

    noAr = true;
    await tester.tap(find.widgetWithText(ElevatedButton, 'Tentar de novo'));
    await tester.pumpAndSettle();

    expect(find.text('Dom Casmurro'), findsOneWidget);
    expect(find.text('Tentar de novo'), findsNothing);
  });

  testWidgets('enquanto a resposta não chega, a tela mostra o carregando', (tester) async {
    final resposta = Completer<http.Response>();
    final sessao = sessaoDeMentira(guardado: {'token': 'token-de-ana@biblioteca.com'});
    await sessao.restaurar();
    await tester.pumpWidget(
      appDeMentira(sessao, livros: MockClient((pedido) => resposta.future)),
    );
    await tester.tap(find.text('Ver os livros'));
    // Sem pumpAndSettle: o círculo gira para sempre, e ele esperaria em vão.
    await tester.pump();
    await tester.pump(const Duration(seconds: 1));

    expect(find.byType(CircularProgressIndicator), findsOneWidget);

    resposta.complete(http.Response(jsonEncode(doisLivros), 200));
    await tester.pumpAndSettle();

    expect(find.byType(CircularProgressIndicator), findsNothing);
    expect(find.text('Dom Casmurro'), findsOneWidget);
  });

  testWidgets('tocar num livro abre o detalhe, que busca o livro na API pelo id', (tester) async {
    await abrirOsLivros(tester, apiDeLivros(200, doisLivros));
    pedidos = 0;

    await tester.tap(find.text('Vidas Secas'));
    await tester.pumpAndSettle();

    expect(find.byType(LivroScreen), findsOneWidget);
    expect(find.text('1938'), findsOneWidget);
    expect(find.text('Emprestado'), findsOneWidget);
    expect(pedidos, 1);
  });

  testWidgets('o detalhe de um livro que não existe mais mostra o erro da API', (tester) async {
    await abrirOsLivros(tester, apiDeLivros(200, doisLivros));

    Navigator.of(tester.element(find.byType(LivrosScreen))).pushNamed(AppRoutes.livro, arguments: 99);
    await tester.pumpAndSettle();

    expect(find.text('Não consegui carregar o livro'), findsOneWidget);
    expect(find.text('Livro 99 nao esta no seu acervo'), findsOneWidget);
    expect(find.text('Tentar de novo'), findsOneWidget);
  });

  testWidgets('sem o livro na rota (o F5 no detalhe), a tela mostra a lista', (tester) async {
    await abrirOsLivros(tester, apiDeLivros(200, doisLivros));

    Navigator.of(tester.element(find.byType(LivrosScreen))).pushNamed(AppRoutes.livro);
    await tester.pumpAndSettle();

    expect(find.byType(LivroScreen), findsOneWidget);
    expect(find.text('Dom Casmurro'), findsOneWidget);
  });

  // O formulário: criar, a validação nas duas pontas, editar e excluir.
  testWidgets('o + abre o formulário vazio, e salvar põe o livro novo na lista', (tester) async {
    await abrirOsLivros(tester, acervoDeMentira());

    await preencherOFormulario(tester, 'O Cortiço', '1890');
    expect(find.text('Novo livro'), findsOneWidget);
    await tester.tap(find.text('Salvar'));
    await tester.pumpAndSettle();

    expect(find.byType(FormularioScreen), findsNothing);
    expect(find.byType(ListTile), findsNWidgets(3));
    expect(find.text('O Cortiço'), findsOneWidget);
  });

  testWidgets('o validator segura o formulário: com campo errado, nada vai para a API', (tester) async {
    await abrirOsLivros(tester, acervoDeMentira());
    await preencherOFormulario(tester, '', '');
    pedidos = 0;

    await tester.tap(find.text('Salvar'));
    await tester.pump();
    expect(find.text('Informe o título'), findsOneWidget);
    expect(find.text('Informe o ano, só com números'), findsOneWidget);

    await tester.enterText(find.byType(TextFormField).at(0), 'O Cortiço');
    await tester.enterText(find.byType(TextFormField).at(1), 'mil oitocentos');
    await tester.tap(find.text('Salvar'));
    await tester.pump();
    expect(find.text('Informe o título'), findsNothing);
    expect(find.text('Informe o ano, só com números'), findsOneWidget);
    expect(pedidos, 0);
    expect(find.byType(FormularioScreen), findsOneWidget);
  });

  testWidgets('título repetido: a API recusa (409), e o formulário mostra a frase e fica aberto', (tester) async {
    await abrirOsLivros(tester, acervoDeMentira());

    await preencherOFormulario(tester, 'Dom Casmurro', '1899');
    await tester.tap(find.text('Salvar'));
    await tester.pumpAndSettle();

    expect(find.text('Ja existe um livro chamado Dom Casmurro'), findsOneWidget);
    expect(find.byType(FormularioScreen), findsOneWidget);
  });

  testWidgets('editar: o formulário vem preenchido, e salvar volta para a lista, já atualizada', (tester) async {
    await abrirOsLivros(tester, acervoDeMentira());
    await tester.tap(find.text('Dom Casmurro'));
    await tester.pumpAndSettle();

    await tester.tap(find.text('Editar'));
    await tester.pumpAndSettle();
    expect(find.text('Editar livro'), findsOneWidget);
    expect(find.widgetWithText(TextFormField, 'Dom Casmurro'), findsOneWidget);
    expect(find.widgetWithText(TextFormField, '1899'), findsOneWidget);

    await tester.enterText(find.byType(TextFormField).at(1), '1900');
    await tester.tap(find.text('Salvar'));
    await tester.pumpAndSettle();

    expect(find.byType(FormularioScreen), findsNothing);
    expect(find.byType(LivroScreen), findsNothing);
    expect(find.text('1900'), findsOneWidget);
    expect(find.text('1899'), findsNothing);
  });

  testWidgets('excluir pergunta antes: Cancelar deixa o livro; Excluir o tira da lista', (tester) async {
    await abrirOsLivros(tester, acervoDeMentira());
    await tester.tap(find.text('Dom Casmurro'));
    await tester.pumpAndSettle();

    await tester.tap(find.text('Excluir'));
    await tester.pumpAndSettle();
    expect(find.text('Excluir Dom Casmurro?'), findsOneWidget);
    await tester.tap(find.text('Cancelar'));
    await tester.pumpAndSettle();
    expect(find.byType(AlertDialog), findsNothing);
    expect(find.byType(LivroScreen), findsOneWidget);

    await excluirRespondendo(tester, 'Excluir');

    expect(find.byType(LivroScreen), findsNothing);
    expect(find.text('Dom Casmurro'), findsNothing);
    expect(find.byType(ListTile), findsOneWidget);
  });

  testWidgets('a API não deixa excluir o livro emprestado (409): o detalhe mostra a frase', (tester) async {
    await abrirOsLivros(tester, acervoDeMentira());
    await tester.tap(find.text('Vidas Secas'));
    await tester.pumpAndSettle();

    await excluirRespondendo(tester, 'Excluir');

    expect(find.text('Livro 2 esta emprestado'), findsOneWidget);
    expect(find.byType(LivroScreen), findsOneWidget);
  });

  // A busca e os avisos.
  testWidgets('a busca pede à API só os livros com o texto no título', (tester) async {
    await abrirOsLivros(tester, acervoDeMentira());

    await buscar(tester, 'casm');

    expect(ultimoEndereco!.queryParameters['titulo'], 'casm');
    expect(find.text('Dom Casmurro'), findsOneWidget);
    expect(find.text('Vidas Secas'), findsNothing);
    expect(find.byType(ListTile), findsOneWidget);
  });

  testWidgets('a busca sem resultado diz o que foi procurado', (tester) async {
    await abrirOsLivros(tester, acervoDeMentira());

    await buscar(tester, 'xyz');

    expect(find.text('Nenhum livro com "xyz" no título.'), findsOneWidget);
    expect(find.byType(ListTile), findsNothing);
  });

  testWidgets('a busca vazia volta a lista inteira, sem o ?titulo=', (tester) async {
    await abrirOsLivros(tester, acervoDeMentira());
    await buscar(tester, 'casm');

    await buscar(tester, '');

    expect(ultimoEndereco!.hasQuery, isFalse);
    expect(find.byType(ListTile), findsNWidgets(2));
  });

  testWidgets('depois de salvar, a lista pede de novo com a mesma busca', (tester) async {
    await abrirOsLivros(tester, acervoDeMentira());
    await buscar(tester, 'casm');

    await preencherOFormulario(tester, 'Casmurro de Novo', '1900');
    await tester.tap(find.text('Salvar'));
    await tester.pumpAndSettle();

    expect(find.byType(ListTile), findsNWidgets(2));
    expect(find.text('Vidas Secas'), findsNothing);
  });

  // O filtro dos disponíveis e o x que limpa a busca.
  testWidgets('o filtro Só os disponíveis pede à API o ?disponivel=true', (tester) async {
    await abrirOsLivros(tester, acervoDeMentira());

    await tester.tap(find.text('Só os disponíveis'));
    await tester.pumpAndSettle();

    expect(ultimoEndereco!.queryParameters['disponivel'], 'true');
    expect(find.text('Dom Casmurro'), findsOneWidget);
    expect(find.text('Vidas Secas'), findsNothing);
  });

  testWidgets('desligar o filtro volta a lista inteira', (tester) async {
    await abrirOsLivros(tester, acervoDeMentira());
    await tester.tap(find.text('Só os disponíveis'));
    await tester.pumpAndSettle();

    await tester.tap(find.text('Só os disponíveis'));
    await tester.pumpAndSettle();

    expect(ultimoEndereco!.hasQuery, isFalse);
    expect(find.byType(ListTile), findsNWidgets(2));
  });

  testWidgets('a busca e o filtro vão juntos: ?titulo=...&disponivel=true', (tester) async {
    await abrirOsLivros(tester, acervoDeMentira());
    await buscar(tester, 'secas');

    await tester.tap(find.text('Só os disponíveis'));
    await tester.pumpAndSettle();

    expect(ultimoEndereco!.queryParameters, {'titulo': 'secas', 'disponivel': 'true'});
    expect(find.text('Nenhum livro com "secas" no título.'), findsOneWidget);
  });

  testWidgets('o x apaga a busca e volta a lista inteira', (tester) async {
    await abrirOsLivros(tester, acervoDeMentira());
    await buscar(tester, 'casm');

    await tester.tap(find.byTooltip('Limpar a busca'));
    await tester.pumpAndSettle();

    expect(ultimoEndereco!.hasQuery, isFalse);
    expect(find.byType(ListTile), findsNWidgets(2));
    expect(find.text('casm'), findsNothing);
  });

  testWidgets('salvar mostra o aviso verde: Livro salvo, já na lista', (tester) async {
    await abrirOsLivros(tester, acervoDeMentira());

    await preencherOFormulario(tester, 'O Cortiço', '1890');
    await tester.tap(find.text('Salvar'));
    await tester.pumpAndSettle();

    expect(find.byType(FormularioScreen), findsNothing);
    expect(find.widgetWithText(SnackBar, 'Livro salvo'), findsOneWidget);
  });

  testWidgets('a recusa da API mostra o aviso vermelho, e a frase fica no formulário', (tester) async {
    await abrirOsLivros(tester, acervoDeMentira());

    await preencherOFormulario(tester, 'Dom Casmurro', '1899');
    await tester.tap(find.text('Salvar'));
    await tester.pumpAndSettle();

    expect(find.widgetWithText(SnackBar, 'Não deu para salvar'), findsOneWidget);
    expect(find.text('Ja existe um livro chamado Dom Casmurro'), findsOneWidget);
    expect(find.byType(FormularioScreen), findsOneWidget);
  });

  testWidgets('excluir mostra o aviso: Livro excluído; o emprestado, Não deu para excluir', (tester) async {
    await abrirOsLivros(tester, acervoDeMentira());
    await tester.tap(find.text('Dom Casmurro'));
    await tester.pumpAndSettle();
    await excluirRespondendo(tester, 'Excluir');
    expect(find.widgetWithText(SnackBar, 'Livro excluído'), findsOneWidget);

    await tester.tap(find.text('Vidas Secas'));
    await tester.pumpAndSettle();
    await excluirRespondendo(tester, 'Excluir');
    expect(find.widgetWithText(SnackBar, 'Não deu para excluir'), findsOneWidget);
    expect(find.text('Livro 2 esta emprestado'), findsOneWidget);
  });

  testWidgets('depois de um F5 no formulário (a primeira tela da pilha), ele mostra a lista', (tester) async {
    await abrirOsLivros(tester, acervoDeMentira());

    Navigator.of(tester.element(find.byType(LivrosScreen))).pushNamedAndRemoveUntil(
      AppRoutes.formulario,
      (rota) => false,
    );
    await tester.pumpAndSettle();

    expect(find.byType(FormularioScreen), findsOneWidget);
    expect(find.text('Novo livro'), findsNothing);
    expect(find.text('Dom Casmurro'), findsOneWidget);
  });

  // O service testado sozinho, sem tela nenhuma: é o que as camadas compram.
  test('o service recusa campos vazios sem nem chamar a API', () async {
    final sessao = sessaoDeMentira();
    pedidos = 0;

    await expectLater(sessao.entrar('', ''), throwsA(isA<ErroDeLogin>()));
    await expectLater(sessao.cadastrar('', '', ''), recusadoCom('Preencha o nome, o e-mail e a senha'));
    expect(pedidos, 0);
    expect(sessao.logado, isFalse);
  });

  test('entrar e sair mudam a sessão e avisam quem está de olho', () async {
    final sessao = sessaoDeMentira();
    var avisos = 0;
    sessao.addListener(() => avisos++);

    await sessao.entrar('ana@biblioteca.com', 'segredo123');
    expect(sessao.token, 'token-de-ana@biblioteca.com');
    expect(sessao.usuario?.nome, 'Ana');
    expect(avisos, 1);

    await sessao.sair();
    expect(sessao.logado, isFalse);
    expect(sessao.usuario, isNull);
    expect(avisos, 2);
  });

  test('cadastrar cria a conta e já entra com ela, pelo mesmo caminho do login', () async {
    final sessao = sessaoDeMentira();

    await sessao.cadastrar('Bia', 'bia@biblioteca.com', 'segredo456');

    expect(sessao.logado, isTrue);
    expect(sessao.usuario?.nome, 'Bia');
    expect(sessao.token, 'token-de-bia@biblioteca.com');
  });

  test('o service traduz a recusa da API: e-mail repetido (409) e campo inválido (422)', () async {
    final sessao = sessaoDeMentira();

    await expectLater(
      sessao.cadastrar('Ana', 'ana@biblioteca.com', 'segredo123'),
      recusadoCom('Já existe uma conta com este e-mail'),
    );
    await expectLater(
      sessao.cadastrar('Bia', 'bia@biblioteca.com', '123'),
      recusadoCom('senha: String should have at least 6 characters'),
    );
    expect(sessao.logado, isFalse);
    expect(await tokenGuardado(), isNull);
  });

  test('entrar guarda o token no aparelho', () async {
    final sessao = sessaoDeMentira();

    await sessao.entrar('ana@biblioteca.com', 'segredo123');

    expect(await tokenGuardado(), 'token-de-ana@biblioteca.com');
  });

  test('restaurar devolve a sessão a quem tem um token guardado', () async {
    final sessao = sessaoDeMentira(guardado: {'token': 'token-de-ana@biblioteca.com'});
    pedidos = 0;

    await sessao.restaurar();

    expect(sessao.logado, isTrue);
    expect(sessao.usuario?.nome, 'Ana');
    expect(pedidos, 1);
  });

  test('restaurar sem token guardado não pede nada à API', () async {
    final sessao = sessaoDeMentira();
    pedidos = 0;

    await sessao.restaurar();

    expect(sessao.logado, isFalse);
    expect(pedidos, 0);
  });

  test('restaurar apaga o token que a API não aceita mais', () async {
    final sessao = sessaoDeMentira(guardado: {'token': 'token-vencido'});

    await sessao.restaurar();

    expect(sessao.logado, isFalse);
    expect(await tokenGuardado(), isNull);
  });

  test('sair apaga o token guardado no aparelho', () async {
    final sessao = sessaoDeMentira(guardado: {'token': 'token-de-ana@biblioteca.com'});
    await sessao.restaurar();
    expect(sessao.logado, isTrue);

    await sessao.sair();

    expect(await tokenGuardado(), isNull);
  });

  test('o repositório manda o token no cabeçalho e devolve objetos Livro', () async {
    String? cabecalho;
    final cliente = MockClient((pedido) async {
      cabecalho = pedido.headers['Authorization'];
      return http.Response(jsonEncode(doisLivros), 200);
    });

    final livros = await LivroRepository(cliente: cliente).listar('tk-123');

    expect(cabecalho, 'Bearer tk-123');
    expect(livros, hasLength(2));
    expect(livros.first, isA<Livro>());
    expect(livros.first.titulo, 'Dom Casmurro');
    expect(livros.last.disponivel, isFalse);
  });

  test('o repositório busca um livro só pelo id, com o token: GET /livros/2', () async {
    String? caminho;
    String? cabecalho;
    final cliente = MockClient((pedido) async {
      caminho = pedido.url.path;
      cabecalho = pedido.headers['Authorization'];
      return http.Response(jsonEncode(doisLivros.last), 200);
    });

    final livro = await LivroRepository(cliente: cliente).buscar('tk-123', 2);

    expect(caminho, '/livros/2');
    expect(cabecalho, 'Bearer tk-123');
    expect(livro.titulo, 'Vidas Secas');
  });

  test('o repositório cria com POST: o livro em JSON no corpo, e o token no cabeçalho', () async {
    late http.Request enviado;
    final cliente = MockClient((pedido) async {
      enviado = pedido;
      return http.Response(
        jsonEncode({'id': 3, 'titulo': 'O Cortiço', 'ano': 1890, 'disponivel': true, 'dono_id': 1}),
        201,
      );
    });

    final livro = await LivroRepository(cliente: cliente).criar('tk-123', 'O Cortiço', 1890);

    expect(enviado.method, 'POST');
    expect(enviado.url.path, '/livros/');
    expect(enviado.headers['Authorization'], 'Bearer tk-123');
    expect(enviado.headers['Content-Type'], startsWith('application/json'));
    expect(jsonDecode(enviado.body), {'titulo': 'O Cortiço', 'ano': 1890});
    expect(livro.id, 3);
  });

  test('o repositório edita com PATCH e exclui com DELETE, no endereço do livro', () async {
    final feitos = <String>[];
    final cliente = MockClient((pedido) async {
      feitos.add('${pedido.method} ${pedido.url.path}');
      if (pedido.method == 'DELETE') {
        return http.Response('', 204);
      }
      return http.Response(jsonEncode(doisLivros.first), 200);
    });
    final repositorio = LivroRepository(cliente: cliente);

    await repositorio.atualizar('tk-123', 1, 'Dom Casmurro', 1900);
    await repositorio.excluir('tk-123', 1);

    expect(feitos, ['PATCH /livros/1', 'DELETE /livros/1']);
  });

  test('o 422 da API vira a frase da tela: o campo e a mensagem, sem o Value error', () async {
    final sessao = sessaoDeMentira();
    await sessao.entrar('ana@biblioteca.com', 'segredo123');
    final recusa = MockClient((pedido) async {
      return http.Response(
        jsonEncode({
          'detail': [
            {
              'type': 'value_error',
              'loc': ['body', 'ano'],
              'msg': 'Value error, o ano precisa estar entre 1450 e 2100',
            },
          ],
        }),
        422,
      );
    });
    final servico = LivroService(LivroRepository(cliente: recusa), sessao);

    await expectLater(
      servico.criar('O Cortiço', 1200),
      throwsA(isA<ErroDeLivros>().having((e) => '$e', 'texto', 'ano: o ano precisa estar entre 1450 e 2100')),
    );
  });

  test('o service dos livros traduz a recusa: a frase da API vai para a tela', () async {
    final sessao = sessaoDeMentira();
    await sessao.entrar('ana@biblioteca.com', 'segredo123');
    final recusa = apiDeLivros(401, {'detail': 'Token invalido ou vencido'});
    final servico = LivroService(LivroRepository(cliente: recusa), sessao);

    await expectLater(
      servico.listar(),
      throwsA(isA<ErroDeLivros>().having((e) => '$e', 'texto', 'Token invalido ou vencido')),
    );
  });
}
