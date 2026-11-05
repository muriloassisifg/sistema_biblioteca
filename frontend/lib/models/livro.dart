// O livro como o app o conhece: o mesmo LivroPublico que a API devolve.
class Livro {
  Livro({
    required this.id,
    required this.titulo,
    required this.ano,
    required this.disponivel,
  });

  final int id;
  final String titulo;
  final int ano;
  final bool disponivel;

  // Monta um Livro a partir de um item do JSON da API:
  // {"id": 1, "titulo": "Dom Casmurro", "ano": 1899, "disponivel": true, ...}.
  // O que o app não usa (o dono_id) fica de fora.
  factory Livro.fromJson(Map<String, dynamic> json) {
    return Livro(
      id: json['id'],
      titulo: json['titulo'],
      ano: json['ano'],
      disponivel: json['disponivel'],
    );
  }
}
