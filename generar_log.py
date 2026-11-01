
from pathlib import Path
from datetime import datetime
import sys

from lexer import analizar


def ejecutar_prueba(ruta_archivo):
    ruta = Path(ruta_archivo)

    if not ruta.is_file():
        print(f"No existe el archivo: {ruta}")
        return

    codigo = ruta.read_text(encoding="utf-8")
    tokens, errores = analizar(codigo)

    ahora = datetime.now()
    fecha = ahora.strftime("%d-%m-%Y-%Hh%M")
    nombre = f"lexico-JoseMora-{fecha}.txt"

    carpeta_logs = Path("logs")
    carpeta_logs.mkdir(exist_ok=True)

    # Evitar sobrescribir un log si hay varias pruebas
    # dentro del mismo minuto.
    destino = carpeta_logs / nombre
    if destino.exists():
        fecha = ahora.strftime("%d-%m-%Y-%Hh%M%S")
        destino = carpeta_logs / f"lexico-JoseMora-{fecha}.txt"

    contenido = [
        "ANALISIS LEXICO - JOSE MORA",
        f"Archivo: {ruta}",
        f"Fecha: {ahora:%d-%m-%Y %H:%M:%S}",
        "",
        "TOKENS RECONOCIDOS",
        "=" * 60,
    ]

    for tipo, valor, linea in tokens:
        contenido.append(
            f"Linea {linea:03d} | {tipo:20s} | {valor!r}"
        )

    contenido.extend([
        "",
        f"Total de tokens: {len(tokens)}",
        "",
        "ERRORES LEXICOS",
        "=" * 60,
    ])

    if errores:
        for error in errores:
            contenido.append(error["mensaje"])
    else:
        contenido.append("No se encontraron errores lexicos.")

    contenido.append(f"\nTotal de errores: {len(errores)}")

    destino.write_text(
        "\n".join(contenido) + "\n",
        encoding="utf-8"
    )

    print(f"Tokens reconocidos: {len(tokens)}")
    print(f"Errores lexicos: {len(errores)}")
    print(f"Log generado: {destino}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: py generar_log.py archivo.go")
        sys.exit(1)

    ejecutar_prueba(sys.argv[1])
