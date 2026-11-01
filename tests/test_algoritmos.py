# -*- coding: utf-8 -*-
"""
Prueba los archivos .go de la carpeta algoritmos/:
- algoritmo1/2/3.go deben analizarse sin errores y usar TODOS los tokens de su dueño.
- errores_*.go deben producir exactamente los errores léxicos esperados.
"""
import unittest
from pathlib import Path

import lexer
from lexer import analizar

RAIZ = Path(__file__).resolve().parent.parent / "algoritmos"

DUENOS = {
    "algoritmo1.go": ("Andrade", lexer.tokens_andrade, lexer.reservadas_andrade),
    "algoritmo2.go": ("Burgos", lexer.tokens_burgos, lexer.reservadas_burgos),
    "algoritmo3.go": ("Mora", lexer.tokens_mora, lexer.reservadas_mora),
}

# Tokens que se reconocen por regla de función y no figuran en las listas anteriores
ERRORES_ESPERADOS = {
    "errores_andrade.go": ["Cadena sin cerrar"] * 2,
    "errores_burgos.go": ["Número mal formado 12abc", "Número mal formado 3.",
                          "Número mal formado 3.14xyz"],
    "errores_mora.go": ["Símbolo no reconocido @", "Símbolo no reconocido #",
                        "Símbolo no reconocido $"],
}


def leer(nombre):
    return (RAIZ / nombre).read_text(encoding="utf-8")


class TestAlgoritmos(unittest.TestCase):

    def test_algoritmos_sin_errores_y_con_todos_sus_tokens(self):
        for archivo, (dueno, tokens_lista, reservadas) in DUENOS.items():
            with self.subTest(archivo=archivo):
                tokens, errores = analizar(leer(archivo))
                self.assertEqual(errores, [], f"{archivo} no debe tener errores")
                vistos = {tipo for tipo, _, _ in tokens}
                esperados = set(tokens_lista) | set(reservadas.values())
                self.assertEqual(sorted(esperados - vistos), [],
                                 f"{archivo}: tokens de {dueno} sin cubrir")

    def test_archivos_de_errores(self):
        for archivo, mensajes in ERRORES_ESPERADOS.items():
            with self.subTest(archivo=archivo):
                _, errores = analizar(leer(archivo))
                self.assertEqual(len(errores), len(mensajes))
                for error, parte in zip(errores, mensajes):
                    self.assertIn(parte, error["mensaje"])

    def test_formato_del_mensaje(self):
        _, errores = analizar("x := @")
        self.assertEqual(errores[0]["mensaje"],
                         "Error léxico en la línea 1. Símbolo no reconocido @")

    def test_la_linea_se_reinicia_en_cada_analisis(self):
        analizar("a\nb\nc")
        tokens, _ = analizar("x")
        self.assertEqual(tokens[0][2], 1)


if __name__ == "__main__":
    unittest.main()
