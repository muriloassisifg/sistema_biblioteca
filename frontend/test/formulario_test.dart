import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/screens/formulario_screen.dart';

// O formulário precisa de uma tela embaixo dele: sozinho na pilha, ele mostra a
// lista (é o caso do F5). Esta tela de baixo é só do teste.
Future<void> abrirOFormulario(WidgetTester tester) async {
  await tester.pumpWidget(const MaterialApp(home: Scaffold()));
  Navigator.of(tester.element(find.byType(Scaffold))).push(
    MaterialPageRoute(builder: (_) => const FormularioScreen()),
  );
  await tester.pumpAndSettle();
}

void main() {
  testWidgets('o formulário vazio mostra as duas frases', (tester) async {
    await abrirOFormulario(tester);

    await tester.tap(find.text('Salvar'));
    await tester.pump();

    expect(find.text('Informe o título'), findsOneWidget);
    expect(find.text('Informe o ano, só com números'), findsOneWidget);
  });

  testWidgets('com o título preenchido, só o ano continua recusado', (tester) async {
    await abrirOFormulario(tester);

    await tester.enterText(find.byType(TextFormField).at(0), 'O Cortiço');
    await tester.enterText(find.byType(TextFormField).at(1), 'mil oitocentos');
    await tester.tap(find.text('Salvar'));
    await tester.pump();

    expect(find.text('Informe o título'), findsNothing);
    expect(find.text('Informe o ano, só com números'), findsOneWidget);
  });
}
