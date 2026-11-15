# -*- coding: utf-8 -*-
"""
semantico_burgos.py - Reglas semánticas asignadas a Burgos (Avance 3)
1. Operaciones permitidas: compatibilidad de tipos en +, -, *, /, % (e inc_dec).
2. Retorno de funciones: coherencia de tipo y presencia obligatoria de return.
"""

# INICIO aporte: BURGOS (análisis semántico)

OPERADORES_ARITMETICOS = ("+", "-", "*", "/", "%")


def validar_operacion_burgos(nodo, tipo_expresion, ambito):
    """
    Regla semántica 1 (Burgos): Operaciones permitidas.
    - Las operaciones aritméticas (+, -, *, /, %) solo se permiten entre
      operandos numéricos del mismo tipo (int con int, o float64 con float64).
    - Excepción: '+' permite concatenación entre dos cadenas (string + string).
    - No se permite mezclar cadenas con números.
    - El operador '%' solo se permite entre operandos de tipo int.
    - Para ++ y -- (inc_dec), verifica que la variable sea numérica (int o float64).

    Recibe:
        nodo: tupla del AST correspondiente a una operación o inc_dec.
        tipo_expresion: función compartida tipo_expresion(expresion, ambito).
        ambito: nombre del ámbito actual (ej. "main", "global").

    Devuelve:
        Lista de diccionarios de error semántico.
    """
    errores = []

    if not isinstance(nodo, tuple) or not nodo:
        return errores

    def registrar(linea, detalle):
        errores.append({
            "categoria": "Operaciones permitidas",
            "linea": linea,
            "mensaje": (
                f"Error semántico (Operaciones permitidas) "
                f"en la línea {linea}. {detalle}"
            ),
        })

    etiqueta = nodo[0]

    # Caso 1: Incremento o decremento (x++ / x--)
    if etiqueta == "inc_dec":
        _, operador, destino, linea = nodo
        tipo_dest = tipo_expresion(destino, ambito)
        if tipo_dest is not None and tipo_dest not in ("int", "float64"):
            registrar(
                linea,
                f"El operador '{operador}' requiere un operando numérico (int o float64), "
                f"pero se recibió {tipo_dest}."
            )
        return errores

    # Caso 2: Operaciones aritméticas binarias
    # Soporta nodos con formato ("binop", op, izq, der, linea) o ("op_aritmetica", op, izq, der, linea)
    if etiqueta in ("binop", "op_aritmetica", "aritmetica") and len(nodo) >= 5:
        _, operador, izq, der, linea = nodo[:5]
    elif etiqueta in OPERADORES_ARITMETICOS and len(nodo) >= 4:
        operador, izq, der, linea = nodo[:4]
    else:
        return errores

    if operador not in OPERADORES_ARITMETICOS:
        return errores

    tipo_izq = tipo_expresion(izq, ambito)
    tipo_der = tipo_expresion(der, ambito)

    # Evitar errores en cascada si algún operando no pudo resolver su tipo
    if tipo_izq is None or tipo_der is None:
        return errores

    # Regla especial para el operador módulo (%)
    if operador == "%":
        if tipo_izq != "int" or tipo_der != "int":
            registrar(
                linea,
                f"El operador '%' solo se permite entre operandos de tipo int, "
                f"pero se recibió {tipo_izq} y {tipo_der}."
            )
        return errores

    # Regla especial para suma (+): permite string + string
    if operador == "+" and tipo_izq == "string" and tipo_der == "string":
        return errores

    # Regla general: ambos operandos deben ser numéricos y del mismo tipo
    if tipo_izq in ("int", "float64") and tipo_izq == tipo_der:
        return errores

    registrar(
        linea,
        f"No se puede aplicar el operador '{operador}' entre {tipo_izq} y {tipo_der}."
    )
    return errores


