import 'package:shared_preferences/shared_preferences.dart';

// A camada de dados do aparelho: o único lugar do app que sabe ONDE o token
// fica guardado. No navegador, é o localStorage do Chrome; no celular, um
// arquivo do app. O resto do app só pede: ler, salvar ou apagar.
class TokenRepository {
  static const _chave = 'token';

  Future<String?> ler() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_chave);
  }

  Future<void> salvar(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_chave, token);
  }

  Future<void> apagar() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_chave);
  }
}
