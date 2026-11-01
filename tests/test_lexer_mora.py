
import unittest
from lexer import analizar


class TestLexerMora(unittest.TestCase):

    def comprobar(self, codigo, esperados):
        tokens, errores = analizar(codigo)
        tipos = [tipo for tipo, valor, linea in tokens]

        self.assertEqual(errores, [])
        self.assertEqual(tipos, esperados)

    def test_mapa(self):
        self.comprobar(
            "map[string]int",
            ["MAPA"]
        )

    def test_println(self):
        self.comprobar(
            "fmt.Println(true)",
            ["FMT_PRINTLN", "PAREN_IZQ",
             "BOOL_LITERAL", "PAREN_DER"]
        )

    def test_scanln(self):
        self.comprobar(
            "fmt.Scanln(&nombre)",
            ["FMT_SCANLN", "PAREN_IZQ",
             "AMPERSAND", "ID", "PAREN_DER"]
        )

    def test_operadores_logicos(self):
        self.comprobar(
            "true && !false || true",
            ["BOOL_LITERAL", "AND", "NOT",
             "BOOL_LITERAL", "OR", "BOOL_LITERAL"]
        )

    def test_asignacion_compuesta(self):
        self.comprobar(
            "x += 5",
            ["ID", "PLUS_ASSIGN", "ENTERO"]
        )

    def test_incremento(self):
        self.comprobar(
            "x++",
            ["ID", "INCREMENT"]
        )

    def test_decremento(self):
        self.comprobar(
            "x--",
            ["ID", "DECREMENT"]
        )

    def test_switch(self):
        self.comprobar(
            "switch x { case 1: default: }",
            ["SWITCH", "ID", "LLAVE_IZQ",
             "CASE", "ENTERO", "DOSPUNTOS",
             "DEFAULT", "DOSPUNTOS", "LLAVE_DER"]
        )

    def test_error_simbolo(self):
        tokens, errores = analizar("@")
        self.assertEqual(tokens, [])
        self.assertEqual(len(errores), 1)
        self.assertIn("no reconocido", errores[0]["mensaje"])


if __name__ == "__main__":
    unittest.main()
