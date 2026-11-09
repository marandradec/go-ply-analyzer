# -*- coding: utf-8 -*-
"""
ANALIZADOR SINTÁCTICO (Avance 2) - subconjunto de Go con PLY (yacc)

REGLAS DE ESTRUCTURA
- El léxico NO se modifica: se importan los tokens y el lexer de lexer.py.
- Cada aporte está delimitado con INICIO / FIN por integrante.
- Los no terminales compartidos (tipo, tipo_var, factor, llamada, funcion...) se
  completan con una producción por integrante, cada una en su propia función.
- Los errores se reportan con el formato:
  "Error sintáctico en la línea N. Se encontró el token X y se esperaba Y"
  o con un mensaje personalizado cuando se reconoce un error típico.
- Un error léxico en una línea suprime los errores sintácticos de esa misma línea
  (son consecuencia de que el token inválido se descarta).
"""

import sys
from pathlib import Path

import ply.yacc as yacc

import lexer as lexer_go_mod
from lexer import tokens  # noqa: F401  (yacc lo busca en este espacio de nombres)

lexer_go = lexer_go_mod.lexer

# INICIO aporte: MORA (infraestructura, registro de errores, fuente de tokens y precedencia)
# Registro global de errores sintácticos
errores_sintacticos = []

# Funciones completas reconocidas (sirve para los logs cuando un error impide devolver el árbol)
funciones_reconocidas = []


def _funcion_reconocida(nodo):
    funciones_reconocidas.append(nodo)
    return nodo


def registrar_error(linea, detalle, token=None):
    errores_sintacticos.append({
        "linea": linea,
        "token": token,  # token donde falló la gramática (para logs e interfaz)
        "mensaje": f"Error sintáctico en la línea {linea}. {detalle}",
    })


class _Fuente:
    """Envuelve al lexer para recordar la última línea leída (errores de fin de archivo)."""

    def __init__(self):
        self.ultima = 1

    def __getattr__(self, nombre):  # lineno, lexpos, etc. los toma del lexer real
        return getattr(lexer_go, nombre)

    def token(self):
        tok = lexer_go.token()
        if tok is not None:
            self.ultima = tok.lineno
        return tok


fuente = _Fuente()


# PRECEDENCIA Y ASOCIATIVIDAD
# La precedencia de operadores se resuelve con los niveles de la gramática
# (expresion > conjuncion > igualdad > orden > expr > term > factor), todos
# asociativos por la izquierda. La tabla solo desempata Println("...") entre la regla
# de Andrade (una cadena) y la de Burgos (lista de valores): gana el desplazamiento de ")".
precedence = (
    ('nonassoc', 'CADENA'),
    ('nonassoc', 'PAREN_DER'),
)
# FIN aporte: MORA (infraestructura, registro de errores, fuente de tokens y precedencia)


# INICIO aporte: ANDRADE (sintáctico)
# Estructura del programa, declaración corta, reasignación, suma y resta,
# igualdad, impresión de cadenas, if y else, arreglos y funciones sin parámetros.

def p_programa(p):
    '''programa : opt_nl PACKAGE ID nl import_decl funciones'''
    p[0] = ('programa', p[3], p[5], p[6])


def p_import_decl(p):
    '''import_decl : IMPORT CADENA nl'''
    p[0] = ('import', p[2])


def p_funciones(p):
    '''funciones : funciones funcion
                 | funcion'''
    p[0] = (p[1] + [p[2]]) if len(p) == 3 else [p[1]]


def p_funcion_sin_parametros(p):
    '''funcion : FUNC ID PAREN_IZQ PAREN_DER bloque nl'''
    p[0] = _funcion_reconocida(('funcion', p[2], [], None, p[5], p.lineno(1)))


def p_tipo_andrade(p):
    '''tipo : T_INT
            | T_STRING'''
    p[0] = p[1]


def p_tipo_var_arreglo(p):
    '''tipo_var : ARREGLO'''
    p[0] = p[1]


def p_decl_corta(p):
    '''decl_corta : ID DECLARACION_CORTA expresion'''
    p[0] = ('decl_corta', p[1], p[3], p.lineno(1))


