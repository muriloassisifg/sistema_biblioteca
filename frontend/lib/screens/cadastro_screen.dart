import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../routes.dart';
import '../services/sessao_service.dart';

// A tela de cadastro, pelo mesmo caminho da de login: recebe o clique, pede
// ao service e mostra a resposta. O erro que a API mandou aparece em vermelho.
class CadastroScreen extends StatefulWidget {
  const CadastroScreen({super.key});

  @override
  State<CadastroScreen> createState() => _CadastroScreenState();
}

class _CadastroScreenState extends State<CadastroScreen> {
  final nome = TextEditingController();
  final email = TextEditingController();
  final senha = TextEditingController();
  bool carregando = false;
  String? erro;

  Future<void> cadastrar() async {
    setState(() {
      carregando = true;
      erro = null;
    });
    try {
      await context.read<SessaoService>().cadastrar(
        nome.text,
        email.text,
        senha.text,
      );
    } on ErroDeCadastro catch (e) {
      setState(() {
        carregando = false;
        erro = e.mensagem;
      });
      return;
    }
    if (!mounted) return;
    Navigator.pushNamedAndRemoveUntil(
      context,
      AppRoutes.inicio,
      (rota) => false,
    );
  }

  @override
  void dispose() {
    nome.dispose();
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
                const Text(
                  'Criar conta',
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 24),
                TextField(
                  controller: nome,
                  decoration: const InputDecoration(
                    labelText: 'Nome',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 16),
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
                    helperText: 'Pelo menos 6 caracteres',
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
                  onPressed: carregando ? null : cadastrar,
                  child: Text(carregando ? 'Cadastrando...' : 'Cadastrar'),
                ),
                const SizedBox(height: 8),
                TextButton(
                  onPressed: () {
                    Navigator.pushNamedAndRemoveUntil(
                      context,
                      AppRoutes.login,
                      (rota) => false,
                    );
                  },
                  child: const Text('Já tenho conta'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
