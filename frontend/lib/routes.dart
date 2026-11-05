// Os nomes das telas, num lugar só. Quem navega escreve AppRoutes.livros e
// não '/livros' solto: um erro de digitação vira erro do editor, não tela em branco.
class AppRoutes {
  static const login = '/login';
  static const cadastro = '/cadastro';
  static const inicio = '/inicio';
  static const livros = '/livros';
  static const livro = '/livro'; // o detalhe de UM livro
  static const formulario = '/formulario'; // criar ou editar um livro
  static const perfil = '/perfil';
}
