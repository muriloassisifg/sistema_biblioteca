import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/telas/cadastro_tela.dart';
import 'package:frontend/telas/login_tela.dart';

void main() {
  testWidgets('a tela de login tem e-mail, senha e o botão Entrar', (tester) async {
    await tester.pumpWidget(const MaterialApp(home: LoginTela()));

    expect(find.byType(TextField), findsNWidgets(2));
    expect(find.widgetWithText(ElevatedButton, 'Entrar'), findsOneWidget);
    expect(find.text('Criar uma conta'), findsOneWidget);
  });

  testWidgets('a tela de cadastro tem nome, e-mail e senha', (tester) async {
    await tester.pumpWidget(const MaterialApp(home: CadastroTela()));

    expect(find.byType(TextField), findsNWidgets(3));
    expect(find.widgetWithText(ElevatedButton, 'Cadastrar'), findsOneWidget);
  });
}
