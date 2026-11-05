import 'package:flutter/material.dart';

// O aviso de toda ação: uma faixa embaixo da tela, que some sozinha (o
// SnackBar). Verde quando deu certo, vermelho quando não deu. Quem a mostra é
// o ScaffoldMessenger do app inteiro: por isso o aviso continua na tela mesmo
// depois que a tela que o pediu fecha. Ele guarda os avisos numa fila; o
// hideCurrentSnackBar tira o que está na tela, e o novo aparece na hora.
void avisar(BuildContext context, String texto, {bool erro = false}) {
  final mensageiro = ScaffoldMessenger.of(context);
  mensageiro.hideCurrentSnackBar();
  mensageiro.showSnackBar(
    SnackBar(
      content: Text(texto),
      backgroundColor: erro ? Colors.red : Colors.green,
    ),
  );
}
