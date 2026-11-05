import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../models/livro.dart';
import '../services/livro_service.dart';
import '../widgets/aviso.dart';
import 'livros_screen.dart';

// Uma tela só para criar e para editar: sem livro, cria; com o livro, edita.
// Os campos e as regras são os mesmos; muda o título da barra, o que vem
// preenchido e o pedido que sai (POST para criar, PATCH para editar).
class FormularioScreen extends StatefulWidget {
  const FormularioScreen({super.key, this.livro});

  // O livro a editar, que veio nos arguments; null é um livro novo.
  final Livro? livro;

  @override
  State<FormularioScreen> createState() => _FormularioScreenState();
}

class _FormularioScreenState extends State<FormularioScreen> {
  // A chave do Form: é por ela que o Salvar alcança o formulário e confere
  // todos os campos de uma vez.
  final chave = GlobalKey<FormState>();
  final titulo = TextEditingController();
  final ano = TextEditingController();
  bool salvando = false;
  String? erro;

  @override
  void initState() {
    super.initState();
    // Editando: os campos já começam com o que o livro tem.
    if (widget.livro != null) {
      titulo.text = widget.livro!.titulo;
      ano.text = '${widget.livro!.ano}';
    }
  }

  Future<void> salvar() async {
    // A ponta do app: cada validator confere o seu campo. Se algum devolver
    // uma frase, ela aparece embaixo do campo, e nada vai para a API.
    if (!chave.currentState!.validate()) {
      return;
    }
    setState(() {
      salvando = true;
      erro = null;
    });
    // A ponta da API: ela confere tudo de novo, e pode recusar (422, 409).
    // O servico é o LivroService, pego uma vez para as duas chamadas abaixo.
    final servico = context.read<LivroService>();
    try {
      if (widget.livro == null) {
        await servico.criar(titulo.text, int.parse(ano.text));
      } else {
        await servico.atualizar(widget.livro!.id, titulo.text, int.parse(ano.text));
      }
    } on ErroDeLivros catch (e) {
      if (!mounted) return;
      setState(() {
        salvando = false;
        erro = '$e';
      });
      // A frase da API fica no formulário; o aviso diz que não deu.
      avisar(context, 'Não deu para salvar', erro: true);
      return;
    }
    if (!mounted) return;
    // Deu certo: o aviso verde, e o formulário fecha com true; quem o abriu
    // pede de novo. O aviso continua na tela da lista.
    avisar(context, 'Livro salvo');
    Navigator.pop(context, true);
  }

  @override
  void dispose() {
    titulo.dispose();
    ano.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    // Depois de um F5, o formulário é a primeira tela da pilha: ninguém o
    // abriu, e não há quem receba o true. Aí, ele mostra a lista, como o detalhe.
    if (ModalRoute.of(context)!.isFirst) {
      return const LivrosScreen();
    }
    final editando = widget.livro != null;
    return Scaffold(
      appBar: AppBar(title: Text(editando ? 'Editar livro' : 'Novo livro')),
      body: Center(
        child: SingleChildScrollView(
          child: Container(
            constraints: const BoxConstraints(maxWidth: 400),
            padding: const EdgeInsets.all(24),
            child: Form(
              key: chave,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  TextFormField(
                    controller: titulo,
                    decoration: const InputDecoration(
                      labelText: 'Título',
                      border: OutlineInputBorder(),
                    ),
                    validator: (valor) {
                      if ((valor ?? '').trim().isEmpty) {
                        return 'Informe o título';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: ano,
                    decoration: const InputDecoration(
                      labelText: 'Ano',
                      border: OutlineInputBorder(),
                    ),
                    keyboardType: TextInputType.number,
                    validator: (valor) {
                      if (int.tryParse(valor ?? '') == null) {
                        return 'Informe o ano, só com números';
                      }
                      return null;
                    },
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
                    onPressed: salvando ? null : salvar,
                    child: Text(salvando ? 'Salvando...' : 'Salvar'),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
