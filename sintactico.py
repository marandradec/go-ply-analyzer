import ply.yacc as yacc
import datetime
import os
from lexer import tokens

# Estructura general del programa (coordinada para que sirva a todos)
def p_programa(p):
    '''programa : sentencias'''
    pass

def p_sentencias(p):
    '''sentencias : sentencia sentencias
                  | sentencia'''
    pass

def p_sentencia(p):
    '''sentencia : declaracion_burgos
                 | bucle_for_burgos
                 | sentencia_break_burgos
                 | expresion_aritmetica
                 | condicion_burgos'''
    pass

# ==========================================
# INICIO aporte: BURGOS (Analizador Sintáctico)
# ==========================================

# 1. Asignación de variables (var y const) y Estructura de datos (Matriz)
def p_declaracion_burgos(p):
    '''declaracion_burgos : VAR ID tipo_burgos ASIGNACION expresion_aritmetica
                          | CONST ID tipo_burgos ASIGNACION expresion_aritmetica
                          | VAR ID MATRIZ
                          | CONST ID MATRIZ'''
    pass

def p_tipo_burgos(p):
    '''tipo_burgos : T_FLOAT64'''
    pass

# 2. Estructuras de control (for y break)
def p_bucle_for_burgos(p):
    '''bucle_for_burgos : FOR condicion_burgos LLAVE_IZQ sentencias LLAVE_DER
                        | FOR ID DECLARACION_CORTA expresion_aritmetica SEMICOLON condicion_burgos SEMICOLON expresion_aritmetica LLAVE_IZQ sentencias LLAVE_DER'''
    pass

def p_sentencia_break_burgos(p):
    '''sentencia_break_burgos : BREAK'''
    pass

# 3. Expresiones aritméticas y booleanas
def p_expresion_aritmetica(p):
    '''expresion_aritmetica : expresion_aritmetica PLUS termino
                            | expresion_aritmetica MINUS termino
                            | termino'''
    pass

def p_termino(p):
    '''termino : termino TIMES factor
               | termino DIVIDE factor
               | termino MODULO factor
               | factor'''
    pass

def p_factor(p):
    '''factor : FLOAT_LITERAL
              | ID'''
    # Nota: Aquí después se agregará ENTERO de Andrade
    pass

def p_condicion_burgos(p):
    '''condicion_burgos : expresion_aritmetica EQ expresion_aritmetica
                        | expresion_aritmetica NEQ expresion_aritmetica
                        | expresion_aritmetica LE expresion_aritmetica
                        | expresion_aritmetica GE expresion_aritmetica
                        | expresion_aritmetica LT expresion_aritmetica
                        | expresion_aritmetica GT expresion_aritmetica'''
    pass

# ==========================================
# FIN aporte: BURGOS (Analizador Sintáctico)
# ==========================================

# --- Funciones de error y generación de LOG (Obligatorio) ---
def p_error(p):
    if p:
        mensaje = f"Error sintactico de tipo {p.type} en el valor '{p.value}', linea {p.lineno}"
    else:
        mensaje = "Error sintactico: Fin de archivo inesperado (EOF)"
    
    print(mensaje)
    generar_log_sintactico(mensaje)

def generar_log_sintactico(mensaje_error):
    if not os.path.exists('logs'):
        os.makedirs('logs')
        
    fecha_hora = datetime.datetime.now().strftime("%Y%m%d-%Hh%M")
    nombre_archivo = f"logs/sintactico-JoshuaBurgos-{fecha_hora}.txt"
    
    with open(nombre_archivo, 'a', encoding='utf-8') as archivo:
        archivo.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {mensaje_error}\n")
    print(f"Log guardado en: {nombre_archivo}")

parser = yacc.yacc()

# --- Zona de pruebas manuales por terminal ---
if __name__ == '__main__':
    while True:
        try:
            s = input('Prueba sintáctica > ')
        except EOFError:
            break
        if not s: continue
        resultado = parser.parse(s)
        if resultado is None:
            print("Analisis terminado (Sin errores devueltos por el parser principal).")