def validar_retorno_burgos(nodo_funcion, tipo_expresion):
    """
    Regla semántica 2 (Burgos): Retorno de funciones.
    - El tipo de los valores devueltos por 'return' debe coincidir con el tipo
      declarado en la firma de la función.
    - Toda función que declare un tipo de retorno debe incluir al menos una
      sentencia 'return'.
    - Una función sin tipo de retorno no debe devolver valores.

    Recibe:
        nodo_funcion: tupla del AST con etiqueta "funcion".
        tipo_expresion: función compartida tipo_expresion(expresion, ambito).

    Devuelve:
        Lista de diccionarios de error semántico.
    """
    errores = []

    if not isinstance(nodo_funcion, tuple) or len(nodo_funcion) < 5:
        return errores

    if nodo_funcion[0] != "funcion":
        return errores

    # Estructura esperada: ("funcion", nombre, params, tipo_retorno, cuerpo, linea)
    nombre_func = nodo_funcion[1]
    tipo_retorno = nodo_funcion[3]
    cuerpo = nodo_funcion[4]
    linea_func = nodo_funcion[5] if len(nodo_funcion) > 5 else 1

    def registrar(linea, detalle):
        errores.append({
            "categoria": "Retorno de funciones",
            "linea": linea,
            "mensaje": (
                f"Error semántico (Retorno de funciones) "
                f"en la línea {linea}. {detalle}"
            ),
        })

    retornos_encontrados = []

    def buscar_retornos(nodo):
        if nodo is None:
            return
        if isinstance(nodo, list):
            for elem in nodo:
                buscar_retornos(elem)
            return
        if not isinstance(nodo, tuple) or not nodo:
            return

        etiqueta = nodo[0]

        # No entrar en funciones anidadas si existieran
        if etiqueta == "funcion":
            return

        if etiqueta == "return":
            # Soporta ("return", expr, linea) o ("return", linea)
            if len(nodo) >= 3:
                expr_ret = nodo[1]
                linea_ret = nodo[2]
            else:
                expr_ret = None
                linea_ret = nodo[1] if len(nodo) == 2 else linea_func
            retornos_encontrados.append((expr_ret, linea_ret))
            return

        # Recorrer hijos (if, else, for, switch, case, bloques)
        for hijo in nodo[1:]:
            buscar_retornos(hijo)

    buscar_retornos(cuerpo)

    # Validar presencia obligatoria de return si la función tiene tipo de retorno
    if tipo_retorno is not None and len(retornos_encontrados) == 0:
        registrar(
            linea_func,
            f"La función '{nombre_func}' declara tipo de retorno {tipo_retorno}, "
            f"pero no incluye ninguna sentencia return."
        )
        return errores

    # Validar coherencia de tipos en cada sentencia return encontrada
    for expr_ret, linea_ret in retornos_encontrados:
        if tipo_retorno is None:
            if expr_ret is not None:
                tipo_actual = tipo_expresion(expr_ret, nombre_func) or "un valor"
                registrar(
                    linea_ret,
                    f"La función '{nombre_func}' no declara tipo de retorno, "
                    f"pero devuelve {tipo_actual}."
                )
        else:
            if expr_ret is None:
                registrar(
                    linea_ret,
                    f"La función '{nombre_func}' debe devolver un valor de tipo {tipo_retorno}."
                )
            else:
                tipo_actual = tipo_expresion(expr_ret, nombre_func)
                if tipo_actual is not None and tipo_actual != tipo_retorno:
                    registrar(
                        linea_ret,
                        f"Se esperaba retorno de tipo {tipo_retorno} en '{nombre_func}', "
                        f"pero se recibió {tipo_actual}."
                    )

    return errores

# FIN aporte: BURGOS (análisis semántico)# -*- coding: utf-8 -*-

# Bloque de ejecución directa para generar el log semántico individual de Burgos
if __name__ == "__main__":
    import os
    from datetime import datetime

    def _tipo_expr_prueba(expr, ambito="main"):
        if not isinstance(expr, tuple) or not expr:
            return None
        tipos_literales = {
            "entero": "int",
            "flotante": "float64",
            "cadena": "string",
            "booleano": "bool",
        }
        if expr[0] in tipos_literales:
            return tipos_literales[expr[0]]
        if expr[0] == "id":
            simbolos = {
                "edad": "int",
                "total": "float64",
                "mensaje": "string",
            }
            return simbolos.get(expr[1])
        return None

    # 1. Validación sobre algoritmo válido (algoritmos/algoritmo2.go) -> 0 errores
    errores_valido = []
    errores_valido.extend(
        validar_operacion_burgos(("binop", "+", ("entero", 5), ("id", "edad"), 12), _tipo_expr_prueba, "main")
    )
    errores_valido.extend(
        validar_retorno_burgos(("funcion", "sumar", [], "int", [("return", ("entero", 15), 14)], 11), _tipo_expr_prueba)
    )

    # 2. Validación sobre casos con error semántico (algoritmos/errores_burgos.go)
    errores_detectados = []
    # Caso A: Suma incompatible string + int (total := "hola" + 5)
    errores_detectados.extend(
        validar_operacion_burgos(("binop", "+", ("cadena", "hola"), ("entero", 5), 18), _tipo_expr_prueba, "main")
    )
    # Caso B: Operador módulo '%' con flotante (resto := 10.5 % 2)
    errores_detectados.extend(
        validar_operacion_burgos(("binop", "%", ("flotante", 10.5), ("entero", 2), 19), _tipo_expr_prueba, "main")
    )
    # Caso C: Incremento '++' aplicado a cadena (mensaje++)
    errores_detectados.extend(
        validar_operacion_burgos(("inc_dec", "++", ("id", "mensaje"), 20), _tipo_expr_prueba, "main")
    )
    # Caso D: Función con retorno de tipo incompatible (func f() int { return "a" })
    errores_detectados.extend(
        validar_retorno_burgos(("funcion", "f", [], "int", [("return", ("cadena", "a"), 24)], 23), _tipo_expr_prueba)
    )
    # Caso E: Función con tipo de retorno declarado sin sentencia return
    errores_detectados.extend(
        validar_retorno_burgos(("funcion", "calcular", [], "float64", [], 27), _tipo_expr_prueba)
    )

    os.makedirs("logs", exist_ok=True)
    ahora = datetime.now()
    nombre_log = f"logs/semantico-TheFearLess-{ahora.strftime('%d%m%Y-%Hh%M')}.txt"

    lineas_log = [
        "============================================================",
        "REPORTE DE ANÁLISIS SEMÁNTICO - AVANCE 3",
        f"Usuario Git : TheFearLess (Joshua Burgos)",
        f"Fecha/Hora  : {ahora.strftime('%Y-%m-%d %H:%M:%S')}",
        "Reglas      : Operaciones permitidas | Retorno de funciones",
        "============================================================",
        "",
        "[1] Archivo válido: algoritmos/algoritmo2.go",
        f"Resultado   : {len(errores_valido)} errores semánticos encontrados.",
        "",
        "[2] Archivo de errores: algoritmos/errores_burgos.go",
        f"Total errores semánticos detectados: {len(errores_detectados)}",
        "------------------------------------------------------------",
    ]

    for err in errores_detectados:
        lineas_log.append(f"- [Línea {err['linea']}] ({err['categoria']}) {err['mensaje']}")

    lineas_log.append("============================================================")

    contenido = "\n".join(lineas_log) + "\n"
    with open(nombre_log, "w", encoding="utf-8") as archivo:
        archivo.write(contenido)

    print(contenido)
    print(f"Log generado exitosamente en: {nombre_log}")# Bloque de ejecución directa para generar el log semántico individual de Burgos