def p_asignacion(p):
    '''asignacion : lvalue ASIGNACION expresion'''
    p[0] = ('asignacion', p[1], p[3], p.lineno(2))


def p_lvalue(p):
    '''lvalue : ID
              | acceso'''
    p[0] = ('id', p[1], p.lineno(1)) if isinstance(p[1], str) else p[1]


def p_acceso_arreglo(p):
    '''acceso : ID CORCHETE_IZQ expresion CORCHETE_DER'''
    p[0] = ('acceso', p[1], p[3], p.lineno(1))


def p_expr_suma_resta(p):
    '''expr : expr PLUS term
            | expr MINUS term'''
    p[0] = ('binop', p[2], p[1], p[3], p.lineno(2))


def p_expr_term(p):
    '''expr : term'''
    p[0] = p[1]


def p_igualdad(p):
    '''igualdad : igualdad EQ orden
                | igualdad NEQ orden'''
    p[0] = ('binop', p[2], p[1], p[3], p.lineno(2))


def p_igualdad_orden(p):
    '''igualdad : orden'''
    p[0] = p[1]


def p_imprimir_cadena(p):
    '''imprimir : FMT_PRINTLN PAREN_IZQ CADENA PAREN_DER'''
    p[0] = ('imprimir', [('cadena', p[3], p.lineno(3))], p.lineno(1))


def p_factor_andrade(p):
    '''factor : ENTERO
              | CADENA'''
    tipo = 'entero' if isinstance(p[1], int) else 'cadena'
    p[0] = (tipo, p[1], p.lineno(1))


def p_factor_id_acceso(p):
    '''factor : ID
              | acceso
              | llamada'''
    p[0] = ('id', p[1], p.lineno(1)) if isinstance(p[1], str) else p[1]


def p_factor_arreglo(p):
    '''factor : ARREGLO LLAVE_IZQ lista_expr LLAVE_DER'''
    p[0] = ('arreglo', p[1], p[3], p.lineno(1))


# Literal vacío: [3]int{} crea el arreglo con sus valores por defecto.
def p_factor_arreglo_vacio(p):
    '''factor : ARREGLO LLAVE_IZQ LLAVE_DER'''
    p[0] = ('arreglo', p[1], [], p.lineno(1))


def p_llamada_sin_argumentos(p):
    '''llamada : ID PAREN_IZQ PAREN_DER'''
    p[0] = ('llamada', p[1], [], p.lineno(1))


def p_if(p):
    '''if_stmt : IF expresion bloque
               | IF expresion bloque ELSE bloque
               | IF expresion bloque ELSE if_stmt'''
    p[0] = ('if', p[2], p[3], p[5] if len(p) == 6 else None, p.lineno(1))


# El else en una línea distinta a la llave } se reconoce completo para no generar
# errores en cascada: se registra un solo error y se continúa con lo que sigue.
def p_else_mal_ubicado(p):
    '''sentencia : ELSE bloque nl
                 | ELSE if_stmt nl'''
    registrar_error(p.lineno(1),
                    "Se encontró el token else. El else debe ir en la misma línea "
                    "que la llave de cierre. Ejemplo: } else {", token="else")
    p[0] = ('else_mal_ubicado', p.lineno(1))


# Recuperación: condición mal escrita; se descarta hasta la llave { del bloque.
def p_if_error(p):
    '''if_stmt : IF error bloque'''
    parser.errok()
    p[0] = ('if_error', p.lineno(1))


# Recuperación por sentencia: se descarta hasta el fin de línea y se continúa.
def p_sentencia_error(p):
    '''sentencia : error nl'''
    parser.errok()
    p[0] = ('sentencia_error', p.lineno(1))


