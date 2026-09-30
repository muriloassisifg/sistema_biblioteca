import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../screens/login_screen.dart';
import '../services/sessao_service.dart';

// O guarda de uma rota: com sessão, mostra a tela; sem sessão, mostra o login.
// O watch faz o guarda conferir de novo sempre que a sessão mudar.
class RotaProtegida extends StatelessWidget {
  const RotaProtegida({super.key, required this.tela});

  final Widget tela;

  @override
  Widget build(BuildContext context) {
    final logado = context.watch<SessaoService>().logado;
    return logado ? tela : const LoginScreen();
  }
}
