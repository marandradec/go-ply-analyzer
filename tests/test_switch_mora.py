
import unittest
import parser


class TestSwitchMora(unittest.TestCase):

    def analizar(self, cuerpo):
        codigo = (
            'package main\n'
            'import "fmt"\n'
            'func main() {\n'
            f'{cuerpo}\n'
            '}\n'
        )
        return parser.analizar_sintactico(codigo)

    def test_default_duplicado(self):
        """Dos bloques default deben provocar error sintáctico."""
        arbol, errores = self.analizar("""
    switch 1 {
    default:
        fmt.Println("Primero")
    default:
        fmt.Println("Segundo")
    }
""")
        self.assertGreater(len(errores), 0)
        self.assertTrue(
            any(e["token"] == "default" for e in errores)
        )

    def test_default_intermedio(self):
        """Un default entre dos case es válido."""
        arbol, errores = self.analizar("""
    switch 1 {
    case 1:
        fmt.Println("Uno")
    default:
        fmt.Println("Otro")
    case 2:
        fmt.Println("Dos")
    }
""")
        self.assertIsNotNone(arbol)
        self.assertEqual(errores, [])

    def test_switch_sin_default(self):
        """Un switch puede tener casos sin default."""
        arbol, errores = self.analizar("""
    switch 1 {
    case 1:
        fmt.Println("Uno")
    case 2:
        fmt.Println("Dos")
    }
""")
        self.assertIsNotNone(arbol)
        self.assertEqual(errores, [])


if __name__ == "__main__":
    unittest.main()