# Manejador de errores de Andrade. Ejemplos de lo que reconoce
#   }                      <- el else va en la misma línea del }
#   else {                    (correcto: } else {)
#   total :=               <- falta el valor a la derecha de :=
#   if {                   <- falta la condición del if
#   import fmt             <- el import requiere comillas
#   x := [3]int{2, 3, 5    <- falta cerrar el literal con }
def _error_andrade(p, pila, enc):
    if enc == 'ELSE':
        return "El else debe ir en la misma línea que la llave de cierre. Ejemplo: } else {"
    if enc == 'NEWLINE' and pila[-1] == 'DECLARACION_CORTA':
        return "Falta el valor a la derecha de :="
    if enc == 'NEWLINE' and pila[-1] == 'ASIGNACION':
        return "Falta el valor a la derecha de ="
    if pila[-1] == 'IF' and enc == 'LLAVE_IZQ':
        return "El if necesita una condición antes de {"
    if pila[-1] == 'IMPORT' and enc != 'CADENA':
        return 'El import requiere una cadena entre comillas. Ejemplo: import "fmt"'
    if enc == 'NEWLINE' and 'LLAVE_IZQ' in pila:
        idx = len(pila) - 1 - pila[::-1].index('LLAVE_IZQ')
        if idx > 0 and pila[idx - 1] in ('ARREGLO', 'MATRIZ', 'MAPA'):
            return "Falta cerrar el literal con }"
    return None
# FIN aporte: ANDRADE (sintáctico)


# INICIO aporte: BURGOS (sintáctico)
# var con y sin valor inicial, * / %, comparación de orden, impresión de valores,
# for con contador o condición, matrices y funciones con un valor de retorno
# (con o sin parámetros).

def p_funcion_con_retorno(p):
    '''funcion : FUNC ID PAREN_IZQ lista_params PAREN_DER tipo bloque nl'''
    p[0] = _funcion_reconocida(('funcion', p[2], p[4], p[6], p[7], p.lineno(1)))


# Con retorno y sin parámetros. Ejemplo: func uno() int { return 1 }
def p_funcion_con_retorno_sin_parametros(p):
    '''funcion : FUNC ID PAREN_IZQ PAREN_DER tipo bloque nl'''
    p[0] = _funcion_reconocida(('funcion', p[2], [], p[5], p[6], p.lineno(1)))


def p_tipo_burgos(p):
    '''tipo : T_FLOAT64'''
    p[0] = p[1]


def p_tipo_var(p):
    '''tipo_var : tipo
                | MATRIZ'''
    p[0] = p[1]


def p_var_decl(p):
    '''var_decl : VAR ID tipo_var ASIGNACION expresion
                | VAR ID tipo_var'''
    p[0] = ('var', p[2], p[3], p[5] if len(p) == 6 else None, p.lineno(1))


def p_term(p):
    '''term : term TIMES factor
            | term DIVIDE factor
            | term MODULO factor'''
    p[0] = ('binop', p[2], p[1], p[3], p.lineno(2))


def p_term_factor(p):
    '''term : factor'''
    p[0] = p[1]


def p_orden(p):
    '''orden : orden LT expr
             | orden LE expr
             | orden GT expr
             | orden GE expr'''
    p[0] = ('binop', p[2], p[1], p[3], p.lineno(2))


def p_orden_expr(p):
    '''orden : expr'''
    p[0] = p[1]


def p_imprimir_valores(p):
    '''imprimir : FMT_PRINTLN PAREN_IZQ lista_expr PAREN_DER'''
    p[0] = ('imprimir', p[3], p.lineno(1))


# Sin argumentos. fmt.Println() imprime solo un salto de línea.
def p_imprimir_vacio(p):
    '''imprimir : FMT_PRINTLN PAREN_IZQ PAREN_DER'''
    p[0] = ('imprimir', [], p.lineno(1))


def p_lista_expr(p):
    '''lista_expr : lista_expr COMA expresion
                  | expresion'''
    p[0] = (p[1] + [p[3]]) if len(p) == 4 else [p[1]]


def p_for(p):
    '''for_stmt : FOR for_init SEMICOLON expresion SEMICOLON for_post bloque
                | FOR expresion bloque
                | FOR bloque'''
    if len(p) == 8:
        p[0] = ('for', p[2], p[4], p[6], p[7], p.lineno(1))
    elif len(p) == 4:
        p[0] = ('for', None, p[2], None, p[3], p.lineno(1))
    else:
        p[0] = ('for', None, None, None, p[2], p.lineno(1))


