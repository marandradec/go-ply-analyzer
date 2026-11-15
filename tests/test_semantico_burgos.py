# -*- coding: utf-8 -*-
"""
test_semantico_burgos.py - Pruebas unitarias para las reglas semánticas de Burgos (Avance 3)
"""

import unittest
from semantico_burgos import validar_operacion_burgos, validar_retorno_burgos


# INICIO aporte: BURGOS (pruebas unitarias semánticas)

def tipo_expresion_simulado(expr, ambito="main"):
    """
    Simula la función compartida tipo_expresion(expresion, ambito)
    para probar las reglas de Burgos de forma aislada.
    """
    if not isinstance(expr, tuple) or not expr:
        return None

    etiqueta = expr[0]
    if etiqueta == "entero":
        return "int"
    if etiqueta == "flotante":
        return "float64"
    if etiqueta == "cadena":
        return "string"
    if etiqueta == "booleano":
        return "bool"
    if etiqueta == "id":
        tabla_mock = {
            "edad": "int",
            "precio": "float64",
            "nombre": "string",
            "activo": "bool",
        }
        return tabla_mock.get(expr[1])
    return None


class TestSemanticoBurgos(unittest.TestCase):

    # --- Pruebas Regla 1: Operaciones permitidas ---

    def test_operaciones_aritmeticas_validas(self):
        # int + int
        nodo_int = ("binop", "+", ("entero", 10), ("id", "edad"), 5)
        self.assertEqual(validar_operacion_burgos(nodo_int, tipo_expresion_simulado, "main"), [])

        # float64 * float64
        nodo_float = ("binop", "*", ("flotante", 2.5), ("id", "precio"), 6)
        self.assertEqual(validar_operacion_burgos(nodo_float, tipo_expresion_simulado, "main"), [])

        # string + string (concatenación permitida)
        nodo_str = ("binop", "+", ("cadena", "Hola "), ("id", "nombre"), 7)
        self.assertEqual(validar_operacion_burgos(nodo_str, tipo_expresion_simulado, "main"), [])

        # int % int
        nodo_mod = ("binop", "%", ("entero", 17), ("entero", 5), 8)
        self.assertEqual(validar_operacion_burgos(nodo_mod, tipo_expresion_simulado, "main"), [])

    def test_error_mezcla_cadena_y_numero(self):
        # total := "hola" + 5
        nodo_error = ("binop", "+", ("cadena", "hola"), ("entero", 5), 10)
        errores = validar_operacion_burgos(nodo_error, tipo_expresion_simulado, "main")
        self.assertEqual(len(errores), 1)
        self.assertEqual(errores[0]["categoria"], "Operaciones permitidas")
        self.assertEqual(errores[0]["linea"], 10)

    def test_error_mezcla_int_y_float(self):
        # mezcla := edad + precio
        nodo_error = ("binop", "+", ("id", "edad"), ("id", "precio"), 11)
        errores = validar_operacion_burgos(nodo_error, tipo_expresion_simulado, "main")
        self.assertEqual(len(errores), 1)
        self.assertIn("int y float64", errores[0]["mensaje"])

    def test_error_modulo_con_flotante(self):
        # resto := 10.5 % 2
        nodo_error = ("binop", "%", ("flotante", 10.5), ("entero", 2), 12)
        errores = validar_operacion_burgos(nodo_error, tipo_expresion_simulado, "main")
        self.assertEqual(len(errores), 1)
        self.assertIn("'%'", errores[0]["mensaje"])

    def test_error_incremento_en_cadena(self):
        # nombre++
        nodo_error = ("inc_dec", "++", ("id", "nombre"), 13)
        errores = validar_operacion_burgos(nodo_error, tipo_expresion_simulado, "main")
        self.assertEqual(len(errores), 1)
        self.assertEqual(errores[0]["linea"], 13)

    # --- Pruebas Regla 2: Retorno de funciones ---

    def test_retorno_funcion_valido(self):
        # func sumar() int { return 10 }
        nodo_func = (
            "funcion",
            "sumar",
            [],
            "int",
            [("return", ("entero", 10), 16)],
            15,
        )
        self.assertEqual(validar_retorno_burgos(nodo_func, tipo_expresion_simulado), [])

    def test_error_retorno_tipo_incompatible(self):
        # func f() int { return "a" }
        nodo_func = (
            "funcion",
            "f",
            [],
            "int",
            [("return", ("cadena", "a"), 21)],
            20,
        )
        errores = validar_retorno_burgos(nodo_func, tipo_expresion_simulado)
        self.assertEqual(len(errores), 1)
        self.assertEqual(errores[0]["categoria"], "Retorno de funciones")
        self.assertEqual(errores[0]["linea"], 21)

    def test_error_funcion_sin_return(self):
        # func calcular() float64 { x := 3.14 } (falta return)
        nodo_func = (
            "funcion",
            "calcular",
            [],
            "float64",
            [("decl_corta", "x", ("flotante", 3.14), 26)],
            25,
        )
        errores = validar_retorno_burgos(nodo_func, tipo_expresion_simulado)
        self.assertEqual(len(errores), 1)
        self.assertEqual(errores[0]["linea"], 25)
        self.assertIn("no incluye ninguna sentencia return", errores[0]["mensaje"])

    def test_error_retorno_en_funcion_void(self):
        # func saludar() { return 1 }
        nodo_func = (
            "funcion",
            "saludar",
            [],
            None,
            [("return", ("entero", 1), 31)],
            30,
        )
        errores = validar_retorno_burgos(nodo_func, tipo_expresion_simulado)
        self.assertEqual(len(errores), 1)
        self.assertEqual(errores[0]["linea"], 31)


# FIN aporte: BURGOS (pruebas unitarias semánticas)

if __name__ == "__main__":
    unittest.main()