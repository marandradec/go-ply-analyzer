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
    'return': 'RETURN',
    'float64': 'FLOAT64',
}
# FIN aporte: BURGOS

# INICIO aporte: MORA
reservadas_mora = {
    'switch': 'SWITCH',
    'case': 'CASE',
    'default': 'DEFAULT',

    # Tipo y literales booleanos
    'bool': 'T_BOOL',
    'true': 'BOOL_LITERAL',
    'false': 'BOOL_LITERAL',
}
# FIN aporte: MORA

reservadas = {**reservadas_andrade, **reservadas_burgos, **reservadas_mora}


# LISTA DE TOKENS
# INICIO aporte: ANDRADE
tokens_andrade = [
    'ID', 
    'ENTERO', 
    'CADENA', 
    'ARREGLO',
    'ASIGNACION', 
    'DECLARACION_CORTA',
    'LLAVE_IZQ', 
    'LLAVE_DER', 
    'PAREN_IZQ', 
    'PAREN_DER',
    'NEWLINE',
]
# FIN aporte: ANDRADE

# INICIO aporte: BURGOS
tokens_burgos = [
    'MATRIZ', 
    'FLOAT_LITERAL',
    'EQ', 
    'NEQ', 
    'LE', 
    'GE', 
    'LT', 
    'GT',
    'PLUS', 
    'MINUS', 
    'TIMES', 
    'DIVIDE', 
    'MODULO',
    'SEMICOLON'
]
# FIN aporte: BURGOS

# INICIO aporte: MORA
tokens_mora = [
    'MAPA',
    'FMT_PRINTLN',
    'FMT_SCANLN',
    'AND',
    'OR',
    'NOT',
    'PLUS_ASSIGN',
    'MINUS_ASSIGN',
    'INCREMENT',
    'DECREMENT',
    'AMPERSAND',
    'CORCHETE_IZQ',
    'CORCHETE_DER',
    'DOSPUNTOS',
    'COMA',
]
# FIN aporte: MORA

# Esta línea junta todo: las tres listas + los nombres del diccionario "reservadas"
tokens = tokens_andrade + tokens_burgos + tokens_mora + sorted(set(reservadas.values()))


# REGLAS COMO FUNCIÓN
# INICIO aporte: BURGOS (funciones)

def t_MALFORMED_NUMBER(t):
    r'(?:[0-9]+[a-zA-Z_]\w*)|(?:[0-9]+\.(?![0-9]))'
    registrar_error(t.lexer.lineno, f"Número mal formado {t.value}")

def t_FLOAT_LITERAL(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

# FIN aporte: BURGOS (funciones)

# INICIO aporte: MORA (funciones)

def t_MAPA(t):
    r'map\[(?:int|float64|string|bool)\](?:int|float64|string|bool)(?![a-zA-Z0-9_])'
    return t


def t_FMT_PRINTLN(t):
    r'fmt\.Println(?![a-zA-Z0-9_])'
    return t


def t_FMT_SCANLN(t):
    r'fmt\.Scanln(?![a-zA-Z0-9_])'
    return t

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
t_MATRIZ    = r'\[[0-9]+\]\[[0-9]+\](?:int|float64|string|bool)'

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

# Operadores logicos
t_AND = r'&&'
t_OR = r'\|\|'
t_NOT = r'!'

# Asignaciones compuestas
t_PLUS_ASSIGN = r'\+='
t_MINUS_ASSIGN = r'-='

# Incremento y decremento
t_INCREMENT = r'\+\+'
t_DECREMENT = r'--'

# Direccion de memoria
t_AMPERSAND = r'&'

# Delimitadores
t_CORCHETE_IZQ = r'\['
t_CORCHETE_DER = r'\]'
t_DOSPUNTOS = r':'
t_COMA = r','

# FIN aporte: MORA (cadenas)

# INICIO aporte: MORA (errores lexicos)

def t_error(t):
    caracter = t.value[0]
    registrar_error(t.lineno, f"Símbolo no reconocido {caracter}")
    t.lexer.skip(1)

# FIN aporte: MORA (errores lexicos)

# CONSTRUCCIÓN DEL LEXER
lexer = lex.lex()

def analizar(codigo):
    errores_lexicos.clear()
    lexer.lineno = 1
    lexer.input(codigo)
    reconocidos = [(tok.type, tok.value, tok.lineno) for tok in lexer]
    return reconocidos, list(errores_lexicos)