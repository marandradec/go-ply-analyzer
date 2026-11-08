# -*- coding: utf-8 -*-
"""
generar_log_sintactico.py - Logs del análisis léxico + sintáctico (Avance 2)

Uso:
  py generar_log_sintactico.py archivo.go usuarioGit
  py generar_log_sintactico.py algoritmos/algoritmo1.go marandradec
"""
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

import parser as parser_go
from generar_log import CARPETA_LOGS, _valor
from lexer import analizar

# Logs del análisis sintáctico
RAIZ = Path(__file__).resolve().parent
CARPETA_ALGORITMOS = RAIZ / "algoritmos"

# Usuario de Git responsable de cada archivo de prueba (se usa para nombrar el log)
USUARIOS_GIT = {
    "algoritmo1": "marandradec", "errores_andrade": "marandradec",   # Andrade
    "algoritmo2": "TheFearLess", "errores_burgos": "TheFearLess",    # Burgos
    "algoritmo3": "JosMoraE", "errores_mora": "JosMoraE",            # Mora
}
PATRON_USUARIO_GIT = r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?"

# Archivos de prueba del Avance 2 (en el orden en que se generan los logs)
ARCHIVOS_PRUEBA = [(f"{base}.go", usuario) for base, usuario in USUARIOS_GIT.items()]


def usuario_git_de(archivo):
    """Usuario de Git del dueño del archivo de prueba, o None si el archivo no es uno de los seis."""
    return USUARIOS_GIT.get(Path(archivo).stem)


def usuario_git_valido(usuario):
    return bool(usuario) and re.fullmatch(PATRON_USUARIO_GIT, usuario) is not None

# Nodos del árbol que representan sentencias (para el resumen de aciertos)
_SENTENCIAS = {
    "decl_corta": "declaraciones cortas (:=)", "asignacion": "asignaciones",
    "asig_comp": "asignaciones compuestas", "inc_dec": "incrementos y decrementos",
    "var": "declaraciones var", "const": "declaraciones const",
    "imprimir": "impresiones (fmt.Println)", "leer": "lecturas (fmt.Scanln)",
    "return": "return", "break": "break", "if": "if", "for": "for", "switch": "switch",
    "case": "case", "default": "default",
}


# ANÁLISIS COMBINADO
def analizar_completo(codigo):
    """Ejecuta léxico y sintáctico sobre el mismo código y devuelve un diccionario."""
    tokens, errores_lexicos = analizar(codigo)
    arbol, errores = parser_go.analizar_sintactico(codigo)
    return {
        "tokens": tokens,
        "errores_lexicos": errores_lexicos,
        "arbol": arbol,
        # con error grave el árbol no se devuelve, pero las funciones completas sí se conservan
        "funciones": arbol[3] if arbol else list(parser_go.funciones_reconocidas),
        "errores_sintacticos": errores,
        # errores de líneas que ya tienen un error léxico (consecuencia del token descartado)
        "omitidos": len(parser_go.errores_sintacticos) - len(errores),
    }


def _contar_nodos(nodo, cuenta):
    if isinstance(nodo, tuple):
        if nodo and isinstance(nodo[0], str) and nodo[0] in _SENTENCIAS:
            cuenta[nodo[0]] += 1
        for hijo in nodo:
            _contar_nodos(hijo, cuenta)
    elif isinstance(nodo, list):
        for hijo in nodo:
            _contar_nodos(hijo, cuenta)


def resumir_arbol(nodos_funcion):
    """Devuelve (lista de funciones, Counter de sentencias) a partir de los nodos func de PLY."""
    funciones = [(f[1], f[5], len(f[4])) for f in nodos_funcion]  # nombre, línea, nº de sentencias
    cuenta = Counter()
    _contar_nodos(nodos_funcion, cuenta)
    return funciones, cuenta


