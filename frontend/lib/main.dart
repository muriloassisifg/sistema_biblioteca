import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'repositories/usuario_repository.dart';
import 'routes.dart';
import 'screens/cadastro_screen.dart';
import 'screens/inicio_screen.dart';
import 'screens/livros_screen.dart';
import 'screens/login_screen.dart';
import 'screens/perfil_screen.dart';
import 'services/sessao_service.dart';
import 'widgets/rota_protegida.dart';

// Aqui as camadas se montam, como o main.py monta a API no backend: o
// repositório entra no service, e o service fica no topo do app, onde toda
// tela o alcança, sem passar de construtor em construtor.
void main() {
  runApp(
    ChangeNotifierProvider(
      create: (context) => SessaoService(UsuarioRepository()),
      child: const BibliotecaApp(),
    ),
  );
}

class BibliotecaApp extends StatelessWidget {
  const BibliotecaApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Biblioteca',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(colorSchemeSeed: Colors.indigo),
      initialRoute: AppRoutes.login,
      routes: {
        AppRoutes.login: (context) => const LoginScreen(),
        AppRoutes.cadastro: (context) => const CadastroScreen(),
        AppRoutes.inicio: (context) => const RotaProtegida(tela: InicioScreen()),
        AppRoutes.livros: (context) => const RotaProtegida(tela: LivrosScreen()),
        AppRoutes.perfil: (context) => const RotaProtegida(tela: PerfilScreen()),
      },
    );
  }
}
