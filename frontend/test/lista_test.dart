import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:provider/provider.dart';

import 'package:frontend/repositories/livro_repository.dart';
import 'package:frontend/repositories/usuario_repository.dart';
import 'package:frontend/screens/livros_screen.dart';
import 'package:frontend/services/livro_service.dart';
import 'package:frontend/services/sessao_service.dart';

// A lista pede os livros à API. Aqui, quem responde é uma API de mentira: para
// qualquer pedido, ela devolve o texto que o teste escolheu.
Future<void> abrirALista(WidgetTester tester, String respostaDaApi) async {
  final api = MockClient((pedido) async => http.Response(respostaDaApi, 200));
  final sessao = SessaoService(UsuarioRepository());
  sessao.token = 'um-token';
  final livros = LivroService(LivroRepository(cliente: api), sessao);

  await tester.pumpWidget(
    Provider.value(
      value: livros,
      child: const MaterialApp(home: LivrosScreen()),
    ),
  );
  await tester.pumpAndSettle();
}

void main() {
  testWidgets('a lista mostra o livro que a API devolveu', (tester) async {
    await abrirALista(
      tester,
      '[{"id": 1, "titulo": "Dom Casmurro", "ano": 1899, "disponivel": true}]',
    );

    expect(find.text('Dom Casmurro'), findsOneWidget);
    expect(find.text('Nenhum livro ainda.'), findsNothing);
  });

  testWidgets('sem livro nenhum, a lista avisa que está vazia', (tester) async {
    await abrirALista(tester, '[]');

    expect(find.text('Nenhum livro ainda.'), findsOneWidget);
  });
}
