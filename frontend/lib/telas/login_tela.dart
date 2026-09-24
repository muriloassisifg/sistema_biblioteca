import 'package:flutter/material.dart';

class LoginTela extends StatelessWidget {
  const LoginTela({super.key});

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
                const TextField(
                  decoration: InputDecoration(
                    labelText: 'E-mail',
                    border: OutlineInputBorder(),
                  ),
                  keyboardType: TextInputType.emailAddress,
                ),
                const SizedBox(height: 16),
                const TextField(
                  decoration: InputDecoration(
                    labelText: 'Senha',
                    border: OutlineInputBorder(),
                  ),
                  obscureText: true,
                ),
                const SizedBox(height: 24),
                ElevatedButton(
                  onPressed: () {},
                  child: const Text('Entrar'),
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
                        onPressed: () {},
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
