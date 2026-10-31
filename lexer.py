# -*- coding: utf-8 -*-
"""
REGLAS DE ORDEN EN PLY:
- El orden de las funciones determina la prioridad léxica.
- Secuencia obligatoria: BURGOS -> MORA -> ANDRADE
"""

import ply.lex as lex

# Registro global de errores léxicos
errores_lexicos = []

def registrar_error(linea, detalle):
    errores_lexicos.append({
        "linea": linea,
        "mensaje": f"Error léxico en la línea {linea}. {detalle}",
    })


# PALABRAS RESERVADAS Y TIPOS
# INICIO aporte: ANDRADE
reservadas_andrade = {
    # Palabras reservadas
    'package': 'PACKAGE',
    'import': 'IMPORT',
    'func': 'FUNC',
    'if': 'IF',
    'else': 'ELSE',
    # Tipos predefinidos
    'int': 'T_INT',
    'string': 'T_STRING',
}
# FIN aporte: ANDRADE

# INICIO aporte: BURGOS
reservadas_burgos = {
	'var': 'VAR',
    'const': 'CONST',
    'for': 'FOR',
    'break': 'BREAK',
    'return': 'RETURN'
}
# FIN aporte: BURGOS

# INICIO aporte: MORA
reservadas_mora = {}
# FIN aporte: MORA

reservadas = {**reservadas_andrade, **reservadas_burgos, **reservadas_mora}


# LISTA DE TOKENS
# INICIO aporte: ANDRADE
tokens_andrade = [
    'ID', 'ENTERO', 'CADENA', 'ARREGLO',
    'ASIGNACION', 'DECLARACION_CORTA',
    'LLAVE_IZQ', 'LLAVE_DER', 'PAREN_IZQ', 'PAREN_DER',
    'NEWLINE',
]
# FIN aporte: ANDRADE

# INICIO aporte: BURGOS
tokens_burgos = [
'FLOAT64', 'MATRIZ', 'FLOAT_LITERAL',
    'EQ', 'NEQ', 'LE', 'GE', 'LT', 'GT',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MODULO',
    'SEMICOLON'
]
# FIN aporte: BURGOS

# INICIO aporte: MORA
tokens_mora = []
# FIN aporte: MORA

# Esta línea junta todo: las tres listas + los nombres del diccionario "reservadas"
tokens = tokens_andrade + tokens_burgos + tokens_mora + sorted(set(reservadas.values()))


# REGLAS COMO FUNCIÓN
# INICIO aporte: BURGOS (funciones)
# FIN aporte: BURGOS (funciones)

# INICIO aporte: MORA (funciones)
# FIN aporte: MORA (funciones)

# INICIO aporte: ANDRADE (funciones)
def t_COMENTARIO_LINEA(t):
    r'//[^\n]*'
    pass

def t_COMENTARIO_BLOQUE(t):
    r'/\*(?:.|\n)*?\*/'
    t.lexer.lineno += t.value.count('\n')

def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    t.value = '\\n'
    return t

def t_CADENA(t):
    r'"[^"\n]*"'
    return t

def t_ERROR_CADENA(t):
    r'"[^"\n]*'
    registrar_error(t.lexer.lineno, f"Cadena sin cerrar {t.value}")

def t_ENTERO(t):
    r'[0-9]+'
    t.value = int(t.value)
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reservadas.get(t.value, 'ID')
    return t
# FIN aporte: ANDRADE (funciones)


# --- REGLAS COMO CADENA ---
# INICIO aporte: ANDRADE (cadenas)
t_ARREGLO = r'\[[0-9]+\](?:int|float64|string|bool)'
t_DECLARACION_CORTA = r':='
t_ASIGNACION = r'='
t_LLAVE_IZQ = r'\{'
t_LLAVE_DER = r'\}'
t_PAREN_IZQ = r'\('
t_PAREN_DER = r'\)'
t_ignore = ' \t\r'
# FIN aporte: ANDRADE (cadenas)

# INICIO aporte: BURGOS (cadenas)
t_MATRIZ    = r'\[[0-9]+\]\[[0-9]+\](?:[a-zA-Z_][a-zA-Z0-9_]*)' 
t_FLOAT64   = r'float64'

t_EQ        = r'=='
t_NEQ       = r'!='
t_LE        = r'<='
t_GE        = r'>='
t_LT        = r'<'
t_GT        = r'>'
t_PLUS      = r'\+'
t_MINUS     = r'-'
t_TIMES     = r'\*'
t_DIVIDE    = r'/'
t_MODULO    = r'%'
t_SEMICOLON = r';'
# FIN aporte: BURGOS (cadenas)

# INICIO aporte: MORA (cadenas)
# FIN aporte: MORA (cadenas)

# INICIO aporte: BURGOS (funciones)

def t_MALFORMED_NUMBER(t):
    r'(?:\d+[a-zA-Z_]+)|(?:\d+\.)'
    print(f"Error léxico: Número mal formado '{t.value}'")
    t.lexer.skip(len(t.value))

def t_FLOAT_LITERAL(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

# FIN aporte: BURGOS (funciones)

# CONSTRUCCIÓN DEL LEXER
lexer = lex.lex()

def analizar(codigo):
    errores_lexicos.clear()
    lexer.lineno = 1
    lexer.input(codigo)
    reconocidos = [(tok.type, tok.value, tok.lineno) for tok in lexer]
    return reconocidos, list(errores_lexicos)
