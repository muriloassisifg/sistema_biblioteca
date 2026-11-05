import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../models/livro.dart';
import '../routes.dart';
import '../services/livro_service.dart';
import '../widgets/app_drawer.dart';

// A lista dos livros de quem está logado, vinda da API. A tela tem quatro
// estados, um de cada vez: carregando, erro, lista vazia e a lista. No alto, o
// campo de busca (com o x que a limpa) e o filtro dos disponíveis; o + abre o
// formulário de um livro novo, e o toque, o detalhe (que edita e exclui).
class LivrosScreen extends StatefulWidget {
  const LivrosScreen({super.key});

  @override
  State<LivrosScreen> createState() => _LivrosScreenState();
}

class _LivrosScreenState extends State<LivrosScreen> {
  // O pedido à API: nasce UMA vez, quando a tela nasce, e só é refeito pelo
  // pedirDeNovo. Criado dentro do build, sairia de novo a cada redesenho.
  late Future<List<Livro>> livros;
  // O que a pessoa procurou: '' é a lista inteira.
  String busca = '';
  // O filtro "Só os disponíveis": ligado, a API devolve só os que não estão
  // emprestados.
  bool soDisponiveis = false;
  // O controller do campo de busca: é por ele que o x apaga o texto digitado.
  final campoDaBusca = TextEditingController();

  @override
  void initState() {
    super.initState();
    livros = context.read<LivroService>().listar();
  }

  @override
  void dispose() {
    campoDaBusca.dispose();
    super.dispose();
  }

  // Pede a lista de novo, com a busca de agora: o Tentar de novo, a volta de
  // uma tela que mudou o acervo (fechou com true) e a busca fazem o mesmo.
  void pedirDeNovo() {
    setState(() {
      livros = context.read<LivroService>().listar(busca: busca, soDisponiveis: soDisponiveis);
    });
  }

  // O Enter no campo de busca: guarda o texto e pede de novo. Quem filtra é a
  // API (o ?titulo=), e não a tela.
  void buscar(String texto) {
    busca = texto.trim();
    pedirDeNovo();
  }

  // O x no fim do campo: apaga o texto e volta a lista sem busca.
  void limparABusca() {
    campoDaBusca.clear();
    buscar('');
  }

  // O toque no filtro: liga ou desliga, e pede de novo. A busca continua: os
  // dois filtros vão juntos para a API.
  void filtrar(bool ligado) {
    soDisponiveis = ligado;
    pedirDeNovo();
  }

  // Os quatro estados da lista, como antes; vazia, a frase diz o que foi buscado.
  Widget listaDosLivros() {
    return FutureBuilder<List<Livro>>(
      future: livros,
      builder: (context, snapshot) {
        // 1. Carregando: a resposta ainda não chegou.
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator());
        }
        // 2. Erro: a API recusou, ou nem respondeu.
        if (snapshot.hasError) {
          return Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.cloud_off, size: 56),
                const SizedBox(height: 16),
                const Text('Não consegui carregar os livros'),
                const SizedBox(height: 8),
                Text(
                  '${snapshot.error}',
                  style: const TextStyle(color: Colors.red),
                ),
                const SizedBox(height: 16),
                ElevatedButton(
                  onPressed: pedirDeNovo,
                  child: const Text('Tentar de novo'),
                ),
              ],
            ),
          );
        }
        final lista = snapshot.data!;
        // 3. Vazia: o pedido deu certo, mas não há livro nenhum.
        if (lista.isEmpty) {
          final String frase;
          if (busca.isNotEmpty) {
            frase = 'Nenhum livro com "$busca" no título.';
          } else if (soDisponiveis) {
            frase = 'Nenhum livro disponível agora.';
          } else {
            frase = 'Nenhum livro ainda.';
          }
          return Center(child: Text(frase));
        }
        // 4. A lista: um ListTile por livro. O toque abre o detalhe e leva só
        // o id: a tela do livro busca o livro de agora na API. O await espera
        // o detalhe fechar: com true (editou ou excluiu), a lista pede de novo.
        return ListView.builder(
          itemCount: lista.length,
          itemBuilder: (context, i) {
            final livro = lista[i];
            return ListTile(
              leading: const Icon(Icons.menu_book),
              title: Text(livro.titulo),
              subtitle: Text('${livro.ano}'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () async {
                final mudou = await Navigator.pushNamed(context, AppRoutes.livro, arguments: livro.id);
                if (mudou == true) {
                  pedirDeNovo();
                }
              },
            );
          },
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Livros')),
      drawer: const AppDrawer(),
      body: Column(
        children: [
          // A busca: o Enter (onSubmitted) chama o buscar com o texto digitado;
          // o x (suffixIcon) apaga o texto e volta a lista inteira.
          Padding(
            padding: const EdgeInsets.fromLTRB(12, 12, 12, 4),
            child: TextField(
              controller: campoDaBusca,
              decoration: InputDecoration(
                labelText: 'Buscar pelo título',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: IconButton(
                  icon: const Icon(Icons.clear),
                  tooltip: 'Limpar a busca',
                  onPressed: limparABusca,
                ),
                border: const OutlineInputBorder(),
              ),
              textInputAction: TextInputAction.search,
              onSubmitted: buscar,
            ),
          ),
          // O filtro: um FilterChip, que fica marcado enquanto está ligado.
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12),
            child: Align(
              alignment: Alignment.centerLeft,
              child: FilterChip(
                label: const Text('Só os disponíveis'),
                selected: soDisponiveis,
                onSelected: filtrar,
              ),
            ),
          ),
          // A lista ocupa o resto da tela, embaixo da busca.
          Expanded(child: listaDosLivros()),
        ],
      ),
      // O + abre o formulário vazio. Ele fecha com true quando salvou: aí, a
      // lista pede de novo, e o livro novo aparece.
      floatingActionButton: FloatingActionButton(
        tooltip: 'Novo livro',
        onPressed: () async {
          final salvou = await Navigator.pushNamed(context, AppRoutes.formulario);
          if (salvou == true) {
            pedirDeNovo();
          }
        },
        child: const Icon(Icons.add),
      ),
    );
  }
}
