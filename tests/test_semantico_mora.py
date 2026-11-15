
"""
Pruebas unitarias de las reglas semánticas de Mora.

Avance 3: control válido de break dentro de for o switch.
"""

import unittest
from pathlib import Path

from parser import analizar_sintactico
from semantico_mora import validar_break
from semantico_mora import validar_break, validar_asignacion_mora


RAIZ = Path(__file__).resolve().parents[1]


class TestSemanticoMora(unittest.TestCase):

    # INICIO aporte: MORA (pruebas semánticas)

    def test_break_fuera_de_control(self):
        """Un break aislado debe generar un error."""
        arbol = ("break", 5)

        errores = validar_break(arbol)

        self.assertEqual(len(errores), 1)
        self.assertEqual(errores[0]["linea"], 5)
        self.assertEqual(
            errores[0]["categoria"],
            "Estructuras de control"
        )

    def test_break_dentro_de_for(self):
        """Un break dentro de for es válido."""
        arbol = (
            "for",
            None,
            None,
            None,
            [("break", 8)],
            4
        )

        errores = validar_break(arbol)

        self.assertEqual(errores, [])

    def test_break_dentro_de_switch(self):
        """Un break dentro de case es válido."""
        arbol = (
            "switch",
            ("id", "dia", 3),
            [
                (
                    "case",
                    [("entero", 1, 4)],
                    [("break", 5)],
                    4
                )
            ],
            3
        )

        errores = validar_break(arbol)

        self.assertEqual(errores, [])

    def test_break_dentro_de_if_sin_for(self):
        """Un if por sí solo no permite break."""
        arbol = (
            "if",
            ("booleano", "true", 2),
            [("break", 3)],
            None,
            2
        )

        errores = validar_break(arbol)

        self.assertEqual(len(errores), 1)
        self.assertEqual(errores[0]["linea"], 3)

    def test_break_dentro_de_if_con_for(self):
        """Un if dentro de for sí permite break."""
        arbol = (
            "for",
            None,
            None,
            None,
            [
                (
                    "if",
                    ("booleano", "true", 5),
                    [("break", 6)],
                    None,
                    5
                )
            ],
            3
        )

        errores = validar_break(arbol)

        self.assertEqual(errores, [])

    def test_break_despues_de_for(self):
        """El contexto del for no continúa fuera del ciclo."""
        arbol = [
            (
                "for",
                None,
                None,
                None,
                [("break", 4)],
                2
            ),
            ("break", 7)
        ]

        errores = validar_break(arbol)

        self.assertEqual(len(errores), 1)
        self.assertEqual(errores[0]["linea"], 7)

    def test_algoritmo3_real(self):
        """El algoritmo de Mora no debe generar errores de break."""
        ruta = RAIZ / "algoritmos" / "algoritmo3.go"
        codigo = ruta.read_text(encoding="utf-8")

        arbol, errores_sintacticos = analizar_sintactico(codigo)

        self.assertEqual(errores_sintacticos, [])
        self.assertIsNotNone(arbol)

        errores_semanticos = validar_break(arbol)

        self.assertEqual(errores_semanticos, [])

#Segundo bloque test pruebas de asignacion estricta de tipos de variables

