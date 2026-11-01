# -*- coding: utf-8 -*-
import unittest
from lexer import analizar


class TestLexerBurgos(unittest.TestCase):

    def comprobar(self, codigo, esperados):
        tokens, errores = analizar(codigo)
        self.assertEqual(errores, [])
        self.assertEqual([tipo for tipo, valor, linea in tokens], esperados)

    def test_palabras_reservadas(self):
        self.comprobar("var const for break return",
                       ["VAR", "CONST", "FOR", "BREAK", "RETURN"])

    def test_tipo_float64(self):
        self.comprobar("float64", ["T_FLOAT64"])

    def test_literal_flotante(self):
        tokens, errores = analizar("3.14")
        self.assertEqual(errores, [])
        self.assertEqual(tokens, [("FLOAT_LITERAL", 3.14, 1)])

    def test_matriz(self):
        self.comprobar("[2][2]int", ["MATRIZ"])

    def test_aritmeticos(self):
        self.comprobar("a + b - c * d / e % f",
                       ["ID", "PLUS", "ID", "MINUS", "ID", "TIMES", "ID",
                        "DIVIDE", "ID", "MODULO", "ID"])

    def test_comparacion(self):
        self.comprobar("a == b != c < d <= e > f >= g",
                       ["ID", "EQ", "ID", "NEQ", "ID", "LT", "ID", "LE",
                        "ID", "GT", "ID", "GE", "ID"])

    def test_for_con_punto_y_coma(self):
        self.comprobar("for i := 0; i < 10; i++",
                       ["FOR", "ID", "DECLARACION_CORTA", "ENTERO", "SEMICOLON",
                        "ID", "LT", "ENTERO", "SEMICOLON", "ID", "INCREMENT"])

    def test_error_numero_con_letras(self):
        _, errores = analizar("12abc")
        self.assertEqual(len(errores), 1)
        self.assertIn("Número mal formado 12abc", errores[0]["mensaje"])

    def test_error_punto_sin_decimales(self):
        _, errores = analizar("3.")
        self.assertEqual(len(errores), 1)
        self.assertIn("Número mal formado 3.", errores[0]["mensaje"])

    def test_error_flotante_con_letras(self):
        _, errores = analizar("3.14abc")
        self.assertEqual(len(errores), 1)
        self.assertIn("Número mal formado 3.14abc", errores[0]["mensaje"])


if __name__ == "__main__":
    unittest.main()
