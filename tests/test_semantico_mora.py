"""Pruebas de Mora sobre el UNICO motor semantico compartido (semantic.py).

Mantiene 24 escenarios: 7 de break, 10 de asignacion/constantes,
3 con AST real de PLY y 4 de integracion con archivos Go.
No importa ni replica semantico_mora.py.
"""

import unittest
from pathlib import Path

from parser import analizar_sintactico
from semantic import analizar_completo_semantico, analizar_semantico

RAIZ = Path(__file__).resolve().parents[1]


def programa(cuerpo, funciones=""):
    """Construye un programa Go del subconjunto soportado por el equipo."""
    return (
        'package main\n'
        'import "fmt"\n'
        f'{funciones}\n'
        'func main() {\n'
        f'{cuerpo}\n'
        '}\n'
    )


class AyudasMora(unittest.TestCase):
    """Ejecuta las tres fases reales; nunca simula una tabla de simbolos."""

    def analizar(self, cuerpo, funciones=""):
        resultado = analizar_completo_semantico(programa(cuerpo, funciones))
        self.assertEqual(resultado["errores_lexicos"], [], "Error lexico inesperado")
        self.assertEqual(resultado["errores_sintacticos"], [], "Error sintactico inesperado")
        self.assertTrue(resultado["semantico_ejecutado"])
        return resultado["errores_semanticos"]

    def categoria(self, errores, nombre):
        return [e for e in errores if e.get("categoria") == nombre]

    def errores_break(self, errores):
        return [
            e for e in self.categoria(errores, "Estructuras de control")
            if "break" in e.get("mensaje", "").lower()
        ]

    def errores_asignacion(self, errores):
        return self.categoria(errores, "Asignación de tipo")


# INICIO aporte: MORA (control de break)
class TestBreakMora(AyudasMora):
    def test_break_fuera_de_control(self):
        self.assertEqual(len(self.errores_break(self.analizar("break"))), 1)

    def test_break_dentro_de_for(self):
        errores = self.analizar("for i := 0; i < 3; i++ {\n break\n }")
        self.assertEqual(self.errores_break(errores), [])

    def test_break_dentro_de_switch(self):
        errores = self.analizar(
            'dia := 1\n switch dia {\n case 1:\n break\n'
            ' default:\n fmt.Println("otro")\n }'
        )
        self.assertEqual(self.errores_break(errores), [])

    def test_break_dentro_de_if_sin_for(self):
        errores = self.analizar("if true {\n break\n }")
        self.assertEqual(len(self.errores_break(errores)), 1)

    def test_break_dentro_de_if_con_for(self):
        errores = self.analizar(
            "for i := 0; i < 3; i++ {\n"
            " if i == 1 {\n break\n }\n }"
        )
        self.assertEqual(self.errores_break(errores), [])

    def test_break_despues_de_for(self):
        errores = self.analizar(
            "for i := 0; i < 3; i++ {\n break\n }\n break"
        )
        self.assertEqual(len(self.errores_break(errores)), 1)

    def test_algoritmo3_real(self):
        ruta = RAIZ / "algoritmos" / "algoritmo3.go"
        resultado = analizar_completo_semantico(ruta.read_text(encoding="utf-8"))
        self.assertEqual(resultado["errores_lexicos"], [])
        self.assertEqual(resultado["errores_sintacticos"], [])
        self.assertEqual(self.errores_break(resultado["errores_semanticos"]), [])
# FIN aporte: MORA (control de break)


