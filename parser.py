# -*- coding: utf-8 -*-
"""
ANALIZADOR SINTÁCTICO (Avance 2)

REGLAS DE ESTRUCTURA
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

















































































































































































# FIN aporte: BURGOS (sintáctico)


# INICIO aporte: MORA (sintáctico)











































































































































































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






























# FIN aporte: BURGOS (soporte, lista de sentencias)


# INICIO aporte: MORA (soporte, manejo de errores y ejecución del parser)






























































































































# FIN aporte: MORA (soporte, manejo de errores y ejecución del parser)