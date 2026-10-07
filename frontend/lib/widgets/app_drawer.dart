import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../routes.dart';
import '../services/sessao_service.dart';

// O menu lateral, igual em toda tela protegida. Ele não recebe nada pelo
// construtor: pergunta à sessão quem está logado, onde quer que esteja.
class AppDrawer extends StatelessWidget {
  const AppDrawer({super.key});

  @override
  Widget build(BuildContext context) {
    // O guarda só abre as telas com sessão, então o usuário nunca é null aqui.
    final usuario = context.watch<SessaoService>().usuario!;
    return Drawer(
      child: ListView(
        children: [
          UserAccountsDrawerHeader(
            accountName: Text(usuario.nome),
            accountEmail: Text(usuario.email),
          ),
          ListTile(
            leading: const Icon(Icons.home),
            title: const Text('Início'),
            onTap: () => Navigator.pushReplacementNamed(context, AppRoutes.inicio),
          ),
          ListTile(
            leading: const Icon(Icons.menu_book),
            title: const Text('Livros'),
            onTap: () => Navigator.pushReplacementNamed(context, AppRoutes.livros),
          ),
          ListTile(
            leading: const Icon(Icons.person),
            title: const Text('Perfil'),
            onTap: () => Navigator.pushReplacementNamed(context, AppRoutes.perfil),
          ),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.logout),
            title: const Text('Sair'),
            onTap: () async {
              await context.read<SessaoService>().sair();
              if (!context.mounted) return;
              Navigator.pushNamedAndRemoveUntil(
                context,
                AppRoutes.login,
                (rota) => false,
              );
            },
          ),
        ],
      ),
    );
  }
}
