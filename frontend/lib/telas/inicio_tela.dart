import 'package:flutter/material.dart';

import '../api.dart';
import 'login_tela.dart';

class InicioTela extends StatefulWidget {
  const InicioTela({super.key, required this.api, required this.token});

  final Api api;
  final String token;

  @override
  State<InicioTela> createState() => _InicioTelaState();
}

class _InicioTelaState extends State<InicioTela> {
  String? nome;
  String? email;

  @override
  void initState() {
    super.initState();
    carregar();
  }

  Future<void> carregar() async {
    final eu = await widget.api.quemSouEu(widget.token);
    if (!mounted) return;
    setState(() {
      nome = eu['nome'];
      email = eu['email'];
    });
  }

  void sair() {
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (context) => LoginTela(api: widget.api)),
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
        child: nome == null
            ? const CircularProgressIndicator()
            : Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(Icons.waving_hand, size: 56),
                  const SizedBox(height: 16),
                  Text(
                    'Olá, $nome!',
                    style: const TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text('$email'),
                  const SizedBox(height: 24),
                  const Text('A API reconheceu o seu token.'),
                ],
              ),
      ),
    );
  }
}
