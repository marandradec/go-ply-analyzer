# -*- coding: utf-8 -*-
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

from generar_log_lexico import CARPETA_LOGS
from generar_log_sintactico import (CARPETA_ALGORITMOS, USUARIOS_GIT, usuario_git_de,
                                    usuario_git_valido)
from semantic import analizar_completo_semantico


# Archivos de prueba del Avance 3: los tres algoritmos correctos (0 errores) y un archivo con
# errores semánticos por integrante (semantico_*.go). Son programas Go normales, sin marcas.
ARCHIVOS_SEMANTICOS = [(f"{base}.go", usuario) for base, usuario in USUARIOS_GIT.items()
                       if base.startswith(("algoritmo", "errores_semantico_"))]

def construir_log_semantico(resultado, codigo, archivo, autor, ahora):
    tokens = resultado["tokens"]
    err_lex = resultado["errores_lexicos"]
    err_sin = resultado["errores_sintacticos"]
    err_sem = resultado["errores_semanticos"]
    lineas_codigo = codigo.splitlines()   # el código original, con la misma numeración de líneas

    lineas = [
        f"ANALISIS LEXICO, SINTACTICO Y SEMANTICO - usuario Git: {autor}",
        f"Archivo: {archivo}",
        f"Fecha: {ahora:%d-%m-%Y %H:%M:%S}",
    ]

    # FASE 1
    lineas += ["", "FASE 1. ANALISIS LEXICO", "=" * 60,
               f"Tokens reconocidos: {len(tokens)}"]
    lineas += [e["mensaje"] for e in err_lex] or ["No se encontraron errores lexicos."]
    lineas.append(f"Total de errores lexicos: {len(err_lex)}")

    # FASE 2
    lineas += ["", "FASE 2. ANALISIS SINTACTICO", "=" * 60]
    if err_lex:
        lineas += ["Resultado: NO EJECUTADO", "Motivo: Existen errores léxicos en el código fuente."]
    elif err_sin:
        lineas.append(f"Resultado: SE ENCONTRARON {len(err_sin)} ERROR(ES) SINTACTICO(S)")
        for e in err_sin:
            lineas.append(f"Linea {e['linea']:03d} | Token: {e.get('token') or '-'}")
            lineas.append(f"    {e['mensaje']}")
    elif resultado["arbol"] is None:
        lineas += ["Resultado: ANALISIS SINTACTICO INCOMPLETO",
                   "Motivo: El parser no pudo construir un árbol completo."]
    else:
        lineas += ["Resultado: ANALISIS SINTACTICO CORRECTO", "Total de errores sintacticos: 0"]

    # FASE 3
    lineas += ["", "FASE 3. ANALISIS SEMANTICO", "=" * 60]
    if not resultado["semantico_ejecutado"]:
        lineas += ["Resultado: NO EJECUTADO", f"Motivo: {resultado['motivo']}"]
    elif err_sem:
        lineas.append(f"Resultado: SE ENCONTRARON {len(err_sem)} ERROR(ES) SEMANTICO(S)")
    else:
        lineas.append("Resultado: ANALISIS SEMANTICO CORRECTO")

    lineas += ["", "TABLA DE SIMBOLOS", "-" * 60]
    if resultado["semantico_ejecutado"]:
        lineas.append(f"{'Ambito':20s} | {'Nombre':20s} | {'Clase':10s} | {'Tipo':18s} | Const | Linea")
        for ambito, nombre, clase, tipo, const, linea in resultado["tabla"]:
            lineas.append(f"{ambito:20s} | {nombre:20s} | {clase:10s} | {tipo:18s} | {const:5s} | {linea:03d}")
        lineas.append(f"Total de simbolos: {len(resultado['tabla'])}")
    else:
        lineas.append("Tabla no construida porque el analisis semantico no se ejecuto.")

    lineas += ["", "ERRORES SEMANTICOS", "-" * 60]
    if not resultado["semantico_ejecutado"]:
        lineas.append("No se evaluaron errores semanticos: el analisis se detuvo en una fase anterior.")
    elif err_sem:
        for e in err_sem:
            lineas.append(f"Linea {e['linea']:03d} | Categoria: {e['categoria']} | Regla: {e['regla']}")
            lineas.append(f"    {e['mensaje']}")
            if 1 <= e["linea"] <= len(lineas_codigo):
                lineas.append(f"    Codigo: {lineas_codigo[e['linea'] - 1].strip()}")
    else:
        lineas.append("No se encontraron errores semanticos.")
    if resultado["semantico_ejecutado"]:
        lineas.append("")
        lineas.append(f"Total de errores semanticos: {len(err_sem)}")
        for categoria, cantidad in sorted(Counter(e["categoria"] for e in err_sem).items()):
            lineas.append(f"  {categoria:26s} | {cantidad}")
    else:
        lineas += ["", "Total de errores semanticos: NO EVALUADOS"]

    lineas += [
        "", "RESUMEN FINAL", "=" * 60,
        f"Tokens reconocidos        | {len(tokens)}",
        f"Errores lexicos           | {len(err_lex)}",
        (f"Errores sintacticos       | {len(err_sin)}" if resultado["sintactico_ejecutado"]
         else "Errores sintacticos       | NO EVALUADOS"),
        (f"Errores semanticos        | {len(err_sem)}" if resultado["semantico_ejecutado"]
         else "Errores semanticos        | NO EVALUADOS"),
        "Fase semantica ejecutada  | " + ("Si" if resultado["semantico_ejecutado"] else "No"),
    ]
    return "\n".join(lineas) + "\n"


