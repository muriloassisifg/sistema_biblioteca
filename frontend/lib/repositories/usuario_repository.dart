import 'dart:convert';

import 'package:http/http.dart' as http;

import '../models/usuario.dart';

// Onde a API roda: o uvicorn, na porta de sempre.
const enderecoDaApi = 'http://127.0.0.1:8000';

// A API disse não: o código HTTP e a frase que ela mandou, já em texto simples.
// É a língua do repositório; quem decide o que a tela mostra é o service.
class RecusaDaApi implements Exception {
  RecusaDaApi(this.status, this.mensagem);

  final int status;
  final String mensagem;
}

// A camada de dados: o único lugar do app que sabe endereço, HTTP e JSON.
// No backend, o repository fala com o banco; aqui, ele fala com a API.
class UsuarioRepository {
  UsuarioRepository({http.Client? cliente}) : cliente = cliente ?? http.Client();

  final http.Client cliente;

  // Manda o e-mail e a senha, como o Authorize do /docs. Devolve o token,
  // ou null se a API recusar.
  Future<String?> entrar(String email, String senha) async {
    final resposta = await cliente.post(
      Uri.parse('$enderecoDaApi/usuarios/login'),
      body: {'username': email, 'password': senha},
    );
    if (resposta.statusCode != 200) {
      return null;
    }
    final corpo = jsonDecode(resposta.body);
    return corpo['access_token'];
  }

  // Cria a conta: o POST /usuarios/, com os dados em JSON no corpo do pedido.
  // A API responde 201 e o usuário criado; qualquer outra resposta vira uma
  // RecusaDaApi, com a frase que a API mandou.
  Future<Usuario> cadastrar(String nome, String email, String senha) async {
    final resposta = await cliente.post(
      Uri.parse('$enderecoDaApi/usuarios/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'nome': nome, 'email': email, 'senha': senha}),
    );
    if (resposta.statusCode != 201) {
      throw RecusaDaApi(resposta.statusCode, _frase(resposta.body));
    }
    return Usuario.fromJson(jsonDecode(resposta.body));
  }

  // Pergunta quem é o dono do token. O token vai no cabeçalho do pedido.
  Future<Usuario> quemSouEu(String token) async {
    final resposta = await cliente.get(
      Uri.parse('$enderecoDaApi/usuarios/eu'),
      headers: {'Authorization': 'Bearer $token'},
    );
    if (resposta.statusCode != 200) {
      throw RecusaDaApi(resposta.statusCode, _frase(resposta.body));
    }
    return Usuario.fromJson(jsonDecode(resposta.body));
  }

  // Tira do JSON de erro a frase que vale mostrar. O "detail" é um texto
  // (no 409) ou uma lista, com um item por campo errado (no 422).
  String _frase(String corpo) {
    final detalhe = jsonDecode(corpo)['detail'];
    if (detalhe is String) {
      return detalhe;
    }
    final primeiro = detalhe[0];
    return '${primeiro['loc'].last}: ${primeiro['msg']}';
  }
}
