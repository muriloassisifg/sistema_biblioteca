// O usuário como o app o conhece: o mesmo UsuarioPublico que a API devolve.
class Usuario {
  Usuario({required this.id, required this.nome, required this.email});

  final int id;
  final String nome;
  final String email;

  // Monta um Usuario a partir do JSON da API: {"id": 1, "nome": "Ana", ...}.
  factory Usuario.fromJson(Map<String, dynamic> json) {
    return Usuario(id: json['id'], nome: json['nome'], email: json['email']);
  }
}
