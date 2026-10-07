import 'package:flutter/foundation.dart';

import '../models/usuario.dart';
import '../repositories/token_repository.dart';
import '../repositories/usuario_repository.dart';

// Uma recusa do app, com a frase para a tela mostrar: como os erros.py do backend.
class ErroDeLogin implements Exception {
  ErroDeLogin(this.mensagem);

  final String mensagem;
}

// A recusa do cadastro: a mesma ideia, com a frase que a tela mostra.
class ErroDeCadastro implements Exception {
  ErroDeCadastro(this.mensagem);

  final String mensagem;
}

// A camada de negócio do app: as regras do login e do cadastro e quem está
// logado. Não sabe de tela e não faz HTTP nem JSON: quem faz é o repositório.
// É um ChangeNotifier: quando a sessão muda, ele avisa (notifyListeners) quem
// estiver de olho.
class SessaoService extends ChangeNotifier {
  SessaoService(this.repositorio, {TokenRepository? tokens})
      : tokens = tokens ?? TokenRepository();

  final UsuarioRepository repositorio;
  final TokenRepository tokens;
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
    await tokens.salvar(recebido);
    notifyListeners();
  }

  // Cria a conta e já entra com ela, pelo mesmo caminho do login.
  Future<void> cadastrar(String nome, String email, String senha) async {
    if (nome.isEmpty || email.isEmpty || senha.isEmpty) {
      throw ErroDeCadastro('Preencha o nome, o e-mail e a senha');
    }
    try {
      await repositorio.cadastrar(nome, email, senha);
      await entrar(email, senha);
    } on RecusaDaApi catch (e) {
      if (e.status == 409) {
        throw ErroDeCadastro('Já existe uma conta com este e-mail');
      }
      throw ErroDeCadastro(e.mensagem);
    } on ErroDeLogin {
      throw ErroDeCadastro('Conta criada, mas não consegui entrar. Tente pelo login.');
    } catch (e) {
      throw ErroDeCadastro('Não consegui falar com a API. O uvicorn está rodando?');
    }
  }

  // Roda uma vez, antes de a primeira tela aparecer: se há um token guardado
  // no aparelho e a API ainda o aceita, a sessão volta sozinha.
  Future<void> restaurar() async {
    final guardado = await tokens.ler();
    if (guardado == null) {
      return;
    }
    try {
      usuario = await repositorio.quemSouEu(guardado);
      token = guardado;
      notifyListeners();
    } on RecusaDaApi {
      // A API respondeu e disse não: o token venceu, ou não vale mais.
      await tokens.apagar();
    } catch (e) {
      // A API nem respondeu (uvicorn parado): o token fica guardado, e o app
      // abre no login. Quando a API voltar, a sessão volta no próximo F5.
    }
  }

  Future<void> sair() async {
    await tokens.apagar();
    token = null;
    usuario = null;
    notifyListeners();
  }
}
