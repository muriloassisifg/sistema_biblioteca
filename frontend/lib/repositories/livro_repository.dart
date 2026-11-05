import 'dart:convert';

import 'package:http/http.dart' as http;

import '../models/livro.dart';
import 'usuario_repository.dart';

// O repositório dos livros: como o do usuário, o único que sabe endereço,
// HTTP e JSON. O endereço da API e a RecusaDaApi vêm do usuario_repository.
class LivroRepository {
  LivroRepository({http.Client? cliente}) : cliente = cliente ?? http.Client();

  final http.Client cliente;

  // GET /livros/, com o token no cabeçalho, como o quemSouEu: a API devolve só
  // os livros do dono do token. Cada filtro escolhido vira um parâmetro de
  // consulta: a busca, o ?titulo=; o "só os disponíveis", o ?disponivel=true.
  // Os dois juntos: ?titulo=cas&disponivel=true. A resposta é uma LISTA em
  // JSON, e cada item vira um Livro: é o [Livro.from_json(item) for item in
  // itens] do Python.
  Future<List<Livro>> listar(String token, {String busca = '', bool soDisponiveis = false}) async {
    var endereco = Uri.parse('$enderecoDaApi/livros/');
    // O if dentro do mapa: a chave só entra quando o filtro foi escolhido.
    final filtros = {
      if (busca.isNotEmpty) 'titulo': busca,
      if (soDisponiveis) 'disponivel': 'true',
    };
    if (filtros.isNotEmpty) {
      // O replace monta o ?titulo=...&disponivel=... e codifica o espaço e o acento.
      endereco = endereco.replace(queryParameters: filtros);
    }
    final resposta = await cliente.get(
      endereco,
      headers: {'Authorization': 'Bearer $token'},
    );
    if (resposta.statusCode != 200) {
      throw RecusaDaApi(resposta.statusCode, _frase(resposta.body));
    }
    final itens = jsonDecode(resposta.body);
    return [for (final item in itens) Livro.fromJson(item)];
  }

  // GET /livros/{id}: um livro só, como ele está AGORA no banco. Livro de
  // outra pessoa, ou que não existe mais, a API responde 404.
  Future<Livro> buscar(String token, int id) async {
    final resposta = await cliente.get(
      Uri.parse('$enderecoDaApi/livros/$id'),
      headers: {'Authorization': 'Bearer $token'},
    );
    if (resposta.statusCode != 200) {
      throw RecusaDaApi(resposta.statusCode, _frase(resposta.body));
    }
    return Livro.fromJson(jsonDecode(resposta.body));
  }

  // POST /livros/: o livro novo vai em JSON no corpo, como no cadastro da
  // conta, e o token no cabeçalho. A API responde 201 e o livro criado.
  Future<Livro> criar(String token, String titulo, int ano) async {
    final resposta = await cliente.post(
      Uri.parse('$enderecoDaApi/livros/'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
      body: jsonEncode({'titulo': titulo, 'ano': ano}),
    );
    if (resposta.statusCode != 201) {
      throw RecusaDaApi(resposta.statusCode, _frase(resposta.body));
    }
    return Livro.fromJson(jsonDecode(resposta.body));
  }

  // PATCH /livros/{id}: só o que o formulário edita, o título e o ano. A
  // situação (disponivel) não vai: a API não deixa editá-la pelo catálogo.
  Future<Livro> atualizar(String token, int id, String titulo, int ano) async {
    final resposta = await cliente.patch(
      Uri.parse('$enderecoDaApi/livros/$id'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
      body: jsonEncode({'titulo': titulo, 'ano': ano}),
    );
    if (resposta.statusCode != 200) {
      throw RecusaDaApi(resposta.statusCode, _frase(resposta.body));
    }
    return Livro.fromJson(jsonDecode(resposta.body));
  }

  // DELETE /livros/{id}: a API responde 204, sem corpo nenhum.
  Future<void> excluir(String token, int id) async {
    final resposta = await cliente.delete(
      Uri.parse('$enderecoDaApi/livros/$id'),
      headers: {'Authorization': 'Bearer $token'},
    );
    if (resposta.statusCode != 204) {
      throw RecusaDaApi(resposta.statusCode, _frase(resposta.body));
    }
  }

  // A frase da recusa, como no UsuarioRepository: o "detail" é um texto (404,
  // 409) ou uma lista, com um item por campo errado (422). O Pydantic põe
  // "Value error, " na frente das mensagens dos validadores da API: sai aqui.
  String _frase(String corpo) {
    final detalhe = jsonDecode(corpo)['detail'];
    if (detalhe is String) {
      return detalhe;
    }
    final primeiro = detalhe[0];
    final mensagem = '${primeiro['msg']}'.replaceFirst('Value error, ', '');
    return '${primeiro['loc'].last}: $mensagem';
  }
}