class TestAsignacionMora(unittest.TestCase):
    """Pruebas de la regla de asignación estricta."""

    def setUp(self):
        # Simulación de respuestas de la tabla compartida.
        # NO es una segunda tabla de símbolos del proyecto.
        self.simbolos = {
            "edad": {"tipo": "int", "constante": False},
            "activo": {"tipo": "bool", "constante": False},
            "MAX": {"tipo": "int", "constante": True},
            "edades": {
                "tipo": "map[string]int",
                "constante": False
            },
        }

    def buscar(self, nombre, ambito):
        return self.simbolos.get(nombre)

    def tipo(self, expr, ambito):
        if expr is None:
            return None

        etiqueta = expr[0]

        tipos = {
            "entero": "int",
            "cadena": "string",
            "flotante": "float64",
            "booleano": "bool",
        }

        if etiqueta in tipos:
            return tipos[etiqueta]

        if etiqueta == "id":
            simbolo = self.buscar(expr[1], ambito)
            return simbolo["tipo"] if simbolo else None

        if etiqueta == "acceso":
            simbolo = self.buscar(expr[1], ambito)

            if simbolo and simbolo["tipo"] == "map[string]int":
                return "int"

        return None

    def validar(self, nodo):
        return validar_asignacion_mora(
            nodo,
            self.buscar,
            self.tipo,
            "main"
        )

    def test_declaracion_correcta(self):
        nodo = ("var", "x", "int", ("entero", 10, 3), 3)
        self.assertEqual(self.validar(nodo), [])

    def test_declaracion_tipo_incorrecto(self):
        nodo = (
            "var", "x", "int",
            ("cadena", '"hola"', 3), 3
        )
        errores = self.validar(nodo)
        self.assertEqual(len(errores), 1)
        self.assertIn("string", errores[0]["mensaje"])

    def test_asignacion_tipo_incorrecto(self):
        nodo = (
            "asignacion",
            ("id", "edad", 5),
            ("booleano", "true", 5),
            5
        )
        self.assertEqual(len(self.validar(nodo)), 1)

    def test_constante_valida(self):
        nodo = (
            "const", "MAX", "int",
            ("entero", 100, 3), 3
        )
        self.assertEqual(self.validar(nodo), [])

    def test_modificar_constante(self):
        nodo = (
            "asignacion",
            ("id", "MAX", 6),
            ("entero", 5, 6),
            6
        )
        errores = self.validar(nodo)
        self.assertEqual(len(errores), 1)
        self.assertIn("constante MAX", errores[0]["mensaje"])

    def test_modificar_constante_con_asignacion_compuesta(self):
        nodo = (
            "asig_comp", "+=",
            ("id", "MAX", 7),
            ("entero", 1, 7),
            7
        )
        self.assertEqual(len(self.validar(nodo)), 1)

    def test_incrementar_constante(self):
        nodo = (
            "inc_dec", "++",
            ("id", "MAX", 8),
            8
        )
        self.assertEqual(len(self.validar(nodo)), 1)

    def test_asignacion_valida_en_mapa(self):
        nodo = (
            "asignacion",
            ("acceso", "edades", ("cadena", '"Ana"', 9), 9),
            ("entero", 25, 9),
            9
        )
        self.assertEqual(self.validar(nodo), [])

    def test_asignacion_incorrecta_en_mapa(self):
        nodo = (
            "asignacion",
            ("acceso", "edades", ("cadena", '"Ana"', 9), 9),
            ("cadena", '"veinte"', 9),
            9
        )
        self.assertEqual(len(self.validar(nodo)), 1)

    def test_identificador_inexistente_no_duplica_error(self):
        nodo = (
            "asignacion",
            ("id", "desconocido", 10),
            ("entero", 5, 10),
            10
        )
        self.assertEqual(self.validar(nodo), [])

#Tercer bloque- Reglas AST Mora

class TestIntegracionASTAsignacionMora(unittest.TestCase):
    """Integración de las reglas de Mora con el AST real de PLY."""

    def obtener_sentencias(self, cuerpo):
        codigo = (
            'package main\n'
            'import "fmt"\n'
            'func main() {\n'
            f'{cuerpo}\n'
            '}\n'
        )

        arbol, errores = analizar_sintactico(codigo)

        self.assertEqual(errores, [])
        self.assertIsNotNone(arbol)

        funcion_main = next(
            f for f in arbol[3]
            if f[0] == "funcion" and f[1] == "main"
        )

        return funcion_main[4]

    @staticmethod
    def resolver_tipo(expr, ambito):
        """Stub temporal del resolvedor compartido."""
        tipos = {
            "entero": "int",
            "cadena": "string",
            "flotante": "float64",
            "booleano": "bool",
        }

        if isinstance(expr, tuple):
            return tipos.get(expr[0])

        return None

    def test_declaracion_incompatible_ast_real(self):
        sentencias = self.obtener_sentencias(
            'var edad int = "hola"'
        )

        errores = validar_asignacion_mora(
            sentencias[0],
            lambda nombre, ambito: None,
            self.resolver_tipo,
            "main"
        )

        self.assertEqual(len(errores), 1)
        self.assertIn("string", errores[0]["mensaje"])

    def test_modificacion_constante_ast_real(self):
        sentencias = self.obtener_sentencias(
            'const MAX int = 100\n'
            'MAX = 5'
        )

        def buscar_simbolo(nombre, ambito):
            if nombre == "MAX":
                return {
                    "tipo": "int",
                    "constante": True
                }
            return None

        errores = validar_asignacion_mora(
            sentencias[1],
            buscar_simbolo,
            self.resolver_tipo,
            "main"
        )

        self.assertEqual(len(errores), 1)
        self.assertIn("constante MAX", errores[0]["mensaje"])

    def test_asignacion_incompatible_ast_real(self):
        sentencias = self.obtener_sentencias(
            'var edad int = 20\n'
            'edad = "veinte"'
        )

        def buscar_simbolo(nombre, ambito):
            if nombre == "edad":
                return {
                    "tipo": "int",
                    "constante": False
                }
            return None

        errores = validar_asignacion_mora(
            sentencias[1],
            buscar_simbolo,
            self.resolver_tipo,
            "main"
        )

        self.assertEqual(len(errores), 1)
        self.assertIn("string", errores[0]["mensaje"])


    # FIN aporte: MORA (pruebas semánticas)


if __name__ == "__main__":
    unittest.main()
