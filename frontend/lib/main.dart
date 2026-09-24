import 'package:flutter/material.dart';

import 'api.dart';
import 'telas/login_tela.dart';

void main() {
  runApp(const BibliotecaApp());
}

class BibliotecaApp extends StatelessWidget {
  const BibliotecaApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Biblioteca',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(colorSchemeSeed: Colors.indigo),
      home: LoginTela(api: Api()),
    );
  }
}
