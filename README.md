# go-ply-analyzer

Analizador léxico, sintáctico y semántico para un subconjunto del lenguaje Go, desarrollado en Python con PLY (Lex-Yacc) y una interfaz gráfica en Tkinter.
Proyecto parcial de Lenguajes de Programación, ESPOL, II PAO 2026.

## Integrantes

| Integrante | Usuario GitHub |
| --- | --- |
| María Cristina Andrade Echeverría | marandradec |
| Joshua Gabriel Burgos Zorrilla | TheFearLess |
| José Mario Mora Estrella | JosMoraE |

## Estado

Avance 1 (análisis léxico), Avance 2 (análisis sintáctico) y Avance 3 (análisis semántico con tabla de símbolos) terminados. Las tres fases se ejecutan en orden: si una fase encuentra errores, las siguientes se marcan como NO EJECUTADO.

## Instalación

```
pip install -r requirements.txt
```

## Uso

### Interfaz gráfica

```
py interfaz.py
```

Barra superior:

| Botón | Acción |
| --- | --- |
| Analizar léxico | Reconoce los tokens y los errores léxicos y guarda el log léxico |
| Analizar Sintaxis | Ejecuta léxico y sintáctico y guarda el log sintáctico |
| Analizar Semántica | Ejecuta las tres fases, muestra la tabla de símbolos y guarda el log semántico |
| Simular ejecución | Simula la entrada y salida de `main` (`fmt.Println` y `fmt.Scanln`) |
| Logs léxico, Logs sintáctico, Logs semántico | Generan de una vez los logs de los seis archivos de prueba de cada fase |
| Limpiar | Reinicia el análisis sin cerrar la aplicación |

El panel inferior tiene las pestañas Log léxico, Log sintáctico, Log semántico, Consola y Tabla de símbolos.

### Línea de comandos

Análisis léxico (genera el log en `logs/`):

```
py generar_log_lexico.py algoritmos/algoritmo1.go MariaAndrade
```

Análisis sintáctico (genera el log en `logs/`):

```
py parser.py algoritmos/algoritmo1.go
py generar_log_sintactico.py algoritmos/algoritmo1.go marandradec
```

Análisis semántico (genera el log en `logs/`):

```
py semantic.py algoritmos/algoritmo1.go
py generar_log_semantico.py algoritmos/errores_semantico_andrade.go marandradec
```

Si el archivo es uno de los seis de prueba, el usuario de Git se asigna automáticamente; para otros archivos se indica como último argumento.

### Pruebas automáticas

```
py -m unittest discover -s tests -v
```

## Fases y logs

| Fase | Qué valida | Formato del log |
| --- | --- | --- |
| Léxica | Tokens y tres errores: cadena sin cerrar, número mal formado y símbolo no reconocido | `lexico-NombreApellido-dd-mm-aaaa-HHhMM.txt` |
| Sintáctica | Estructura gramatical, con mensajes de error personalizados y recuperación de errores | `sintactico-usuarioGit-ddmmaaaa-HHhMM.txt` |
| Semántica | Coherencia lógica con una tabla de símbolos por ámbitos; seis reglas, dos por integrante | `semantico-usuarioGit-ddmmaaaa-HHhMM.txt` |

Si el mismo usuario genera dos logs sintácticos o semánticos en el mismo minuto, se agrega un sufijo (-2, -3). El log léxico individual se sobrescribe si se repite en el mismo minuto; el sufijo solo se agrega cuando Logs léxico crea dos logs del mismo autor a la vez. Cada log incluye las fases anteriores. El log semántico agrega la tabla de símbolos (ámbito, nombre, clase, tipo, constante y línea), los errores con su categoría, regla, línea y código, y un resumen final con el conteo por fase.

Si un archivo tiene errores léxicos, el análisis sintáctico no se ejecuta; si tiene errores sintácticos, no se ejecuta el semántico. Para obtener el log con los errores sintácticos de un archivo `errores_*.go`, corrige primero sus errores léxicos en el editor de la interfaz y presiona Analizar Sintaxis.

### Reglas semánticas

| Integrante | Categoría | Regla |
| --- | --- | --- |
| Andrade | Identificadores (Inexistencia) | Uso sin declaración: toda variable o función usada debe existir en un ámbito visible |
| Andrade | Identificadores (Duplicidad) | Prohibición de redeclaración en el mismo bloque |
| Burgos | Operaciones permitidas | Operandos compatibles en las operaciones aritméticas, de comparación y lógicas |
| Burgos | Retorno de funciones | El tipo del `return` debe coincidir con el declarado y toda función con retorno debe incluir un `return` |
| Mora | Asignación de tipo | El valor asignado debe coincidir con el tipo declarado y una constante no puede modificarse |
| Mora | Estructuras de control | `break` solo dentro de un `for` o un `switch` |

