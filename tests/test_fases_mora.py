
import unittest
from pathlib import Path

from generar_log_sintactico import analizar_completo


RAIZ = Path(__file__).resolve().parents[1]


class TestFasesMora(unittest.TestCase):

    def test_error_lexico_detiene_parser(self):
        resultado = analizar_completo("package main\n@\n")

        self.assertGreater(len(resultado["errores_lexicos"]), 0)
        self.assertFalse(resultado["sintactico_ejecutado"])
        self.assertIsNone(resultado["arbol"])

    def test_codigo_valido_ejecuta_parser(self):
        codigo = (RAIZ / "algoritmos" / "algoritmo3.go").read_text(
            encoding="utf-8"
        )
        resultado = analizar_completo(codigo)

        self.assertEqual(resultado["errores_lexicos"], [])
        self.assertTrue(resultado["sintactico_ejecutado"])
        self.assertIsNotNone(resultado["arbol"])
        self.assertEqual(resultado["errores_sintacticos"], [])

    def test_errores_sintacticos_sin_errores_lexicos(self):
        codigo = (
            RAIZ / "algoritmos" / "errores_sintacticos_mora.go"
        ).read_text(encoding="utf-8")

        resultado = analizar_completo(codigo)

        self.assertEqual(resultado["errores_lexicos"], [])
        self.assertTrue(resultado["sintactico_ejecutado"])
        self.assertEqual(len(resultado["errores_sintacticos"]), 6)

    def test_log_indica_fase_no_ejecutada(self):
        from datetime import datetime
        from generar_log_sintactico import construir_log_sintactico

        codigo = "package main\n@\n"
        resultado = analizar_completo(codigo)

        log = construir_log_sintactico(
            resultado,
            codigo,
            "prueba.go",
            "JosMoraE",
            datetime(2026, 11, 8, 17, 0),
        )

        self.assertIn("Resultado: NO EJECUTADO", log)
        self.assertIn("NO EVALUADOS", log)
        self.assertNotIn("ANALISIS SINTACTICO CORRECTO", log)

if __name__ == "__main__":
    unittest.main()