def p_for_init(p):
    '''for_init : decl_corta
                | asignacion'''
    p[0] = p[1]


def p_for_post(p):
    '''for_post : asignacion
                | asig_comp
                | inc_dec'''
    p[0] = p[1]


# Recuperación: encabezado del for mal escrito; se descarta hasta la llave {.
def p_for_error(p):
    '''for_stmt : FOR error bloque'''
    parser.errok()
    p[0] = ('for_error', p.lineno(1))


def p_retorno(p):
    '''retorno : RETURN expresion
               | RETURN'''
    p[0] = ('return', p[2] if len(p) == 3 else None, p.lineno(1))


def p_factor_flotante(p):
    '''factor : FLOAT_LITERAL'''
    p[0] = ('flotante', p[1], p.lineno(1))


def p_factor_matriz(p):
    '''factor : MATRIZ LLAVE_IZQ lista_filas LLAVE_DER'''
    p[0] = ('matriz', p[1], p[3], p.lineno(1))


# Literal vacío: [2][2]int{} crea la matriz con sus valores por defecto.
def p_factor_matriz_vacia(p):
    '''factor : MATRIZ LLAVE_IZQ LLAVE_DER'''
    p[0] = ('matriz', p[1], [], p.lineno(1))


def p_lista_filas(p):
    '''lista_filas : lista_filas COMA fila
                   | fila'''
    p[0] = (p[1] + [p[3]]) if len(p) == 4 else [p[1]]


def p_fila(p):
    '''fila : LLAVE_IZQ lista_expr LLAVE_DER'''
    p[0] = p[2]


def p_acceso_matriz(p):
    '''acceso : acceso CORCHETE_IZQ expresion CORCHETE_DER'''
    p[0] = ('acceso', p[1], p[3], p.lineno(2))


def p_llamada_con_argumentos(p):
    '''llamada : ID PAREN_IZQ lista_expr PAREN_DER'''
    p[0] = ('llamada', p[1], p[3], p.lineno(1))


# Recuperación: argumentos mal escritos; se descarta hasta el paréntesis ).
def p_llamada_error(p):
    '''llamada : ID PAREN_IZQ error PAREN_DER'''
    parser.errok()
    p[0] = ('llamada_error', p[1], p.lineno(1))


# Manejador de errores de Burgos. Ejemplos de lo que reconoce
#   var edad = 20                <- var exige tipo explícito
#   for i := 0; i < 10 {         <- el for con contador exige tres partes separadas por ;
#   total := 4 *                 <- falta el operando derecho
#   suma := sumar(1, )           <- falta un argumento después de la coma
_OPERADORES = {'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MODULO', 'EQ', 'NEQ', 'LT', 'LE', 'GT', 'GE'}


def _error_burgos(p, pila, enc):
    if pila[-1] in _OPERADORES:
        simbolo = parser.symstack[-1].value
        return f"Falta el operando a la derecha del operador {simbolo}"
    if len(pila) >= 2 and pila[-1] == 'ID' and pila[-2] == 'VAR':
        return "La declaración con var exige un tipo explícito. Ejemplo: var edad int = 20"
    if pila[-1] == 'COMA' and enc in ('PAREN_DER', 'NEWLINE', 'LLAVE_DER'):
        return "Falta un elemento después de la coma"
    if 'FOR' in pila and enc == 'LLAVE_IZQ':
        idx = len(pila) - 1 - pila[::-1].index('FOR')
        if pila[idx:].count('SEMICOLON') < 2:
            return "El for con contador exige tres partes separadas por ;. Ejemplo: for i := 0; i < 10; i++ {"
    return None
# FIN aporte: BURGOS (sintáctico)


# INICIO aporte: MORA (sintáctico)
# Asignación compuesta e incremento, const, paréntesis y signo negativo, conectores
# lógicos, fmt.Scanln, switch con case, default y break, mapas y funciones con
# parámetros sin retorno.