# INICIO aporte: MORA (asignacion estricta y constantes)
class TestAsignacionMora(AyudasMora):
    def test_declaracion_correcta(self):
        self.assertEqual(self.errores_asignacion(self.analizar("var x int = 10")), [])

    def test_declaracion_tipo_incorrecto(self):
        errores = self.analizar('var x int = "hola"')
        self.assertGreaterEqual(len(self.errores_asignacion(errores)), 1)

    def test_asignacion_tipo_incorrecto(self):
        errores = self.analizar("var edad int = 20\n edad = true")
        self.assertGreaterEqual(len(self.errores_asignacion(errores)), 1)

    def test_constante_valida(self):
        self.assertEqual(
            self.errores_asignacion(self.analizar("const MAX int = 100")), []
        )

    def test_modificar_constante(self):
        errores = self.analizar("const MAX int = 100\n MAX = 5")
        self.assertTrue(any("constante" in e["mensaje"].lower()
                            for e in self.errores_asignacion(errores)))

    def test_modificar_constante_con_asignacion_compuesta(self):
        errores = self.analizar("const MAX int = 100\n MAX += 1")
        self.assertTrue(any("constante" in e["mensaje"].lower()
                            for e in self.errores_asignacion(errores)))

    def test_incrementar_constante(self):
        errores = self.analizar("const MAX int = 100\n MAX++")
        self.assertTrue(any("constante" in e["mensaje"].lower()
                            for e in self.errores_asignacion(errores)))

    def test_asignacion_valida_en_mapa(self):
        errores = self.analizar(
            'edades := map[string]int{"Ana": 20}\n edades["Ana"] = 25'
        )
        self.assertEqual(self.errores_asignacion(errores), [])

    def test_asignacion_incorrecta_en_mapa(self):
        errores = self.analizar(
            'edades := map[string]int{"Ana": 20}\n edades["Ana"] = "veinte"'
        )
        self.assertGreaterEqual(len(self.errores_asignacion(errores)), 1)

    def test_identificador_inexistente_no_duplica_error(self):
        errores = self.analizar("desconocido = 5")
        self.assertEqual(self.errores_asignacion(errores), [])
        self.assertTrue(errores, "Andrade debe reportar la variable inexistente")
# FIN aporte: MORA (asignacion estricta y constantes)


# INICIO aporte: MORA (AST real de PLY, sin funciones duplicadas)
class TestIntegracionASTAsignacionMora(AyudasMora):
    def analizar_ast(self, cuerpo):
        arbol, errores_sintacticos = analizar_sintactico(programa(cuerpo))
        self.assertEqual(errores_sintacticos, [])
        self.assertIsNotNone(arbol)
        _tabla, errores_semanticos = analizar_semantico(arbol)
        return errores_semanticos

    def test_declaracion_incompatible_ast_real(self):
        errores = self.analizar_ast('var edad int = "hola"')
        self.assertGreaterEqual(len(self.errores_asignacion(errores)), 1)

    def test_modificacion_constante_ast_real(self):
        errores = self.analizar_ast('const MAX int = 100\n MAX = 5')
        self.assertTrue(any("constante" in e["mensaje"].lower()
                            for e in self.errores_asignacion(errores)))

    def test_asignacion_incompatible_ast_real(self):
        errores = self.analizar_ast('var edad int = 20\n edad = "veinte"')
        self.assertGreaterEqual(len(self.errores_asignacion(errores)), 1)
# FIN aporte: MORA (AST real)


# INICIO aporte: MORA (integracion semantica del equipo)
class TestIntegracionSemanticaMora(AyudasMora):
    def analizar_archivo(self, nombre):
        ruta = RAIZ / "algoritmos" / nombre
        resultado = analizar_completo_semantico(ruta.read_text(encoding="utf-8"))
        self.assertEqual(resultado["errores_lexicos"], [])
        self.assertEqual(resultado["errores_sintacticos"], [])
        self.assertTrue(resultado["semantico_ejecutado"])
        return resultado

    def test_algoritmo3_semanticamente_valido(self):
        r = self.analizar_archivo("algoritmo3.go")
        self.assertEqual(r["errores_semanticos"], [])

    def test_errores_semanticos_mora(self):
        r = self.analizar_archivo("errores_semantico_mora.go")
        self.assertEqual(len(r["errores_semanticos"]), 18)

    def test_asignaciones_y_constantes_mora(self):
        r = self.analizar_archivo("errores_semantico_mora.go")
        lineas = {e["linea"] for e in self.errores_asignacion(r["errores_semanticos"])}
        self.assertTrue({7, 12, 17, 23, 29, 35, 41, 47}.issubset(lineas))

    def test_break_invalido_mora(self):
        r = self.analizar_archivo("errores_semantico_mora.go")
        lineas = {e["linea"] for e in self.errores_break(r["errores_semanticos"])}
        self.assertEqual(lineas, {81, 88})
# FIN aporte: MORA (integracion semantica del equipo)


if __name__ == "__main__":
    unittest.main()
