import '../models/livro.dart';
import '../repositories/livro_repository.dart';
import '../repositories/usuario_repository.dart';
import 'sessao_service.dart';

// A recusa dos livros, com a frase que a tela mostra.
class ErroDeLivros implements Exception {
  ErroDeLivros(this.mensagem);

  final String mensagem;

  // O texto do erro quando a tela o mostra: é o __str__ do Python.
  @override
  String toString() => mensagem;
}

// As regras dos livros. Não guarda estado (não é um ChangeNotifier): quem
// lembra se está carregando, se deu erro ou qual é a lista é a própria tela.
// O service pega o token na sessão, pede ao repositório e traduz a recusa.
class LivroService {
  LivroService(this.repositorio, this.sessao);

  final LivroRepository repositorio;
  final SessaoService sessao;

  // A lista inteira, ou só a que passa nos filtros: a busca no título ('' =
  // todos) e o "só os disponíveis".
  Future<List<Livro>> listar({String busca = '', bool soDisponiveis = false}) async {
    try {
      // O guarda só abre a tela de livros com sessão: o token nunca é null aqui.
      return await repositorio.listar(sessao.token!, busca: busca, soDisponiveis: soDisponiveis);
    } on RecusaDaApi catch (e) {
      throw ErroDeLivros(e.mensagem);
    } on Exception {
      // Uma falha de fora, como a rede: a API nem respondeu (o uvicorn parado).
      // Um erro do próprio código não é Exception: passa direto, e a tela o
      // mostra inteiro.
      throw ErroDeLivros('Não consegui falar com a API. O uvicorn está rodando?');
    }
  }

  // Um livro só, pelo id: as mesmas regras do listar.
  Future<Livro> buscar(int id) async {
    try {
      return await repositorio.buscar(sessao.token!, id);
    } on RecusaDaApi catch (e) {
      throw ErroDeLivros(e.mensagem);
    } on Exception {
      throw ErroDeLivros('Não consegui falar com a API. O uvicorn está rodando?');
    }
  }

  // Criar, editar e excluir: o mesmo molde do listar. O token vem da sessão,
  // e a recusa da API (422, 409, 404) vira a frase que a tela mostra.
  Future<Livro> criar(String titulo, int ano) async {
    try {
      return await repositorio.criar(sessao.token!, titulo, ano);
    } on RecusaDaApi catch (e) {
      throw ErroDeLivros(e.mensagem);
    } on Exception {
      throw ErroDeLivros('Não consegui falar com a API. O uvicorn está rodando?');
    }
  }

  Future<Livro> atualizar(int id, String titulo, int ano) async {
    try {
      return await repositorio.atualizar(sessao.token!, id, titulo, ano);
    } on RecusaDaApi catch (e) {
      throw ErroDeLivros(e.mensagem);
    } on Exception {
      throw ErroDeLivros('Não consegui falar com a API. O uvicorn está rodando?');
    }
  }

  Future<void> excluir(int id) async {
    try {
      await repositorio.excluir(sessao.token!, id);
    } on RecusaDaApi catch (e) {
      throw ErroDeLivros(e.mensagem);
    } on Exception {
      throw ErroDeLivros('Não consegui falar com a API. O uvicorn está rodando?');
    }
  }
}