def p_funcion_con_parametros(p):
    '''funcion : FUNC ID PAREN_IZQ lista_params PAREN_DER bloque nl'''
    p[0] = _funcion_reconocida(('funcion', p[2], p[4], None, p[6], p.lineno(1)))


def p_lista_params(p):
    '''lista_params : lista_params COMA ID tipo
                    | ID tipo'''
    if len(p) == 5:
        p[0] = p[1] + [(p[3], p[4])]
    else:
        p[0] = [(p[1], p[2])]


def p_tipo_mora(p):
    '''tipo : T_BOOL'''
    p[0] = p[1]


def p_tipo_var_mapa(p):
    '''tipo_var : MAPA'''
    p[0] = p[1]


def p_const_decl(p):
    '''const_decl : CONST ID tipo ASIGNACION expresion'''
    p[0] = ('const', p[2], p[3], p[5], p.lineno(1))


def p_asig_comp(p):
    '''asig_comp : lvalue PLUS_ASSIGN expresion
                 | lvalue MINUS_ASSIGN expresion'''
    p[0] = ('asig_comp', p[2], p[1], p[3], p.lineno(2))


def p_inc_dec(p):
    '''inc_dec : lvalue INCREMENT
               | lvalue DECREMENT'''
    p[0] = ('inc_dec', p[2], p[1], p.lineno(2))


def p_expresion_or(p):
    '''expresion : expresion OR conjuncion'''
    p[0] = ('binop', p[2], p[1], p[3], p.lineno(2))


def p_expresion_conjuncion(p):
    '''expresion : conjuncion'''
    p[0] = p[1]


def p_conjuncion_and(p):
    '''conjuncion : conjuncion AND igualdad'''
    p[0] = ('binop', p[2], p[1], p[3], p.lineno(2))


def p_conjuncion_igualdad(p):
    '''conjuncion : igualdad'''
    p[0] = p[1]


def p_factor_parentesis(p):
    '''factor : PAREN_IZQ expresion PAREN_DER'''
    p[0] = p[2]


def p_factor_negativo(p):
    '''factor : MINUS factor'''
    p[0] = ('neg', p[2], p.lineno(1))


def p_factor_not(p):
    '''factor : NOT factor'''
    p[0] = ('not', p[2], p.lineno(1))


def p_factor_booleano(p):
    '''factor : BOOL_LITERAL'''
    p[0] = ('booleano', p[1], p.lineno(1))


def p_factor_mapa(p):
    '''factor : MAPA LLAVE_IZQ lista_pares LLAVE_DER'''
    p[0] = ('mapa', p[1], p[3], p.lineno(1))


# Literal vacío: map[string]int{} crea un mapa sin elementos.
def p_factor_mapa_vacio(p):
    '''factor : MAPA LLAVE_IZQ LLAVE_DER'''
    p[0] = ('mapa', p[1], [], p.lineno(1))


def p_lista_pares(p):
    '''lista_pares : lista_pares COMA par
                   | par'''
    p[0] = (p[1] + [p[3]]) if len(p) == 4 else [p[1]]


def p_par(p):
    '''par : expresion DOSPUNTOS expresion'''
    p[0] = (p[1], p[3])


def p_leer(p):
    '''leer : FMT_SCANLN PAREN_IZQ AMPERSAND ID PAREN_DER'''
    p[0] = ('leer', p[4], p.lineno(1))


def p_romper(p):
    '''romper : BREAK'''
    p[0] = ('break', p.lineno(1))


def p_llamada_sentencia(p):
    '''llamada_stmt : llamada'''
    p[0] = p[1]


# ===== INICIO aporte: MORA (estructura switch) =====

def p_switch(p):
    '''switch_stmt : SWITCH expresion LLAVE_IZQ opt_nl casos LLAVE_DER'''
    p[0] = ('switch', p[2], p[5], p.lineno(1))


# Un switch puede tener:
# - Solamente casos normales.
# - Casos normales y un único default.
# El default puede aparecer en cualquier posición.
def p_casos(p):
    '''casos : casos_normales
             | casos_normales default_bloque casos_normales'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[1] + [p[2]] + p[3]


# Lista de cero o más casos normales (sin default).
def p_casos_normales(p):
    '''casos_normales : casos_normales caso
                      | empty'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []


