import 'package:flutter/material.dart';

import '../api.dart';
import 'cadastro_tela.dart';
import 'inicio_tela.dart';

class LoginTela extends StatefulWidget {
  const LoginTela({super.key, required this.api});

  final Api api;

  @override
  State<LoginTela> createState() => _LoginTelaState();
}

class _LoginTelaState extends State<LoginTela> {
  final email = TextEditingController();
  final senha = TextEditingController();
  bool carregando = false;
  String? erro;

  Future<void> entrar() async {
    setState(() {
      carregando = true;
      erro = null;
    });
    String? token;
    try {
      token = await widget.api.entrar(email.text, senha.text);
    } catch (e) {
      setState(() {
        carregando = false;
        erro = 'Não consegui falar com a API. O uvicorn está rodando?';
      });
      return;
    }
    if (!mounted) return;
    if (token == null) {
      setState(() {
        carregando = false;
        erro = 'E-mail ou senha incorretos';
      });
      return;
    }
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(
        builder: (context) => InicioTela(api: widget.api, token: token!),
      ),
    );
  }

  @override
  void dispose() {
    email.dispose();
    senha.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Biblioteca')),
      body: Center(
        child: SingleChildScrollView(
          child: Container(
            constraints: const BoxConstraints(maxWidth: 400),
            padding: const EdgeInsets.all(24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const Icon(Icons.local_library, size: 72),
                const SizedBox(height: 8),
                const Text(
                  'Entrar',
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 24),
                TextField(
                  controller: email,
                  decoration: const InputDecoration(
                    labelText: 'E-mail',
                    border: OutlineInputBorder(),
                  ),
                  keyboardType: TextInputType.emailAddress,
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: senha,
                  decoration: const InputDecoration(
                    labelText: 'Senha',
                    border: OutlineInputBorder(),
                  ),
                  obscureText: true,
                ),
                if (erro != null) ...[
                  const SizedBox(height: 16),
                  Text(
                    erro!,
                    textAlign: TextAlign.center,
                    style: const TextStyle(color: Colors.red),
                  ),
                ],
                const SizedBox(height: 24),
                ElevatedButton(
                  onPressed: carregando ? null : entrar,
                  child: Text(carregando ? 'Entrando...' : 'Entrar'),
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Expanded(
                      child: TextButton(
                        onPressed: () {},
                        child: const Text('Esqueci a senha'),
                      ),
                    ),
                    Expanded(
                      child: TextButton(
                        onPressed: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) => const CadastroTela(),
                            ),
                          );
                        },
                        child: const Text('Criar uma conta'),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
