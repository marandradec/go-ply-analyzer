# -*- coding: utf-8 -*-
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

from lexer import analizar

CARPETA_LOGS = Path(__file__).resolve().parent / "logs"


def _destino_log(autor, ahora):
    """Devuelve la ruta fija del log: si se ejecuta en el mismo minuto, sobrescribe el archivo."""
    CARPETA_LOGS.mkdir(exist_ok=True)
    base = f"lexico-{autor}-{ahora:%d-%m-%Y-%Hh%M}"
    return CARPETA_LOGS / f"{base}.txt"


def _valor(tipo, valor):
    return valor if tipo == "NEWLINE" else repr(valor)


def construir_log(tokens, errores, archivo, autor, ahora):
    lineas = [
        f"ANALISIS LEXICO - {autor}",
        f"Archivo: {archivo}",
        f"Fecha: {ahora:%d-%m-%Y %H:%M:%S}",
        "",
        "TOKENS RECONOCIDOS",
        "=" * 60,
    ]
    for tipo, valor, linea in tokens:
        lineas.append(f"Linea {linea:03d} | {tipo:20s} | {_valor(tipo, valor)}")

    lineas += ["", f"Total de tokens: {len(tokens)}", "", "RESUMEN POR TIPO DE TOKEN", "=" * 60]
    for tipo, cantidad in sorted(Counter(t[0] for t in tokens).items()):
        lineas.append(f"{tipo:20s} | {cantidad}")

    lineas += ["", "ERRORES LEXICOS", "=" * 60]
    if errores:
        lineas += [e["mensaje"] for e in errores]
    else:
        lineas.append("No se encontraron errores lexicos.")
    lineas += ["", f"Total de errores: {len(errores)}"]
    return "\n".join(lineas) + "\n"


def guardar_log(codigo, archivo, autor):
    tokens, errores = analizar(codigo)
    ahora = datetime.now()
    destino = _destino_log(autor, ahora)
    destino.write_text(construir_log(tokens, errores, archivo, autor, ahora), encoding="utf-8")
    return destino, tokens, errores


def ejecutar_prueba(ruta_archivo, autor):
    ruta = Path(ruta_archivo)
    if not ruta.is_file():
        print(f"No existe el archivo: {ruta}")
        return 1

    destino, tokens, errores = guardar_log(ruta.read_text(encoding="utf-8"), ruta.as_posix(), autor)

    print(f"Archivo analizado: {ruta}")
    print(f"Tokens reconocidos: {len(tokens)}")
    print(f"Errores lexicos: {len(errores)}")
    for error in errores:
        print(f"  - {error['mensaje']}")
    print(f"Log generado: {destino}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3 or not re.fullmatch(r"[A-Za-z]+", sys.argv[2]):
        print("Uso: py generar_log.py archivo.go NombreApellido")
        print("Ejemplo: py generar_log.py algoritmos/algoritmo1.go MariaAndrade")
        sys.exit(1)
    sys.exit(ejecutar_prueba(sys.argv[1], sys.argv[2]))