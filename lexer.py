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


# --- PALABRAS RESERVADAS Y TIPOS ---
# Diccionario: texto que aparece en el código -> nombre del token.
# Los nombres de este diccionario pasan solos a la lista "tokens" (ver más abajo).

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
reservadas_burgos = {}
# FIN aporte: BURGOS

# INICIO aporte: MORA
reservadas_mora = {}
# FIN aporte: MORA

reservadas = {**reservadas_andrade, **reservadas_burgos, **reservadas_mora}


# --- LISTA DE TOKENS ---
# Aquí van solo los tokens que NO salen del diccionario de arriba (ID, ENTERO, CADENA...).

# INICIO aporte: ANDRADE
tokens_andrade = [
    'ID', 'ENTERO', 'CADENA', 'ARREGLO',
    'ASIGNACION', 'DECLARACION_CORTA',
    'LLAVE_IZQ', 'LLAVE_DER', 'PAREN_IZQ', 'PAREN_DER',
    'NEWLINE',
]
# FIN aporte: ANDRADE

# INICIO aporte: BURGOS
tokens_burgos = []
# FIN aporte: BURGOS

# INICIO aporte: MORA
tokens_mora = []
# FIN aporte: MORA

# Esta línea junta todo: las tres listas + los nombres del diccionario "reservadas"
tokens = tokens_andrade + tokens_burgos + tokens_mora + sorted(set(reservadas.values()))


# --- REGLAS COMO FUNCIÓN ---

# INICIO aporte: BURGOS (funciones)
# FIN aporte: BURGOS (funciones)

# INICIO aporte: MORA (funciones)
# FIN aporte: MORA (funciones)

# INICIO aporte: ANDRADE (funciones)
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
# FIN aporte: BURGOS (cadenas)

# INICIO aporte: MORA (cadenas)
# FIN aporte: MORA (cadenas)