def _destino(autor, ahora):
    CARPETA_LOGS.mkdir(exist_ok=True)
    base = f"semantico-{autor}-{ahora:%d%m%Y-%Hh%M}"
    destino = CARPETA_LOGS / f"{base}.txt"
    n = 2
    while destino.exists():  # mismo usuario y minuto (ej. algoritmo1 y errores_andrade): -2, -3 ...
        destino = CARPETA_LOGS / f"{base}-{n}.txt"
        n += 1
    return destino


def guardar_log_semantico(codigo, archivo, autor):
    """Analiza y guarda el log. Devuelve (ruta del log, resultado del análisis)."""
    resultado = analizar_completo_semantico(codigo)
    ahora = datetime.now()
    destino = _destino(autor, ahora)
    destino.write_text(construir_log_semantico(resultado, codigo, archivo, autor, ahora),
                       encoding="utf-8")
    return destino, resultado


def generar_logs_de_prueba_semanticos():
    """Genera el log semántico de los seis archivos de prueba y devuelve un resumen por archivo."""
    resumen = []
    for nombre, autor in ARCHIVOS_SEMANTICOS:
        ruta = CARPETA_ALGORITMOS / nombre
        if not ruta.is_file():
            print(f"No existe el archivo: {ruta}")
            continue
        destino, res = guardar_log_semantico(ruta.read_text(encoding="utf-8"), f"algoritmos/{nombre}", autor)
        resumen.append((nombre, len(res["tokens"]), len(res["errores_lexicos"]),
                        len(res["errores_sintacticos"]),
                        len(res["errores_semanticos"]) if res["semantico_ejecutado"] else None,
                        destino))
    return resumen


def _imprimir_resumen(resumen):
    print(f"{'Archivo':20s} {'Tokens':>7s} {'Lex':>4s} {'Sint':>5s} {'Sem':>5s}  Log")
    for nombre, tokens, lex, sint, sem, destino in resumen:
        print(f"{nombre:20s} {tokens:7d} {lex:4d} {sint:5d} {'-' if sem is None else sem:>5}  {destino.name}")


if __name__ == "__main__":
    ruta = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    usuario = sys.argv[2] if len(sys.argv) > 2 else (usuario_git_de(ruta) if ruta else None)
    if ruta is None or len(sys.argv) > 3 or not usuario_git_valido(usuario):
        print("Uso: py generar_log_semantico.py archivo.go usuarioGit")
        print("Ejemplo: py generar_log_semantico.py algoritmos/algoritmo1.go marandradec")
        sys.exit(1)
    if not ruta.is_file():
        print(f"No existe el archivo: {ruta}")
        sys.exit(1)
    destino, res = guardar_log_semantico(ruta.read_text(encoding="utf-8"), ruta.as_posix(), usuario)
    _imprimir_resumen([(ruta.name, len(res["tokens"]), len(res["errores_lexicos"]),
                        len(res["errores_sintacticos"]),
                        len(res["errores_semanticos"]) if res["semantico_ejecutado"] else None,
                        destino)])
