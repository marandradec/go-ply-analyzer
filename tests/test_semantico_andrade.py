# -*- coding: utf-8 -*-
"""
test_semantico_andrade.py - Pruebas unitarias de las reglas semánticas de Andrade (Avance 3)

Identificadores: Inexistencia y Duplicidad, para todas las formas de variable del subconjunto
de Go (var, :=, const, parámetros, arreglos, matrices, mapas, bloques, for, switch, _).
Los árboles se arman a mano con la misma forma que produce parser.py, así que estas pruebas
no dependen de PLY.
"""

import unittest

from semantic import analizar_semantico


# INICIO aporte: ANDRADE (pruebas unitarias semánticas)

def I(n, l=1): return ("id", n, l)
def N(v, l=1): return ("entero", v, l)
def F(v, l=1): return ("flotante", v, l)
def C(v, l=1): return ("cadena", v, l)
def B(v, l=1): return ("booleano", v, l)
def DC(n, v, l): return ("decl_corta", n, v, l)
def VAR(n, t, v, l): return ("var", n, t, v, l)
def CONST(n, t, v, l): return ("const", n, t, v, l)
def ASG(d, v, l): return ("asignacion", d, v, l)
def ACC(b, i, l): return ("acceso", b, i, l)
def BIN(op, a, b, l): return ("binop", op, a, b, l)
def CALL(n, a, l): return ("llamada", n, a, l)
def FN(n, params, ret, cuerpo, l): return ("funcion", n, params, ret, cuerpo, l)
def IF(c, b, r, l): return ("if", c, b, r, l)
def FOR(i, c, p, b, l): return ("for", i, c, p, b, l)
def INC(d, l): return ("inc_dec", "++", d, l)


def main(cuerpo):
    return FN("main", [], None, cuerpo, 1)


def analizar(*funciones):
    return analizar_semantico(("programa", "main", ("import", "fmt"), list(funciones)))


