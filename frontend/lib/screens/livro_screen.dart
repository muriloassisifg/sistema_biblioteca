import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../models/livro.dart';
import '../routes.dart';
import '../services/livro_service.dart';
import '../widgets/aviso.dart';
import 'livros_screen.dart';

// O detalhe de um livro. Chega só o id, e a tela pede o livro à API: o dado é
// o de agora, e não o de quando a lista carregou. Daqui, o livro se edita e
// se exclui; quando um dos dois dá certo, a tela fecha com true.
class LivroScreen extends StatefulWidget {
  const LivroScreen({super.key, this.id});

  // O id que a rota tirou dos arguments. Sem ele (um F5 aqui apaga os
  // arguments, que moram na memória), a tela mostra a lista.
  final int? id;

  @override
  State<LivroScreen> createState() => _LivroScreenState();
}

class _LivroScreenState extends State<LivroScreen> {
  // O pedido do livro: como o da lista, nasce uma vez, no initState.
  late Future<Livro> pedido;
  // A recusa da exclusão (o livro emprestado, por exemplo), para a tela mostrar.
  String? erro;

  @override
  void initState() {
    super.initState();
    if (widget.id != null) {
      pedido = context.read<LivroService>().buscar(widget.id!);
    }
  }

  void tentarDeNovo() {
    setState(() {
      pedido = context.read<LivroService>().buscar(widget.id!);
    });
  }

  // Abre o formulário com o livro, para editar. Se ele voltar com true (salvou),
  // esta tela também fecha com true: passa a notícia para a lista.
  Future<void> editar(Livro livro) async {
    final salvou = await Navigator.pushNamed(context, AppRoutes.formulario, arguments: livro);
    if (salvou == true && mounted) {
      Navigator.pop(context, true);
    }
  }

  // Pergunta antes de excluir. O diálogo é uma tela por cima, e fecha devolvendo
  // um valor: true no Excluir, false no Cancelar, null num toque fora dele.
  Future<void> excluir(Livro livro) async {
    final certeza = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Excluir ${livro.titulo}?'),
        content: const Text('Tem certeza? O livro sai do seu acervo, e não dá para desfazer.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancelar'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Excluir'),
          ),
        ],
      ),
    );
    if (certeza != true || !mounted) {
      return;
    }
    try {
      await context.read<LivroService>().excluir(livro.id);
    } on ErroDeLivros catch (e) {
      if (!mounted) return;
      setState(() {
        erro = '$e';
      });
      avisar(context, 'Não deu para excluir', erro: true);
      return;
    }
    if (!mounted) return;
    avisar(context, 'Livro excluído');
    Navigator.pop(context, true);
  }

  @override
  Widget build(BuildContext context) {
    if (widget.id == null) {
      return const LivrosScreen();
    }
    return Scaffold(
      appBar: AppBar(title: const Text('Livro')),
      body: FutureBuilder<Livro>(
        future: pedido,
        builder: (context, snapshot) {
          // Os estados da lista, de novo. O vazio não existe aqui: o livro que
          // sumiu é um 404 da API, e vira erro.
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(Icons.cloud_off, size: 56),
                  const SizedBox(height: 16),
                  const Text('Não consegui carregar o livro'),
                  const SizedBox(height: 8),
                  Text(
                    '${snapshot.error}',
                    style: const TextStyle(color: Colors.red),
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: tentarDeNovo,
                    child: const Text('Tentar de novo'),
                  ),
                ],
              ),
            );
          }
          final livro = snapshot.data!;
          return ListView(
            children: [
              ListTile(
                leading: const Icon(Icons.menu_book),
                title: const Text('Título'),
                subtitle: Text(livro.titulo),
              ),
              ListTile(
                leading: const Icon(Icons.calendar_month),
                title: const Text('Ano'),
                subtitle: Text('${livro.ano}'),
              ),
              ListTile(
                leading: Icon(livro.disponivel ? Icons.check_circle : Icons.schedule),
                title: const Text('Situação'),
                subtitle: Text(livro.disponivel ? 'Disponível' : 'Emprestado'),
              ),
              const SizedBox(height: 16),
              // Editar e Excluir: o livro já está na mão, e é o de agora.
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  ElevatedButton.icon(
                    onPressed: () => editar(livro),
                    icon: const Icon(Icons.edit),
                    label: const Text('Editar'),
                  ),
                  const SizedBox(width: 16),
                  OutlinedButton.icon(
                    onPressed: () => excluir(livro),
                    icon: const Icon(Icons.delete),
                    label: const Text('Excluir'),
                  ),
                ],
              ),
              if (erro != null) ...[
                const SizedBox(height: 16),
                Text(
                  erro!,
                  textAlign: TextAlign.center,
                  style: const TextStyle(color: Colors.red),
                ),
              ],
            ],
          );
        },
      ),
    );
  }
}
