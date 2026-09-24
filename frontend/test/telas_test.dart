import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

import 'package:frontend/api.dart';
import 'package:frontend/telas/cadastro_tela.dart';
import 'package:frontend/telas/login_tela.dart';

// Uma API de mentira: responde como a de verdade, sem precisar do uvicorn.
// A senha certa é 'segredo123', e o token que ela devolve é 'token-da-ana'.
Api apiDeMentira() {
  return Api(
    cliente: MockClient((pedido) async {
      if (pedido.url.path == '/usuarios/login') {
        if (pedido.bodyFields['password'] == 'segredo123') {
          return http.Response(
            jsonEncode({'access_token': 'token-da-ana', 'token_type': 'bearer'}),
            200,
          );
        }
        return http.Response('{"detail": "E-mail ou senha incorretos"}', 401);
      }
      if (pedido.url.path == '/usuarios/eu' &&
          pedido.headers['Authorization'] == 'Bearer token-da-ana') {
        return http.Response(
          jsonEncode({'id': 1, 'nome': 'Ana', 'email': 'ana@biblioteca.com'}),
          200,
        );
      }
      return http.Response('{"detail": "Not authenticated"}', 401);
    }),
  );
}

Future<void> preencherEEntrar(WidgetTester tester, String senha) async {
  await tester.enterText(find.byType(TextField).at(0), 'ana@biblioteca.com');
  await tester.enterText(find.byType(TextField).at(1), senha);
  await tester.tap(find.widgetWithText(ElevatedButton, 'Entrar'));
  await tester.pumpAndSettle();
}

void main() {
  testWidgets('a tela de login tem e-mail, senha e o botão Entrar', (tester) async {
    await tester.pumpWidget(MaterialApp(home: LoginTela(api: apiDeMentira())));

    expect(find.byType(TextField), findsNWidgets(2));
    expect(find.widgetWithText(ElevatedButton, 'Entrar'), findsOneWidget);
    expect(find.text('Criar uma conta'), findsOneWidget);
  });

  testWidgets('a tela de cadastro tem nome, e-mail e senha', (tester) async {
    await tester.pumpWidget(const MaterialApp(home: CadastroTela()));

    expect(find.byType(TextField), findsNWidgets(3));
    expect(find.widgetWithText(ElevatedButton, 'Cadastrar'), findsOneWidget);
  });

  testWidgets('com a senha certa, abre a tela inicial e a API reconhece o token', (tester) async {
    await tester.pumpWidget(MaterialApp(home: LoginTela(api: apiDeMentira())));

    await preencherEEntrar(tester, 'segredo123');

    expect(find.text('Olá, Ana!'), findsOneWidget);
    expect(find.text('ana@biblioteca.com'), findsOneWidget);
    expect(find.byType(LoginTela), findsNothing);
  });

  testWidgets('com a senha errada, fica no login e mostra o erro', (tester) async {
    await tester.pumpWidget(MaterialApp(home: LoginTela(api: apiDeMentira())));

    await preencherEEntrar(tester, 'senha-errada');

    expect(find.text('E-mail ou senha incorretos'), findsOneWidget);
    expect(find.byType(LoginTela), findsOneWidget);
  });

  testWidgets('o link Criar uma conta abre o cadastro', (tester) async {
    await tester.pumpWidget(MaterialApp(home: LoginTela(api: apiDeMentira())));

    await tester.tap(find.text('Criar uma conta'));
    await tester.pumpAndSettle();

    expect(find.byType(CadastroTela), findsOneWidget);
  });
}
