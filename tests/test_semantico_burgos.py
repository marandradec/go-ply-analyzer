# -*- coding: utf-8 -*-
"""
test_semantico_burgos.py - Pruebas unitarias de las reglas semánticas de Burgos (Avance 3)

Reglas evaluadas:
1. Operaciones permitidas (operandos compatibles en +, -, *, /, %, comparaciones y lógica).
2. Retorno de funciones (coherencia de tipo en return, presencia de return y llamadas void).
"""

import os
import unittest

from semantic import analizar_completo_semantico, analizar_semantico


# INICIO aporte: BURGOS (pruebas unitarias semánticas)

def I(n, l=1): return ("id", n, l)
def N(v, l=1): return ("entero", v, l)
def F(v, l=1): return ("flotante", v, l)
def C(v, l=1): return ("cadena", v, l)
def B(v, l=1): return ("booleano", v, l)
def DC(n, v, l): return ("decl_corta", n, v, l)
def VAR(n, t, v, l): return ("var", n, t, v, l)
def BIN(op, a, b, l): return ("binop", op, a, b, l)
def CALL(n, a, l): return ("llamada", n, a, l)
def FN(n, params, ret, cuerpo, l): return ("funcion", n, params, ret, cuerpo, l)
def RET(v, l): return ("return", v, l)


def main(cuerpo):
    return FN("main", [], None, cuerpo, 1)


def analizar(*funciones):
    return analizar_semantico(("programa", "main", ("import", "fmt"), list(funciones)))


class TestSemanticoBurgos(unittest.TestCase):

    def esperar(self, esperados, *funciones):
        _, errores = analizar(*funciones)
        self.assertEqual(len(errores), esperados, [e["mensaje"] for e in errores])
        return errores

    # ---- Regla 1: Operaciones permitidas (casos válidos)
    def test_aritmetica_enteros_y_flotantes_validos(self):
        self.esperar(0, main([
            DC("a", BIN("+", N(4, 2), N(2, 2), 2), 2),
            DC("b", BIN("%", N(10, 3), N(3, 3), 3), 3),
            DC("c", BIN("*", F(2.5, 4), F(4.0, 4), 4), 4),
            DC("d", BIN("/", F(9.0, 5), F(3.0, 5), 5), 5),
        ]))

    def test_concatenacion_cadenas_valida(self):
        self.esperar(0, main([
            DC("saludo", BIN("+", C("Hola ", 2), C("Go", 2), 2), 2),
        ]))

    def test_comparaciones_validas(self):
        self.esperar(0, main([
            DC("c1", BIN("<", N(3, 2), N(5, 2), 2), 2),
            DC("c2", BIN(">=", F(4.5, 3), F(2.0, 3), 3), 3),
            DC("c3", BIN("==", C("a", 4), C("b", 4), 4), 4),
        ]))

    # ---- Regla 1: Operaciones permitidas (errores esperados)
    def test_error_mezcla_int_y_float64(self):
        self.esperar(1, main([
            DC("x", BIN("+", N(5, 2), F(2.5, 2), 2), 2),
        ]))

    def test_error_mezcla_cadena_y_numero(self):
        self.esperar(1, main([
            DC("x", BIN("+", C("hola", 2), N(5, 2), 2), 2),
        ]))

    def test_error_resta_o_multiplicacion_con_cadenas(self):
        self.esperar(1, main([
            DC("x", BIN("-", C("hola", 2), C("a", 2), 2), 2),
        ]))

    def test_error_modulo_con_flotantes(self):
        self.esperar(1, main([
            DC("x", BIN("%", F(10.5, 2), F(3.0, 2), 2), 2),
        ]))

    def test_error_comparacion_tipos_incompatibles(self):
        self.esperar(1, main([
            DC("ok", BIN("<", N(10, 2), C("20", 2), 2), 2),
        ]))

    # ---- Regla 2: Retorno de funciones (casos válidos)
    def test_funcion_con_retorno_coherente(self):
        fn_sumar = FN("sumar", [("a", "int"), ("b", "int")], "int", [
            RET(BIN("+", I("a", 2), I("b", 2), 2), 2)
        ], 1)
        self.esperar(0, fn_sumar, main([
            DC("r", CALL("sumar", [N(2, 5), N(3, 5)], 5), 5)
        ]))

    # ---- Regla 2: Retorno de funciones (errores esperados)
    def test_error_tipo_retorno_incompatible(self):
        fn_mala = FN("obtenerNumero", [], "int", [
            RET(C("no soy int", 2), 2)
        ], 1)
        self.esperar(1, fn_mala, main([]))

    def test_error_funcion_sin_sentencia_return(self):
        fn_incompleta = FN("calcular", [("x", "int")], "float64", [
            DC("y", BIN("*", I("x", 2), N(2, 2), 2), 2)
        ], 1)
        self.esperar(1, fn_incompleta, main([]))

    def test_error_uso_funcion_void_en_expresion(self):
        fn_void = FN("avisar", [], None, [], 1)
        self.esperar(1, fn_void, main([
            DC("x", CALL("avisar", [], 3), 3)
        ]))

    # ---- Integración con archivos de prueba del proyecto
    def test_algoritmo2_sin_errores_semanticos(self):
        ruta = os.path.join(os.path.dirname(__file__), "..", "algoritmos", "algoritmo2.go")
        if os.path.exists(ruta):
            with open(ruta, encoding="utf-8") as f:
                res = analizar_completo_semantico(f.read())
            self.assertEqual(res["errores_lexicos"], [])
            self.assertEqual(res["errores_sintacticos"], [])
            self.assertEqual(res["errores_semanticos"], [])

    def test_errores_semantico_burgos_detecta_fallos(self):
        ruta = os.path.join(os.path.dirname(__file__), "..", "algoritmos", "errores_semantico_burgos.go")
        if os.path.exists(ruta):
            with open(ruta, encoding="utf-8") as f:
                res = analizar_completo_semantico(f.read())
            self.assertEqual(res["errores_lexicos"], [])
            self.assertEqual(res["errores_sintacticos"], [])
            self.assertGreater(len(res["errores_semanticos"]), 0)


# FIN aporte: BURGOS (pruebas unitarias semánticas)

if __name__ == "__main__":
    unittest.main()
