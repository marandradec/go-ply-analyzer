# go-ply-analyzer

Analizador léxico, sintáctico y semántico para un subconjunto del lenguaje Go, desarrollado en Python con PLY (Lex-Yacc).
Proyecto parcial de Lenguajes de Programación, ESPOL, II PAO 2026.

## Integrantes

| Integrante | Usuario GitHub |
| --- | --- |
| María Cristina Andrade Echeverría | marandradec |
| Joshua Gabriel Burgos Zorrilla | TheFearLess |
| José Mario Mora Estrella | JosMoraE |

## Estado

Avance 1 (análisis léxico) terminado. Los avances sintáctico y semántico se agregan en los siguientes entregables.

## Instalación

```
pip install -r requirements.txt
```

## Uso

Analizar un archivo y generar su log (carpeta `logs/`):

```
py generar_log.py algoritmos/algoritmo1.go MariaAndrade
```

El log se llama `lexico-NombreApellido-dd-mm-aaaa-HHhMM.txt` e incluye todos los tokens reconocidos y los errores léxicos.

Abrir la interfaz gráfica:

```
py interfaz.py
```

Ejecutar las pruebas automáticas:

```
py -m unittest discover -s tests -v
```

## Estructura

| Ruta | Contenido |
| --- | --- |
| `lexer.py` | Analizador léxico (cada aporte está marcado con INICIO/FIN por integrante) |
| `interfaz.py` | Interfaz gráfica en Tkinter |
| `generar_log.py` | Ejecuta el analizador sobre un `.go` y guarda el log |
| `algoritmos/algoritmo1.go` | Algoritmo de prueba de Andrade |
| `algoritmos/algoritmo2.go` | Algoritmo de prueba de Burgos |
| `algoritmos/algoritmo3.go` | Algoritmo de prueba de Mora |
| `algoritmos/errores_*.go` | Archivos con errores léxicos de cada integrante |
| `logs/` | Logs generados por las pruebas |
| `tests/` | Pruebas unitarias |