### Usuario de Git por archivo de prueba

| Archivos | Usuario Git |
| --- | --- |
| `algoritmo1.go`, `errores_andrade.go`, `errores_semantico_andrade.go` | marandradec |
| `algoritmo2.go`, `errores_burgos.go`, `errores_semantico_burgos.go` | TheFearLess |
| `algoritmo3.go`, `errores_mora.go`, `errores_semantico_mora.go` | JosMoraE |

## Estructura

| Ruta | Contenido |
| --- | --- |
| `lexer.py` | Analizador léxico (cada aporte está marcado con INICIO/FIN por integrante) |
| `parser.py` | Analizador sintáctico con yacc (aportes marcados con INICIO/FIN) |
| `semantic.py` | Analizador semántico unificado: tabla de símbolos, recorrido del árbol y las seis reglas (aportes marcados con INICIO/FIN) |
| `interfaz.py` | Interfaz gráfica en Tkinter con ttkbootstrap (aportes marcados con INICIO/FIN) |
| `consola.py` | Consola interactiva y simulación de entrada y salida |
| `generar_log_lexico.py` | Ejecuta el analizador léxico sobre un `.go` y guarda el log léxico |
| `generar_log_sintactico.py` | Ejecuta léxico y sintáctico y guarda el log sintáctico |
| `generar_log_semantico.py` | Ejecuta las tres fases y guarda el log semántico con la tabla de símbolos |
| `algoritmos/algoritmo1.go`, `algoritmo2.go`, `algoritmo3.go` | Algoritmos correctos de Andrade, Burgos y Mora (0 errores en las tres fases) |
| `algoritmos/errores_*.go` | Archivos con errores léxicos y sintácticos de cada integrante |
| `algoritmos/errores_semantico_*.go` | Archivos con un caso de error semántico por función, sin errores léxicos ni sintácticos |
| `logs/` | Logs generados por las pruebas |
| `tests/` | Pruebas unitarias (118 en total) |

## Aportes por integrante

Cada archivo fuente delimita la contribución de cada integrante con las marcas `INICIO aporte: NOMBRE` y `FIN aporte: NOMBRE`.

| Archivo | Andrade | Burgos | Mora |
| --- | --- | --- | --- |
| `lexer.py` | Tokens y reglas propias | Tokens y reglas propias | Tokens y reglas propias |
| `parser.py` | Programa, import, if/else, arreglos, bloques | var, for, matrices, retorno, lista de sentencias | const, switch, mapas, Scanln, errores y ejecución del parser |
| `semantic.py` | Tabla de símbolos, recorrido del árbol e Identificadores | Operaciones permitidas y retorno de funciones | Asignación de tipo, estructuras de control y ejecución por fases |
| `interfaz.py` | Ventana, editor, botones y pestañas (incluidas las semánticas) | Tokens, análisis sintáctico y visualización del análisis semántico | Mensajes, logs, simulación y logs de prueba |
| `consola.py`, `generar_log_sintactico.py` | | | Consola, simulación y logs sintácticos |
| `generar_log_semantico.py` | Generador de logs semánticos | | |
| `algoritmos/*.go` | `algoritmo1.go`, `errores_andrade.go`, `errores_semantico_andrade.go` | `algoritmo2.go`, `errores_burgos.go`, `errores_semantico_burgos.go` | `algoritmo3.go`, `errores_mora.go`, `errores_semantico_mora.go` |
| `tests/` | `test_lexer_andrade.py`, clase Andrade de `test_sintactico.py` y `test_semantico_andrade.py` | `test_lexer_burgos.py` y clase Burgos de `test_sintactico.py` | `test_lexer_mora.py`, clase Mora de `test_sintactico.py`, `test_switch_mora.py`, `test_fases_mora.py` y `test_semantico_mora.py` |

## Pruebas automáticas

| Archivo | Pruebas |
| --- | --- |
| `test_lexer_andrade.py`, `test_lexer_burgos.py`, `test_lexer_mora.py`, `test_algoritmos.py` | 33 (analizador léxico) |
| `test_sintactico.py` | 17 |
| `test_switch_mora.py`, `test_fases_mora.py` | 7 |
| `test_semantico_andrade.py` | 37 |
| `test_semantico_mora.py` | 24 |

Las reglas semánticas de Burgos se verifican ejecutando el analizador completo sobre `algoritmo2.go` (0 errores) y `errores_semantico_burgos.go` (16 errores esperados).