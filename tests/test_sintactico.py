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













































if __name__ == "__main__":
    unittest.main()