import 'package:flutter/foundation.dart';

import '../models/usuario.dart';
import '../repositories/usuario_repository.dart';

// Uma recusa do app, com a frase para a tela mostrar: como os erros.py do backend.
class ErroDeLogin implements Exception {
  ErroDeLogin(this.mensagem);

  final String mensagem;
}

// A camada de negócio do app: as regras do login e quem está logado.
// Não sabe de tela nem de HTTP. É um ChangeNotifier: quando a sessão muda,
// ele avisa (notifyListeners) quem estiver de olho.
class SessaoService extends ChangeNotifier {
  SessaoService(this.repositorio);

  final UsuarioRepository repositorio;
  String? token;
  Usuario? usuario;

  bool get logado => token != null;

  Future<void> entrar(String email, String senha) async {
    if (email.isEmpty || senha.isEmpty) {
      throw ErroDeLogin('Preencha o e-mail e a senha');
    }
    String? recebido;
    Usuario? quem;
    try {
      recebido = await repositorio.entrar(email, senha);
      if (recebido != null) {
        quem = await repositorio.quemSouEu(recebido);
      }
    } catch (e) {
      throw ErroDeLogin('Não consegui falar com a API. O uvicorn está rodando?');
    }
    if (recebido == null) {
      throw ErroDeLogin('E-mail ou senha incorretos');
    }
    token = recebido;
    usuario = quem;
    notifyListeners();
  }

  void sair() {
    token = null;
    usuario = null;
    notifyListeners();
  }
}