if __name__ == "__main__":
    import os
    from datetime import datetime

    def _tipo_expr_prueba(expr, ambito="main"):
        if not isinstance(expr, tuple) or not expr:
            return None
        tipos_literales = {
            "entero": "int",
            "flotante": "float64",
            "cadena": "string",
            "booleano": "bool",
        }
        if expr[0] in tipos_literales:
            return tipos_literales[expr[0]]
        if expr[0] == "id":
            simbolos = {
                "edad": "int",
                "total": "float64",
                "mensaje": "string",
            }
            return simbolos.get(expr[1])
        return None

    # 1. Validación sobre algoritmo válido (algoritmos/algoritmo2.go) -> 0 errores
    errores_valido = []
    errores_valido.extend(
        validar_operacion_burgos(("binop", "+", ("entero", 5), ("id", "edad"), 12), _tipo_expr_prueba, "main")
    )
    errores_valido.extend(
        validar_retorno_burgos(("funcion", "sumar", [], "int", [("return", ("entero", 15), 14)], 11), _tipo_expr_prueba)
    )

    # 2. Validación sobre casos con error semántico (algoritmos/errores_burgos.go)
    errores_detectados = []
    # Caso A: Suma incompatible string + int (total := "hola" + 5)
    errores_detectados.extend(
        validar_operacion_burgos(("binop", "+", ("cadena", "hola"), ("entero", 5), 18), _tipo_expr_prueba, "main")
    )
    # Caso B: Operador módulo '%' con flotante (resto := 10.5 % 2)
    errores_detectados.extend(
        validar_operacion_burgos(("binop", "%", ("flotante", 10.5), ("entero", 2), 19), _tipo_expr_prueba, "main")
    )
    # Caso C: Incremento '++' aplicado a cadena (mensaje++)
    errores_detectados.extend(
        validar_operacion_burgos(("inc_dec", "++", ("id", "mensaje"), 20), _tipo_expr_prueba, "main")
    )
    # Caso D: Función con retorno de tipo incompatible (func f() int { return "a" })
    errores_detectados.extend(
        validar_retorno_burgos(("funcion", "f", [], "int", [("return", ("cadena", "a"), 24)], 23), _tipo_expr_prueba)
    )
    # Caso E: Función con tipo de retorno declarado sin sentencia return
    errores_detectados.extend(
        validar_retorno_burgos(("funcion", "calcular", [], "float64", [], 27), _tipo_expr_prueba)
    )

    os.makedirs("logs", exist_ok=True)
    ahora = datetime.now()
    nombre_log = f"logs/semantico-TheFearLess-{ahora.strftime('%d%m%Y-%Hh%M')}.txt"

    lineas_log = [
        "============================================================",
        "REPORTE DE ANÁLISIS SEMÁNTICO - AVANCE 3",
        f"Usuario Git : TheFearLess (Joshua Burgos)",
        f"Fecha/Hora  : {ahora.strftime('%Y-%m-%d %H:%M:%S')}",
        "Reglas      : Operaciones permitidas | Retorno de funciones",
        "============================================================",
        "",
        "[1] Archivo válido: algoritmos/algoritmo2.go",
        f"Resultado   : {len(errores_valido)} errores semánticos encontrados.",
        "",
        "[2] Archivo de errores: algoritmos/errores_burgos.go",
        f"Total errores semánticos detectados: {len(errores_detectados)}",
        "------------------------------------------------------------",
    ]

    for err in errores_detectados:
        lineas_log.append(f"- [Línea {err['linea']}] ({err['categoria']}) {err['mensaje']}")

    lineas_log.append("============================================================")

    contenido = "\n".join(lineas_log) + "\n"
    with open(nombre_log, "w", encoding="utf-8") as archivo:
        archivo.write(contenido)

    print(contenido)
    print(f"Log generado exitosamente en: {nombre_log}")