# CONSTRUCCIÓN DEL LOG
def construir_log_sintactico(resultado, codigo, archivo, autor, ahora):
    tokens = resultado["tokens"]
    err_lex = resultado["errores_lexicos"]
    err_sin = resultado["errores_sintacticos"]
    lineas_codigo = codigo.splitlines()

    lineas = [
        f"ANALISIS LEXICO Y SINTACTICO - usuario Git: {autor}",
        f"Archivo: {archivo}",
        f"Fecha: {ahora:%d-%m-%Y %H:%M:%S}",
        "",
        "FASE 1. ANALISIS LEXICO",
        "=" * 60,
        "TOKENS RECONOCIDOS",
        "-" * 60,
    ]
    for tipo, valor, linea in tokens:
        lineas.append(f"Linea {linea:03d} | {tipo:20s} | {_valor(tipo, valor)}")
    lineas += ["", f"Total de tokens: {len(tokens)}", "", "RESUMEN POR TIPO DE TOKEN", "-" * 60]
    for tipo, cantidad in sorted(Counter(t[0] for t in tokens).items()):
        lineas.append(f"{tipo:20s} | {cantidad}")
    lineas += ["", "ERRORES LEXICOS", "-" * 60]
    lineas += [e["mensaje"] for e in err_lex] or ["No se encontraron errores lexicos."]
    lineas += ["", f"Total de errores lexicos: {len(err_lex)}", ""]

    lineas += ["FASE 2. ANALISIS SINTACTICO", "=" * 60]
    correcto = not err_sin
    lineas.append("Resultado: " + ("ANALISIS SINTACTICO CORRECTO" if correcto
                                   else f"SE ENCONTRARON {len(err_sin)} ERROR(ES) SINTACTICO(S)"))
    if err_lex:
        lineas.append("Nota: el archivo tiene errores lexicos; los errores sintacticos de esas "
                      f"mismas lineas se omiten ({resultado['omitidos']} omitido(s)).")

    funciones, cuenta = resumir_arbol(resultado["funciones"])
    lineas += ["", "ESTRUCTURA RECONOCIDA (aciertos)", "-" * 60]
    if funciones:
        lineas.append("Programa: package y import fmt reconocidos")
        if resultado["arbol"] is None:
            lineas.append("Arbol incompleto: solo se listan las funciones completas anteriores al error grave.")
        for nombre, linea, n in funciones:
            lineas.append(f"Linea {linea:03d} | func {nombre} | {n} sentencia(s) en su bloque")
        lineas.append("")
        for clave, etiqueta in _SENTENCIAS.items():
            if cuenta[clave]:
                lineas.append(f"{etiqueta:34s} | {cuenta[clave]}")
    else:
        lineas.append("No se reconocio ninguna funcion completa (revisar package, import y la primera funcion).")

    lineas += ["", "ERRORES SINTACTICOS", "-" * 60]
    if err_sin:
        for e in err_sin:
            lineas.append(f"Linea {e['linea']:03d} | Token: {e.get('token') or '-'}")
            lineas.append(f"    {e['mensaje']}")
            if 1 <= e["linea"] <= len(lineas_codigo):
                lineas.append(f"    Codigo: {lineas_codigo[e['linea'] - 1].strip()}")
    else:
        lineas.append("No se encontraron errores sintacticos.")
    lineas += ["", f"Total de errores sintacticos: {len(err_sin)}", "",
               "RESUMEN FINAL", "=" * 60,
               f"Tokens reconocidos        | {len(tokens)}",
               f"Errores lexicos           | {len(err_lex)}",
               f"Errores sintacticos       | {len(err_sin)}"]
    return "\n".join(lineas) + "\n"


def _destino(autor, archivo, ahora):
    CARPETA_LOGS.mkdir(exist_ok=True)
    base = f"sintactico-{autor}-{ahora:%d%m%Y-%Hh%M}"
    destino = CARPETA_LOGS / f"{base}.txt"
    n = 2
    while destino.exists():  # mismo usuario y minuto (ej. algoritmo1 y errores_andrade): -2, -3 ...
        destino = CARPETA_LOGS / f"{base}-{n}.txt"
        n += 1
    return destino


def guardar_log_sintactico(codigo, archivo, autor):
    """Analiza y guarda el log. Devuelve (ruta del log, resultado del análisis)."""
    resultado = analizar_completo(codigo)
    ahora = datetime.now()
    destino = _destino(autor, archivo, ahora)
    destino.write_text(construir_log_sintactico(resultado, codigo, archivo, autor, ahora),
                       encoding="utf-8")
    return destino, resultado


def generar_logs_de_prueba():
    """Genera el log de los seis archivos de prueba y devuelve un resumen por archivo."""
    resumen = []
    for nombre, autor in ARCHIVOS_PRUEBA:
        ruta = CARPETA_ALGORITMOS / nombre
        if not ruta.is_file():
            print(f"No existe el archivo: {ruta}")
            continue
        destino, res = guardar_log_sintactico(ruta.read_text(encoding="utf-8"), f"algoritmos/{nombre}", autor)
        resumen.append((nombre, len(res["tokens"]), len(res["errores_lexicos"]),
                        len(res["errores_sintacticos"]), destino))
    return resumen


def _imprimir_resumen(resumen):
    print(f"{'Archivo':20s} {'Tokens':>7s} {'Err.lex':>8s} {'Err.sint':>9s}  Log")
    for nombre, tokens, lex, sint, destino in resumen:
        print(f"{nombre:20s} {tokens:7d} {lex:8d} {sint:9d}  {destino.name}")



if __name__ == "__main__":
    ruta = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    usuario = sys.argv[2] if len(sys.argv) > 2 else (usuario_git_de(ruta) if ruta else None)
    if ruta is None or len(sys.argv) > 3 or not usuario_git_valido(usuario):
        print("Uso: py generar_log_sintactico.py archivo.go usuarioGit")
        print("Ejemplo: py generar_log_sintactico.py algoritmos/algoritmo1.go marandradec")
        sys.exit(1)
    if not ruta.is_file():
        print(f"No existe el archivo: {ruta}")
        sys.exit(1)
    destino, res = guardar_log_sintactico(ruta.read_text(encoding="utf-8"), ruta.as_posix(), usuario)
    _imprimir_resumen([(ruta.name, len(res["tokens"]), len(res["errores_lexicos"]),
                        len(res["errores_sintacticos"]), destino)])