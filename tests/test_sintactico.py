# -*- coding: utf-8 -*-
"""
Pruebas del análisis sintáctico y del formato de los logs.
- algoritmo1/2/3.go deben analizarse sin errores sintácticos.
- errores_*.go deben producir exactamente los errores sintácticos esperados (línea y token).
- Los logs se nombran sintactico-usuarioGit-ddmmaaaa-HHhMM.txt con el usuario de Git del dueño.
"""
import sys
import unittest
from datetime import datetime
from pathlib import Path

# Permite ejecutar este archivo directamente (Run Python File) además de con unittest
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import generar_log_sintactico as gls
from parser import analizar_sintactico

RAIZ = Path(__file__).resolve().parent.parent / "algoritmos"


def errores(nombre):
    return analizar_sintactico((RAIZ / nombre).read_text(encoding="utf-8"))[1]


def errores_de(codigo):
    """Errores sintácticos de un fragmento; agrega el encabezado package e import."""
    return analizar_sintactico('package main\nimport "fmt"\n' + codigo)[1]


class PruebasComunes:
    """Comprobaciones compartidas por la clase de cada integrante."""
    valido = None
    con_errores = None
    lineas_esperadas = None
    usuario = None

    def test_algoritmo_valido_sin_errores(self):
        self.assertEqual(errores(self.valido), [])

    def test_archivo_de_errores(self):
        encontrados = errores(self.con_errores)
        self.assertEqual([e["linea"] for e in encontrados], self.lineas_esperadas)
        self.assertTrue(all(e.get("token") for e in encontrados))

    def test_usuario_git_asignado(self):
        self.assertEqual(gls.usuario_git_de(self.valido), self.usuario)
        self.assertEqual(gls.usuario_git_de(self.con_errores), self.usuario)


# INICIO aporte: ANDRADE (pruebas sintácticas)
class TestSintacticoAndrade(PruebasComunes, unittest.TestCase):
    valido, con_errores, usuario = "algoritmo1.go", "errores_andrade.go", "marandradec"
    lineas_esperadas = [15, 20, 27, 32, 38, 47, 55]

    def test_arreglo_vacio(self):
        self.assertEqual(errores_de("func main() {\n\ta := [3]int{}\n}\n"), [])

    def test_arreglo_sin_cerrar_sigue_siendo_error(self):
        encontrados = errores_de("func main() {\n\ta := [3]int{1, 2\n}\n")
        self.assertEqual(len(encontrados), 1)
# FIN aporte: ANDRADE (pruebas sintácticas)


# INICIO aporte: BURGOS (pruebas sintácticas)
class TestSintacticoBurgos(PruebasComunes, unittest.TestCase):
    valido, con_errores, usuario = "algoritmo2.go", "errores_burgos.go", "TheFearLess"
    lineas_esperadas = [16, 21, 28, 33, 38]

    def test_funcion_con_retorno_sin_parametros(self):
        codigo = ("func uno() int {\n\treturn 1\n}\n"
                  "func nombre() string {\n\treturn \"Ana\"\n}\n"
                  "func main() {\n\tx := uno()\n\tfmt.Println(x, nombre())\n}\n")
        self.assertEqual(errores_de(codigo), [])

    def test_println_sin_argumentos(self):
        self.assertEqual(errores_de("func main() {\n\tfmt.Println()\n}\n"), [])

    def test_matriz_vacia(self):
        self.assertEqual(errores_de("func main() {\n\tm := [2][2]int{}\n}\n"), [])
# FIN aporte: BURGOS (pruebas sintácticas)


# INICIO aporte: MORA (pruebas sintácticas y formato de logs)
class TestSintacticoMora(PruebasComunes, unittest.TestCase):
    valido, con_errores, usuario = "algoritmo3.go", "errores_mora.go", "JosMoraE"
    lineas_esperadas = [17, 22, 27, 32, 39, 50]

    def test_mapa_vacio(self):
        self.assertEqual(errores_de("func main() {\n\tm := map[string]int{}\n\tm[\"a\"] = 1\n}\n"), [])


class TestNombreDeLogs(unittest.TestCase):
    def test_formato_del_nombre(self):
        ahora = datetime(2026, 10, 20, 23, 32)
        destino = gls._destino("marandradec", "algoritmo1.go", ahora)
        self.assertRegex(destino.name, r"^sintactico-marandradec-20102026-23h32(-\d+)?\.txt$")
        self.assertEqual(destino.parent, gls.CARPETA_LOGS)

    def test_usuarios_validos(self):
        for usuario in ("marandradec", "TheFearLess", "JosMoraE"):
            self.assertTrue(gls.usuario_git_valido(usuario))
        for usuario in ("", "con espacio", "tilde-é", None):
            self.assertFalse(gls.usuario_git_valido(usuario))
# FIN aporte: MORA (pruebas sintácticas y formato de logs)


if __name__ == "__main__":
    unittest.main()