import 'package:flutter/material.dart';

import '../models/usuario.dart';
import '../services/sessao_service.dart';
import 'login_screen.dart';

// A tela inicial: pede ao service quem está logado. O token mora na sessão.
class InicioScreen extends StatefulWidget {
  const InicioScreen({super.key, required this.sessao});

  final SessaoService sessao;

  @override
  State<InicioScreen> createState() => _InicioScreenState();
}

class _InicioScreenState extends State<InicioScreen> {
  Usuario? usuario;

  @override
  void initState() {
    super.initState();
    carregar();
  }

  Future<void> carregar() async {
    final quem = await widget.sessao.usuarioLogado();
    if (!mounted) return;
    setState(() {
      usuario = quem;
    });
  }

  void sair() {
    widget.sessao.sair();
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (context) => LoginScreen(sessao: widget.sessao)),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Biblioteca'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            tooltip: 'Sair',
            onPressed: sair,
          ),
        ],
      ),
      body: Center(
        child: usuario == null
            ? const CircularProgressIndicator()
            : Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(Icons.waving_hand, size: 56),
                  const SizedBox(height: 16),
                  Text(
                    'Olá, ${usuario!.nome}!',
                    style: const TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(usuario!.email),
                  const SizedBox(height: 24),
                  const Text('A API reconheceu o seu token.'),
                ],
              ),
      ),
    );
  }
}