# Un caso normal tiene su expresión, dos puntos y sentencias.
def p_caso(p):
    '''caso : CASE lista_expr DOSPUNTOS opt_nl sentencias'''
    p[0] = ('case', p[2], p[5], p.lineno(1))


# El bloque default se define por separado.
# La gramática permite incluirlo una sola vez.
#Aqui la idea es identificar si existe mas de 1 default, ya que es un error sintactico el que haya un default despues de otro
def p_default_bloque(p):
    '''default_bloque : DEFAULT DOSPUNTOS opt_nl sentencias'''
    p[0] = ('default', p[4], p.lineno(1))


# Recuperación: case mal escrito.
# Conservamos el mecanismo original de recuperación.
def p_caso_error(p):
    '''caso : CASE error DOSPUNTOS opt_nl sentencias'''
    parser.errok()
    p[0] = ('case_error', p[5], p.lineno(1))

# ===== FIN aporte: MORA (estructura switch) =====


# Manejador de errores de Mora. Ejemplos de lo que reconoce
#   fmt.Scanln(numero)           <- falta & antes de la variable
#   const LIMITE int             <- la constante debe inicializarse
#   nuevo := (a + b * 2          <- falta cerrar el paréntesis
#   activo := edad >= 18 &&      <- falta el operando después del conector
#   case 1                       <- falta : después del case
#   edades := map[string]int{"Ana" 20}   <- falta : entre clave y valor
def _error_mora(p, pila, enc):
    if len(pila) >= 2 and pila[-1] == 'PAREN_IZQ' and pila[-2] == 'FMT_SCANLN' and enc == 'ID':
        return "fmt.Scanln necesita la dirección de la variable. Ejemplo: fmt.Scanln(&nombre)"
    if len(pila) >= 3 and pila[-3] == 'CONST' and enc == 'NEWLINE':
        return "Una constante debe inicializarse. Ejemplo: const MAX int = 100"
    if pila[-1] in ('AND', 'OR', 'NOT'):
        simbolo = parser.symstack[-1].value
        return f"Falta el operando a la derecha del operador {simbolo}"
    if 'CASE' in pila and enc == 'NEWLINE' and 'DOSPUNTOS' not in pila[pila.index('CASE'):]:
        return "Falta : después del valor del case"
    if 'MAPA' in pila and enc in ('ENTERO', 'CADENA', 'ID', 'FLOAT_LITERAL', 'BOOL_LITERAL'):
        return 'Falta : entre la clave y el valor del mapa. Ejemplo: {"Ana": 20}'
    if pila.count('PAREN_IZQ') > pila.count('PAREN_DER') and enc == 'NEWLINE':
        return "Falta cerrar un paréntesis )"
    return None
# FIN aporte: MORA (sintáctico)


# INICIO aporte: ANDRADE (soporte, saltos de línea y bloques)
# Saltos de línea que terminan las sentencias y bloque { ... } usado por if, for y funciones.

def p_nl(p):
    '''nl : nl NEWLINE
          | NEWLINE'''


def p_opt_nl(p):
    '''opt_nl : opt_nl NEWLINE
              | empty'''


def p_empty(p):
    '''empty :'''
    p[0] = None


def p_bloque(p):
    '''bloque : LLAVE_IZQ opt_nl sentencias LLAVE_DER'''
    p[0] = p[3]


# FIN aporte: ANDRADE (soporte, saltos de línea y bloques)


# INICIO aporte: BURGOS (soporte, lista de sentencias)
# Sentencias simples y compuestas que pueden aparecer dentro de un bloque.

def p_sentencias(p):
    '''sentencias : sentencias sentencia
                  | empty'''
    p[0] = (p[1] + [p[2]]) if len(p) == 3 else []


def p_sentencia_simple(p):
    '''sentencia : decl_corta nl
                 | asignacion nl
                 | asig_comp nl
                 | inc_dec nl
                 | var_decl nl
                 | const_decl nl
                 | imprimir nl
                 | leer nl
                 | retorno nl
                 | romper nl
                 | llamada_stmt nl'''
    p[0] = p[1]


