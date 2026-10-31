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

# INICIO aporte: ANDRADE
reservadas_andrade = {}
# FIN aporte: ANDRADE

# INICIO aporte: BURGOS
reservadas_burgos = {}
# FIN aporte: BURGOS

# INICIO aporte: MORA
reservadas_mora = {}
# FIN aporte: MORA

reservadas = {**reservadas_andrade, **reservadas_burgos, **reservadas_mora}


# --- LISTA DE TOKENS ---

# INICIO aporte: ANDRADE
tokens_andrade = []
# FIN aporte: ANDRADE

# INICIO aporte: BURGOS
tokens_burgos = []
# FIN aporte: BURGOS

# INICIO aporte: MORA
tokens_mora = []
# FIN aporte: MORA

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
# FIN aporte: ANDRADE (cadenas)

# INICIO aporte: BURGOS (cadenas)
# FIN aporte: BURGOS (cadenas)

# INICIO aporte: MORA (cadenas)
# FIN aporte: MORA (cadenas)