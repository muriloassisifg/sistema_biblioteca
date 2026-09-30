import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../services/sessao_service.dart';
import '../widgets/app_drawer.dart';

// O perfil: o nome e o e-mail de quem está na sessão.
class PerfilScreen extends StatelessWidget {
  const PerfilScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final usuario = context.watch<SessaoService>().usuario!;
    return Scaffold(
      appBar: AppBar(title: const Text('Perfil')),
      drawer: const AppDrawer(),
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.account_circle, size: 72),
            const SizedBox(height: 16),
            Text(
              usuario.nome,
              style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(usuario.email),
          ],
        ),
      ),
    );
  }
}