def p_sentencia_compuesta(p):
    '''sentencia : if_stmt nl
                 | for_stmt nl
                 | switch_stmt nl'''
    p[0] = p[1]


# FIN aporte: BURGOS (soporte, lista de sentencias)


# INICIO aporte: MORA (soporte, manejo de errores y ejecución del parser)
# Mensajes "se esperaba ...", p_error, construcción del parser y analizar_sintactico().

# Símbolos legibles para el mensaje "se esperaba ..."
_NOMBRES = {
    'NEWLINE': 'salto de línea', 'LLAVE_IZQ': '{', 'LLAVE_DER': '}',
    'PAREN_IZQ': '(', 'PAREN_DER': ')', 'CORCHETE_IZQ': '[', 'CORCHETE_DER': ']',
    'DOSPUNTOS': ':', 'COMA': ',', 'SEMICOLON': ';', 'ASIGNACION': '=',
    'DECLARACION_CORTA': ':=', 'ID': 'identificador', 'ENTERO': 'número entero',
    'FLOAT_LITERAL': 'número decimal', 'CADENA': 'cadena', 'BOOL_LITERAL': 'true o false',
    'PLUS': '+', 'MINUS': '-', 'TIMES': '*', 'DIVIDE': '/', 'MODULO': '%',
    'EQ': '==', 'NEQ': '!=', 'LT': '<', 'GT': '>', 'LE': '<=', 'GE': '>=',
    'AND': '&&', 'OR': '||', 'NOT': '!', 'PLUS_ASSIGN': '+=', 'MINUS_ASSIGN': '-=',
    'INCREMENT': '++', 'DECREMENT': '--', 'AMPERSAND': '&',
    'FMT_PRINTLN': 'fmt.Println', 'FMT_SCANLN': 'fmt.Scanln',
    'T_INT': 'int', 'T_STRING': 'string', 'T_FLOAT64': 'float64', 'T_BOOL': 'bool',
    'ARREGLO': 'tipo arreglo', 'MATRIZ': 'tipo matriz', 'MAPA': 'tipo mapa',
    'PACKAGE': 'package', 'IMPORT': 'import', 'FUNC': 'func', 'IF': 'if', 'ELSE': 'else',
    'VAR': 'var', 'CONST': 'const', 'FOR': 'for', 'BREAK': 'break', 'RETURN': 'return',
    'SWITCH': 'switch', 'CASE': 'case', 'DEFAULT': 'default',
}
_INICIO_SENTENCIA = {'ID', 'VAR', 'CONST', 'IF', 'FOR', 'SWITCH', 'RETURN', 'BREAK',
                     'FMT_PRINTLN', 'FMT_SCANLN'}
_INICIO_EXPRESION = {'ID', 'ENTERO', 'FLOAT_LITERAL', 'CADENA', 'BOOL_LITERAL', 'NOT',
                     'PAREN_IZQ', 'ARREGLO', 'MATRIZ', 'MAPA'}


def _esperados():
    estado = parser.statestack[-1]
    esperados = {t for t in parser.action.get(estado, {}) if t not in ('error',)}
    if len(esperados & _INICIO_SENTENCIA) >= 4:
        esperados -= _INICIO_SENTENCIA
        esperados.add('una sentencia')
    elif {'ENTERO', 'CADENA'} <= esperados:
        esperados -= _INICIO_EXPRESION
        esperados.add('una expresión')
    pila = [s.type for s in parser.symstack]
    parentesis = pila.count('PAREN_IZQ') - pila.count('PAREN_DER')
    if parentesis <= 0:
        esperados.discard('PAREN_DER')
    if pila.count('CORCHETE_IZQ') - pila.count('CORCHETE_DER') <= 0:
        esperados.discard('CORCHETE_DER')
    en_literal = any(t in pila for t in ('ARREGLO', 'MATRIZ', 'MAPA'))
    if parentesis <= 0 and not en_literal:
        esperados.discard('COMA')
    if 'CASE' not in pila and 'MAPA' not in pila:
        esperados.discard('DOSPUNTOS')
    if 'FOR' not in pila:
        esperados.discard('SEMICOLON')
    if not any(t in pila for t in ('IF', 'FOR', 'SWITCH', 'FUNC', 'ELSE')) and pila[-1] not in ('ARREGLO', 'MATRIZ', 'MAPA'):
        esperados.discard('LLAVE_IZQ')
    if esperados & _OPERADORES and esperados - _OPERADORES - {'AND', 'OR'}:
        esperados -= _OPERADORES | {'AND', 'OR'}
    nombres = sorted(_NOMBRES.get(t, t) if t != '$end' else 'fin del archivo' for t in esperados)
    if not nombres:
        return 'otra construcción'
    if len(nombres) > 4:
        nombres = nombres[:4] + ['...']
    return nombres[0] if len(nombres) == 1 else ", ".join(nombres[:-1]) + " o " + nombres[-1]


