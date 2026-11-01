# -*- coding: utf-8 -*-
import unittest
from lexer import analizar


class TestLexerAndrade(unittest.TestCase):

    def comprobar(self, codigo, esperados):
        tokens, errores = analizar(codigo)
        self.assertEqual(errores, [])
        self.assertEqual([tipo for tipo, valor, linea in tokens], esperados)

    def test_declaracion_corta(self):
        self.comprobar("edad := 20", ["ID", "DECLARACION_CORTA", "ENTERO"])

    def test_asignacion(self):
        self.comprobar("edad = 21", ["ID", "ASIGNACION", "ENTERO"])

    def test_palabras_reservadas(self):
        self.comprobar("package import func if else",
                       ["PACKAGE", "IMPORT", "FUNC", "IF", "ELSE"])

    def test_tipos(self):
        self.comprobar("int string", ["T_INT", "T_STRING"])

    def test_cadena(self):
        self.comprobar('"Hola Mundo"', ["CADENA"])

    def test_arreglo(self):
        self.comprobar("[3]int{2, 3, 5}",
                       ["ARREGLO", "LLAVE_IZQ", "ENTERO", "COMA", "ENTERO",
                        "COMA", "ENTERO", "LLAVE_DER"])

    def test_identificador_en_blanco(self):
        self.comprobar("_ := 1", ["ID", "DECLARACION_CORTA", "ENTERO"])

    def test_comentarios_se_descartan(self):
        self.comprobar("// una línea\n/* varias\nlíneas */ x", ["NEWLINE", "ID"])

    def test_numero_de_linea_tras_comentario_de_bloque(self):
        tokens, _ = analizar("/* a\nb */\nx")
        self.assertEqual(tokens[-1], ("ID", "x", 3))

    def test_error_cadena_sin_cerrar(self):
        tokens, errores = analizar('x := "hola')
        self.assertEqual(len(errores), 1)
        self.assertIn("Cadena sin cerrar", errores[0]["mensaje"])
        self.assertEqual(errores[0]["linea"], 1)


if __name__ == "__main__":
    unittest.main()
