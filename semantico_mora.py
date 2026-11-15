
# -*- coding: utf-8 -*-

# INICIO aporte: MORA (análisis semántico)
# Regla 2: break solo puede aparecer dentro de for o switch.


def validar_break(arbol):
    """
    Recorre el AST y detecta break fuera de for o switch.

    Devuelve una lista de errores semánticos.
    """
    errores = []

    def recorrer(nodo, profundidad_control=0):
        if nodo is None:
            return

        if isinstance(nodo, list):
            for elemento in nodo:
                recorrer(elemento, profundidad_control)
            return

        if not isinstance(nodo, tuple) or not nodo:
            return

        etiqueta = nodo[0]

        if etiqueta == "programa":
            recorrer(nodo[3], 0)

        elif etiqueta == "funcion":
            # Cada función comienza con un contexto independiente.
            recorrer(nodo[4], 0)

        elif etiqueta == "break":
            linea = nodo[1]

            if profundidad_control == 0:
                errores.append({
                    "categoria": "Estructuras de control",
                    "linea": linea,
                    "mensaje": (
                        f"Error semántico (Estructuras de control) "
                        f"en la línea {linea}. "
                        "break solo puede utilizarse dentro de "
                        "un for o switch."
                    ),
                })

        elif etiqueta == "for":
            # Solo el cuerpo queda dentro del contexto del for.
            recorrer(nodo[4], profundidad_control + 1)

        elif etiqueta == "switch":
            # Los case y default pertenecen al switch.
            recorrer(nodo[2], profundidad_control + 1)

        elif etiqueta == "case":
            recorrer(nodo[2], profundidad_control)

        elif etiqueta == "default":
            recorrer(nodo[1], profundidad_control)

        elif etiqueta == "if":
            # Un if NO habilita break por sí mismo.
            recorrer(nodo[2], profundidad_control)
            recorrer(nodo[3], profundidad_control)

    recorrer(arbol)
    return errores


# Regla semántica de Mora:
# Asignación estricta e inmutabilidad de constantes.
#
# No crea ni mantiene una tabla de símbolos propia.
# Recibe dos funciones proporcionadas por el analizador compartido:
#
# buscar_simbolo(nombre, ambito)
# tipo_expresion(expresion, ambito)


def validar_asignacion_mora(
    nodo,
    buscar_simbolo,
    tipo_expresion,
    ambito
):
    """
    Comprueba una declaración, asignación o modificación.

    buscar_simbolo devuelve un registro como:
        {"tipo": "int", "constante": True}
    o None si el identificador no existe.

    tipo_expresion devuelve el tipo como texto o None
    cuando no puede determinarlo.

    La gestión de ámbitos y la tabla de símbolos
    pertenecen al analizador compartido.
    """
    errores = []

    if not isinstance(nodo, tuple) or not nodo:
        return errores

    etiqueta = nodo[0]

    def registrar(linea, detalle):
        errores.append({
            "categoria": "Asignación de tipo",
            "linea": linea,
            "mensaje": (
                f"Error semántico (Asignación de tipo) "
                f"en la línea {linea}. {detalle}"
            ),
        })

    def comprobar_tipos(tipo_destino, valor, linea):
        if tipo_destino is None or valor is None:
            return

        tipo_valor = tipo_expresion(valor, ambito)

        # No generar errores falsos si el tipo es desconocido.
        if tipo_valor is None:
            return

        if tipo_destino != tipo_valor:
            registrar(
                linea,
                f"Se esperaba {tipo_destino}, "
                f"pero se recibió {tipo_valor}."
            )

    # Declaraciones con tipo explícito.
    if etiqueta in ("var", "const"):
        _, nombre, tipo, valor, linea = nodo
        comprobar_tipos(tipo, valor, linea)
        return errores

    # Declaración corta: el tipo se infiere del valor.
    # La creación del símbolo corresponde a Andrade.
    if etiqueta == "decl_corta":
        return errores

    # Asignación normal.
    if etiqueta == "asignacion":
        destino, valor, linea = nodo[1:]

    # Asignación compuesta: += o -=
    elif etiqueta == "asig_comp":
        _, operador, destino, valor, linea = nodo

    # Incremento o decremento: ++ o --
    elif etiqueta == "inc_dec":
        _, operador, destino, linea = nodo
        valor = None

    else:
        return errores

    # Destinos válidos: variable o acceso a un elemento.
    if not isinstance(destino, tuple) or not destino:
        return errores

    if destino[0] == "id":
        nombre = destino[1]
        tipo_elemento = None

    elif destino[0] == "acceso":
        nombre = destino[1]

        # El resolvedor compartido determina el tipo
        # del elemento (mapa, arreglo o matriz).
        tipo_elemento = tipo_expresion(destino, ambito)

    else:
        return errores

    simbolo = buscar_simbolo(nombre, ambito)

    # Los identificadores inexistentes los valida Andrade.
    if simbolo is None:
        return errores

    if simbolo.get("constante", False):
        registrar(
            linea,
            f"No se puede modificar la constante {nombre}."
        )
        return errores

    # El tipo de una variable es el registrado en la tabla.
    # El tipo de un acceso es el de su elemento.
    tipo_destino = (
        simbolo.get("tipo")
        if destino[0] == "id"
        else tipo_elemento
    )

    # ++ y -- no tienen valor a la derecha.
    # Sus restricciones numéricas corresponden a Burgos.
    if etiqueta == "inc_dec":
        return errores

    comprobar_tipos(tipo_destino, valor, linea)
    return errores


# FIN aporte: MORA (análisis semántico)