class TestIdentificadoresAndrade(unittest.TestCase):

    def esperar(self, esperados, *funciones, regla=None):
        _, errores = analizar(*funciones)
        self.assertEqual(len(errores), esperados, [e["mensaje"] for e in errores])
        if regla:
            self.assertTrue(all(e["regla"] == regla for e in errores))

    # ---- Formas de declarar que deben aceptarse
    def test_var_con_y_sin_valor(self):
        self.esperar(0, main([VAR("x", "int", None, 2), ASG(I("x", 3), N(1, 3), 3),
                              VAR("y", "int", N(1, 4), 4)]))

    def test_var_de_todos_los_tipos(self):
        self.esperar(0, main([VAR("a", "string", C("s", 2), 2), VAR("b", "bool", B(True, 3), 3),
                              VAR("c", "float64", F(1.5, 4), 4)]))

    def test_declaracion_corta_y_reasignacion(self):
        self.esperar(0, main([DC("x", N(1, 2), 2), ASG(I("x", 3), N(2, 3), 3)]))

    def test_constante_y_uso(self):
        self.esperar(0, main([CONST("M", "int", N(1, 2), 2), DC("y", BIN("+", I("M", 3), N(1, 3), 3), 3)]))

    def test_arreglo_matriz_y_mapa(self):
        self.esperar(0, main([
            VAR("a", "[3]int", None, 2), ASG(ACC("a", N(0, 3), 3), N(1, 3), 3),
            VAR("m", "[2][2]int", None, 4), ASG(ACC(ACC("m", N(0, 5), 5), N(1, 5), 5), N(1, 5), 5),
            VAR("d", "map[string]int", None, 6), ASG(ACC("d", C("k", 7), 7), N(1, 7), 7)]))

    def test_parametro_usado(self):
        self.esperar(0, FN("f", [("a", "int")], "int", [("return", I("a", 2), 2)], 1), main([]))

    def test_funcion_usada_antes_de_declararse(self):
        self.esperar(0, main([CALL("g", [], 2)]), FN("g", [], None, [], 5))

    def test_recursion(self):
        self.esperar(0, FN("f", [("n", "int")], "int", [("return", CALL("f", [I("n", 2)], 2), 2)], 1), main([]))

    # ---- Ámbitos: el mismo nombre en bloques distintos o tapado es válido
    def test_sombra_en_bloque_interno(self):
        self.esperar(0, main([DC("x", N(1, 2), 2), IF(B(True, 3), [DC("x", C("a", 4), 4)], None, 3)]))

    def test_sombra_de_parametro_en_bloque(self):
        self.esperar(0, FN("f", [("a", "int")], None, [IF(B(True, 2), [DC("a", C("s", 3), 3)], None, 2)], 1), main([]))

    def test_inicializador_ve_la_variable_externa(self):
        self.esperar(0, main([DC("x", N(1, 2), 2), IF(B(True, 3), [DC("x", BIN("+", I("x", 4), N(1, 4), 4), 4)], None, 3)]))

    def test_dos_for_con_la_misma_variable(self):
        def ciclo(l):
            return FOR(DC("i", N(0, l), l), BIN("<", I("i", l), N(3, l), l), INC(I("i", l), l), [], l)
        self.esperar(0, main([ciclo(2), ciclo(3)]))

    def test_cuerpo_del_for_puede_tapar_la_variable_del_for(self):
        self.esperar(0, main([FOR(DC("i", N(0, 2), 2), BIN("<", I("i", 2), N(3, 2), 2), INC(I("i", 2), 2),
                                  [DC("i", N(5, 3), 3)], 2)]))

    def test_cada_case_tiene_su_ambito(self):
        self.esperar(0, main([DC("n", N(1, 2), 2), ("switch", I("n", 3), [
            ("case", [N(1, 4)], [DC("a", N(1, 5), 5)], 4),
            ("case", [N(2, 6)], [DC("a", N(2, 7), 7)], 6),
            ("default", [DC("a", N(3, 9), 9)], 8)], 3)]))

    def test_cada_rama_del_else_if_tiene_su_ambito(self):
        self.esperar(0, main([IF(B(True, 2), [DC("a", N(1, 3), 3)],
                                 IF(B(True, 4), [DC("a", N(2, 5), 5)], [DC("a", N(3, 7), 7)], 4), 2)]))

    def test_variable_con_nombre_de_funcion(self):
        self.esperar(0, FN("saludar", [], None, [], 1), main([DC("saludar", N(1, 3), 3), DC("t", I("saludar", 4), 4)]))

    # ---- Inexistencia
    def test_uso_sin_declarar(self):
        self.esperar(1, main([ASG(I("y", 2), N(1, 2), 2)]), regla="Inexistencia")

    def test_uso_antes_de_declarar(self):
        self.esperar(1, main([DC("y", BIN("+", I("x", 2), N(1, 2), 2), 2), DC("x", N(2, 3), 3)]), regla="Inexistencia")

    def test_variable_de_bloque_no_existe_afuera(self):
        self.esperar(1, main([IF(B(True, 2), [DC("a", N(1, 3), 3)], None, 2), ASG(I("a", 5), N(2, 5), 5)]), regla="Inexistencia")

    def test_variable_del_for_no_existe_afuera(self):
        self.esperar(1, main([FOR(DC("i", N(0, 2), 2), BIN("<", I("i", 2), N(3, 2), 2), INC(I("i", 2), 2), [], 2),
                              ASG(I("i", 3), N(1, 3), 3)]), regla="Inexistencia")

    def test_variable_de_un_case_no_existe_en_otro(self):
        self.esperar(1, main([DC("n", N(1, 2), 2), ("switch", I("n", 3), [
            ("case", [N(1, 4)], [DC("a", N(1, 5), 5)], 4),
            ("case", [N(2, 6)], [ASG(I("a", 7), N(2, 7), 7)], 6)], 3)]), regla="Inexistencia")

    def test_variable_en_su_propio_inicializador(self):
        self.esperar(1, main([VAR("x", "int", I("x", 2), 2)]), regla="Inexistencia")
        self.esperar(1, main([DC("x", I("x", 2), 2)]), regla="Inexistencia")

    def test_cada_lugar_donde_se_usa_una_variable(self):
        usos = {
            "inc_dec": [INC(I("z", 2), 2)],
            "asig_comp": [("asig_comp", "+=", I("z", 2), N(1, 2), 2)],
            "Scanln": [("leer", "z", 2)],
            "condición if": [IF(I("z", 2), [], None, 2)],
            "condición for": [FOR(None, I("z", 2), None, [], 2)],
            "switch": [("switch", I("z", 2), [], 2)],
            "print": [("imprimir", [I("z", 2)], 2)],
            "índice": [VAR("a", "[3]int", None, 1), DC("v", ACC("a", I("z", 2), 2), 2)],
            "arreglo": [ASG(ACC("z", N(0, 2), 2), N(1, 2), 2)],
            "literal de arreglo": [DC("a", ("arreglo", "[2]int", [I("z", 2), N(1, 2)], 2), 2)],
            "literal de mapa": [DC("m", ("mapa", "map[string]int", [(C("a", 2), I("z", 2))], 2), 2)],
            "signo -": [DC("a", ("neg", I("z", 2), 2), 2)],
            "!": [DC("a", ("not", I("z", 2), 2), 2)],
        }
        for nombre, cuerpo in usos.items():
            with self.subTest(uso=nombre):
                self.esperar(1, main(cuerpo), regla="Inexistencia")

    def test_variable_sin_declarar_en_return_y_argumento(self):
        self.esperar(1, FN("f", [], "int", [("return", I("z", 2), 2)], 1), main([]))
        self.esperar(1, FN("f", [("a", "int")], None, [], 1), main([CALL("f", [I("z", 3)], 3)]))

    def test_funcion_sin_declarar_y_variable_usada_como_funcion(self):
        self.esperar(1, main([CALL("nada", [], 2)]), regla="Inexistencia")
        self.esperar(1, main([DC("c", N(1, 2), 2), CALL("c", [], 3)]), regla="Inexistencia")

    def test_funcion_usada_como_variable(self):
        self.esperar(1, FN("f", [], None, [], 1), main([DC("r", I("f", 3), 3)]), regla="Inexistencia")
        self.esperar(1, FN("f", [], None, [], 1), main([ASG(I("f", 3), N(1, 3), 3)]), regla="Inexistencia")

    def test_variable_local_tapa_a_la_funcion(self):
        self.esperar(1, FN("s", [], None, [], 1), main([DC("s", N(1, 3), 3), CALL("s", [], 4)]), regla="Inexistencia")

    # ---- Duplicidad
    def test_duplicidad_en_todas_las_combinaciones(self):
        casos = {
            "var y var": [VAR("x", "int", N(1, 2), 2), VAR("x", "string", C("a", 3), 3)],
            ":= y :=": [DC("a", N(1, 2), 2), DC("a", N(2, 3), 3)],
            "var y :=": [VAR("a", "int", N(1, 2), 2), DC("a", N(2, 3), 3)],
            ":= y var": [DC("a", N(1, 2), 2), VAR("a", "int", N(2, 3), 3)],
            "const y var": [CONST("a", "int", N(1, 2), 2), VAR("a", "int", N(2, 3), 3)],
            "const y const": [CONST("a", "int", N(1, 2), 2), CONST("a", "int", N(2, 3), 3)],
        }
        for nombre, cuerpo in casos.items():
            with self.subTest(caso=nombre):
                self.esperar(1, main(cuerpo), regla="Duplicidad")

    def test_duplicidad_de_parametros_y_locales(self):
        self.esperar(1, FN("f", [("a", "int"), ("a", "int")], None, [], 1), main([]), regla="Duplicidad")
        self.esperar(1, FN("f", [("a", "int")], None, [VAR("a", "int", N(1, 2), 2)], 1), main([]), regla="Duplicidad")

    def test_funcion_declarada_dos_veces(self):
        self.esperar(1, FN("r", [], None, [], 1), FN("r", [], None, [], 3), main([]), regla="Duplicidad")

    # ---- Identificador en blanco _
    def test_blanco_como_destino(self):
        self.esperar(0, main([DC("x", N(1, 2), 2), ASG(I("_", 3), I("x", 3), 3)]))

    def test_blanco_se_puede_repetir_y_no_entra_en_la_tabla(self):
        tabla, errores = analizar(FN("f", [("_", "int"), ("_", "int")], None, [], 1),
                                  FN("_", [], None, [], 2), FN("_", [], None, [], 3),
                                  main([VAR("_", "int", N(1, 5), 5), VAR("_", "int", N(2, 6), 6),
                                        CONST("_", "int", N(3, 7), 7)]))
        self.assertEqual(errores, [])
        self.assertFalse([f for f in tabla.filas() if f[1] == "_"])

    def test_blanco_no_es_un_valor(self):
        casos = {
            "y := _": [DC("y", I("_", 2), 2)],
            "_ += 1": [("asig_comp", "+=", I("_", 2), N(1, 2), 2)],
            "_++": [INC(I("_", 2), 2)],
            "Scanln": [("leer", "_", 2)],
        }
        for nombre, cuerpo in casos.items():
            with self.subTest(caso=nombre):
                self.esperar(1, main(cuerpo), regla="Inexistencia")

    def test_blanco_no_declara_con_dos_puntos_igual(self):
        self.esperar(1, main([DC("_", N(1, 2), 2)]), regla="Duplicidad")

    # ---- Constantes: solo se inicializan con valores constantes
    def test_constante_con_literales_y_constantes(self):
        self.esperar(0, main([CONST("A", "int", N(1, 2), 2), CONST("B", "int", BIN("*", I("A", 3), N(2, 3), 3), 3),
                              CONST("S", "string", BIN("+", C("a", 4), C("b", 4), 4), 4)]))

    def test_constante_con_valor_no_constante(self):
        casos = {
            "variable": [DC("x", N(1, 2), 2), CONST("C", "int", I("x", 3), 3)],
            "variable en operación": [DC("x", N(1, 2), 2), CONST("C", "int", BIN("+", N(1, 3), I("x", 3), 3), 3)],
            "llamada": [CONST("C", "int", CALL("f", [], 3), 3)],
            "elemento": [VAR("a", "[2]int", None, 2), CONST("C", "int", ACC("a", N(0, 3), 3), 3)],
        }
        for nombre, cuerpo in casos.items():
            with self.subTest(caso=nombre):
                self.esperar(1, FN("f", [], "int", [("return", N(1, 1), 1)], 1), main(cuerpo))

    def test_constante_con_identificador_sin_declarar_da_un_solo_error(self):
        self.esperar(1, main([CONST("C", "int", I("zz", 2), 2)]), regla="Inexistencia")


# FIN aporte: ANDRADE (pruebas unitarias semánticas)

if __name__ == "__main__":
    unittest.main()