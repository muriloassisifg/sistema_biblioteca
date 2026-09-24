import 'package:flutter/material.dart';

import 'repositorios/usuario_repositorio.dart';
import 'servicos/sessao_service.dart';
import 'telas/login_tela.dart';

// Aqui as camadas se montam, como no dependencias.py do backend:
// o repositório entra no service, e o service entra nas telas.
void main() {
  final sessao = SessaoService(UsuarioRepositorio());
  runApp(BibliotecaApp(sessao: sessao));
}

class BibliotecaApp extends StatelessWidget {
  const BibliotecaApp({super.key, required this.sessao});

  final SessaoService sessao;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Biblioteca',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(colorSchemeSeed: Colors.indigo),
      home: LoginTela(sessao: sessao),
    );
  }
}
