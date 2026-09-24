import 'dart:convert';

import 'package:http/http.dart' as http;

import '../models/usuario.dart';

// Onde a API roda: o uvicorn, na porta de sempre.
const enderecoDaApi = 'http://127.0.0.1:8000';

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

  // Pergunta quem é o dono do token. O token vai no cabeçalho do pedido.
  Future<Usuario> quemSouEu(String token) async {
    final resposta = await cliente.get(
      Uri.parse('$enderecoDaApi/usuarios/eu'),
      headers: {'Authorization': 'Bearer $token'},
    );
    return Usuario.fromJson(jsonDecode(resposta.body));
  }
}