def _describir(p):
    if p.type == 'NEWLINE':
        return 'salto de línea'
    if p.type == 'ID':
        return f"identificador {p.value}"
    return str(p.value)


def p_error(p):
    pila = [s.type for s in parser.symstack]
    if p is None:
        registrar_error(fuente.ultima,
                        "Se encontró el fin del archivo y se esperaba }. "
                        "Falta cerrar un bloque abierto con {", token="fin del archivo")
        return
    for manejador in (_error_andrade, _error_burgos, _error_mora):
        detalle = manejador(p, pila, p.type)
        if detalle:
            registrar_error(p.lineno, f"Se encontró el token {_describir(p)}. {detalle}",
                            token=_describir(p))
            return
    registrar_error(p.lineno, f"Se encontró el token {_describir(p)} y se esperaba {_esperados()}",
                    token=_describir(p))


# CONSTRUCCIÓN DEL PARSER
parser = yacc.yacc(start='programa', debug=False, write_tables=False)


def analizar_sintactico(codigo):
    """Devuelve (arbol, errores_sintacticos). Los errores de líneas con error léxico se omiten."""
    errores_sintacticos.clear()
    funciones_reconocidas.clear()
    lexer_go_mod.errores_lexicos.clear()
    if not codigo.endswith("\n"):
        codigo += "\n"
    lexer_go.lineno = 1
    lexer_go.input(codigo)
    arbol = parser.parse(lexer=fuente, tracking=True)
    lineas_lexicas = {e["linea"] for e in lexer_go_mod.errores_lexicos}
    errores = [e for e in errores_sintacticos if e["linea"] not in lineas_lexicas]
    return arbol, errores
if __name__ == "__main__":
    # Cada prueba desde la línea de comandos también genera su log en logs/
    #   py parser.py algoritmos/algoritmo1.go [usuarioGit]
    if len(sys.argv) not in (2, 3):
        print("Uso: py parser.py archivo.go [usuarioGit]")
        sys.exit(1)
    ruta = Path(sys.argv[1])
    codigo = ruta.read_text(encoding="utf-8")
    arbol, errores = analizar_sintactico(codigo)
    print(f"Archivo analizado: {ruta}")
    print(f"Errores léxicos (solo informativo): {len(lexer_go_mod.errores_lexicos)}")
    print(f"Errores sintácticos: {len(errores)}")
    for e in errores:
        print(f"  - {e['mensaje']}")
    if not errores:
        print("Análisis sintáctico correcto.")
    from generar_log_sintactico import guardar_log_sintactico, usuario_git_de, usuario_git_valido
    usuario = sys.argv[2] if len(sys.argv) == 3 else usuario_git_de(ruta)
    if usuario_git_valido(usuario):
        destino, _ = guardar_log_sintactico(codigo, ruta.as_posix(), usuario)
        print(f"Log guardado en logs/{destino.name}")
    else:
        print("No se generó el log. Indica el usuario de Git (py parser.py archivo.go usuarioGit).")
    sys.exit(1 if errores else 0)
# FIN aporte: MORA (soporte, manejo de errores y ejecución del parser)