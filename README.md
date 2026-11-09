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

Avance 1 (análisis léxico) y Avance 2 (análisis sintáctico) terminados. El avance semántico se agrega en el siguiente entregable.

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

Analizar la sintaxis de un archivo (genera también su log en `logs/`):

```
py parser.py algoritmos/algoritmo1.go
py generar_log_sintactico.py algoritmos/algoritmo1.go marandradec
```

Los seis logs de prueba a la vez se generan desde la interfaz con el botón Logs de prueba. Si un archivo tiene errores léxicos, el análisis sintáctico no se ejecuta (el log indica NO EVALUADOS). Para obtener el log con los errores sintácticos de un archivo `errores_*.go`, corrige primero sus errores léxicos en el editor de la interfaz y presiona Analizar Sintaxis.

El log se llama `sintactico-usuarioGit-ddmmaaaa-HHhMM.txt` (por ejemplo `sintactico-marandradec-20102026-23h32.txt`) e incluye el análisis léxico y el sintáctico con sus errores, líneas y tokens. Si el mismo usuario genera dos logs en el mismo minuto, se agrega un sufijo (-2, -3). Usuario de Git por archivo de prueba:

| Archivos | Usuario Git |
| --- | --- |
| `algoritmo1.go`, `errores_andrade.go` | marandradec |
| `algoritmo2.go`, `errores_burgos.go` | TheFearLess |
| `algoritmo3.go`, `errores_mora.go` | JosMoraE |

Abrir la interfaz gráfica (barra superior: Analizar léxico, Analizar Sintaxis, Simular ejecución, Logs de prueba y Limpiar):

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
| `parser.py` | Analizador sintáctico con yacc (cada aporte está marcado con INICIO/FIN por integrante) |
| `interfaz.py` | Interfaz gráfica en Tkinter con ttkbootstrap (aportes marcados con INICIO/FIN) |
| `consola.py` | Consola interactiva y simulación de entrada y salida |
| `generar_log.py` | Ejecuta el analizador léxico sobre un `.go` y guarda el log léxico |
| `generar_log_sintactico.py` | Ejecuta léxico y sintáctico y guarda el log sintáctico |
| `algoritmos/algoritmo1.go` | Algoritmo de prueba de Andrade |
| `algoritmos/algoritmo2.go` | Algoritmo de prueba de Burgos |
| `algoritmos/algoritmo3.go` | Algoritmo de prueba de Mora |
| `algoritmos/errores_*.go` | Archivos con errores léxicos y sintácticos de cada integrante |
| `logs/` | Logs generados por las pruebas |
| `tests/` | Pruebas unitarias |

## Aportes por integrante

Cada archivo fuente delimita la contribución de cada integrante con las marcas `INICIO aporte: NOMBRE` y `FIN aporte: NOMBRE`.

| Archivo | Andrade | Burgos | Mora |
| --- | --- | --- | --- |
| `lexer.py` | Tokens y reglas propias | Tokens y reglas propias | Tokens y reglas propias |
| `parser.py` | Programa, import, if/else, arreglos, bloques | var, for, matrices, retorno, lista de sentencias | const, switch, mapas, Scanln, errores y ejecución del parser |
| `interfaz.py` | Ventana, editor, botones y confirmación de logs de prueba | Tokens y análisis sintáctico | Mensajes, logs y simulación |
| `consola.py`, `generar_log_sintactico.py` | | | Consola, simulación y logs sintácticos |
| `algoritmos/*.go` | `algoritmo1.go`, `errores_andrade.go` | `algoritmo2.go`, `errores_burgos.go` | `algoritmo3.go`, `errores_mora.go` |
| `tests/` | `test_lexer_andrade.py` y clase Andrade de `test_sintactico.py` | `test_lexer_burgos.py` y clase Burgos | `test_lexer_mora.py` y clase Mora |