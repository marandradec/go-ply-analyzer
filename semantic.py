# -*- coding: utf-8 -*-
"""
ANALIZADOR SEMÁNTICO (Avance 3) - subconjunto de Go
"""

import re
import sys
from pathlib import Path

# INICIO aporte: ANDRADE (tabla de símbolos, recorrido del árbol e identificadores)

NUMERICOS = ("int", "float64")

_RE_COLECCION = re.compile(r"^\[\d+\](.+)$")      # [3]int -> int   [2][2]int -> [2]int
_RE_MAPA = re.compile(r"^map\[[^\]]+\](.+)$")     # map[string]int -> int
_RE_TAMANO = re.compile(r"^\[(\d+)\](.+)$")        # [3]int -> (3, int)
_RE_MAPA_KV = re.compile(r"^map\[([^\]]+)\](.+)$")  # map[string]int -> (string, int)


def tipo_elemento(tipo):
    """Tipo que se obtiene al indexar un arreglo, una matriz o un mapa (None si no se puede)."""
    if tipo is None:
        return None
    m = _RE_COLECCION.match(tipo) or _RE_MAPA.match(tipo)
    return m.group(1) if m else None


def tipo_clave(tipo):
    """Tipo del índice o la clave: int para arreglos y matrices, el tipo de la clave en un mapa."""
    if tipo is None:
        return None
    if _RE_TAMANO.match(tipo):
        return "int"
    m = _RE_MAPA_KV.match(tipo)
    return m.group(1) if m else None


def tamano_coleccion(tipo):
    """Cantidad de elementos de un arreglo o de una fila de matriz (None si no aplica)."""
    m = _RE_TAMANO.match(tipo) if tipo else None
    return int(m.group(1)) if m else None


def linea_de(nodo, por_defecto):
    """Línea de un nodo de expresión (el último elemento de la tupla), o la dada si no la tiene."""
    if isinstance(nodo, tuple) and nodo and isinstance(nodo[-1], int):
        return nodo[-1]
    return por_defecto


class Simbolo:
    """Una entrada de la tabla. Guarda nombre, tipo, ámbito, si es constante y su línea."""

    def __init__(self, nombre, tipo, linea, clase="variable", constante=False,
                 parametros=None, retorno=None):
        self.nombre = nombre
        self.tipo = tipo                  # tipo del valor (None si no se pudo inferir)
        self.linea = linea
        self.clase = clase                # variable, constante, parámetro o función
        self.constante = constante
        self.parametros = parametros or []  # solo funciones, lista de (nombre, tipo)
        self.retorno = retorno              # solo funciones, tipo de retorno o None
        self.ambito = None

    def descripcion_tipo(self):
        if self.clase == "función":
            params = ", ".join(t for _, t in self.parametros)
            return f"({params}) {self.retorno}" if self.retorno else f"({params})"
        return self.tipo or "desconocido"


class TablaSimbolos:
    """Ámbito global (funciones) y, dentro de cada función, una pila de bloques.

    Los parámetros y el cuerpo de la función comparten el primer bloque; cada if, else, for y
    case abre uno nuevo. Un nombre puede repetirse en bloques distintos (o taparse en uno
    interior, como en Go), pero no dos veces en el mismo bloque."""

    GLOBAL = "global"

    def __init__(self):
        self.globales = {}
        self.pila = []                    # bloques de la función actual, el último es el más interno
        self.registro = []                # todos los símbolos, en orden de declaración (para mostrar)
        self.nombres = {self.GLOBAL}
        self.actual = self.GLOBAL

    def entrar(self, nombre):
        clave, n = nombre, 2
        while clave in self.nombres:      # función declarada dos veces
            clave = f"{nombre}#{n}"
            n += 1
        self.nombres.add(clave)
        self.pila = [{}]
        self.actual = clave

    def salir(self):
        self.pila = []
        self.actual = self.GLOBAL

    def abrir_bloque(self):
        if self.actual != self.GLOBAL:
            self.pila.append({})

    def cerrar_bloque(self):
        if self.actual != self.GLOBAL and len(self.pila) > 1:
            self.pila.pop()

    def _bloque_actual(self):
        return self.pila[-1] if self.actual != self.GLOBAL else self.globales

    def declarar(self, simbolo):
        """Registra el símbolo en el bloque actual. False si el nombre ya existe en él."""
        bloque = self._bloque_actual()
        if simbolo.nombre in bloque:
            return False
        simbolo.ambito = self.actual
        bloque[simbolo.nombre] = simbolo
        self.registro.append(simbolo)
        return True

    def buscar_local(self, nombre):
        return self._bloque_actual().get(nombre)

    def buscar(self, nombre):
        """Busca del bloque más interno hacia afuera y al final en el ámbito global."""
        for bloque in reversed(self.pila):
            if nombre in bloque:
                return bloque[nombre]
        return self.globales.get(nombre)

    def buscar_funcion(self, nombre):
        simbolo = self.globales.get(nombre)
        return simbolo if simbolo is not None and simbolo.clase == "función" else None

    def simbolos(self):
        return list(self.registro)

    def filas(self):
        """Filas para mostrar la tabla (interfaz y logs)."""
        return [(s.ambito, s.nombre, s.clase, s.descripcion_tipo(),
                 "sí" if s.constante else "no", s.linea) for s in self.simbolos()]


class AnalizadorSemantico:
    """Recorre el AST, mantiene la tabla de símbolos y acumula los errores semánticos."""

    def __init__(self):
        self.tabla = TablaSimbolos()
        self.errores = []
        self.funcion = None      # (nombre, tipo de retorno) de la función que se recorre
        self.nivel_ciclo = 0     # cantidad de for y switch abiertos en este momento
        self.hay_return = False  # la función actual ya tiene al menos un return

    # Registro de errores

    def error(self, categoria, regla, linea, detalle):
        self.errores.append({
            "linea": linea,
            "categoria": categoria,
            "regla": regla,
            "mensaje": f"Error semántico ({categoria}) en la línea {linea}. {detalle}",
        })

    # REGLA SEMÁNTICA 1 (Andrade). Identificadores, Inexistencia.
    # Toda variable o función utilizada debe existir en un ámbito visible de la tabla.
    # Ejemplo de error a detectar   y = 10   (sin haber declarado y)
    def buscar_variable(self, nombre, linea):
        if nombre == "_":                     # el identificador en blanco solo recibe valores
            self.error("Identificadores", "Inexistencia", linea,
                       "El identificador _ no puede usarse como valor")
            return None
        simbolo = self.tabla.buscar(nombre)
        if simbolo is None:
            self.error("Identificadores", "Inexistencia", linea,
                       f"La variable {nombre} no fue declarada")
        elif simbolo.clase == "función":      # existe, pero no es una variable
            self.error("Identificadores", "Inexistencia", linea,
                       f"{nombre} es una función y no puede usarse como variable")
            return None
        return simbolo

    def buscar_funcion(self, nombre, linea):
        simbolo = self.tabla.buscar(nombre)   # el símbolo visible más cercano, como en Go
        if simbolo is not None and simbolo.clase == "función":
            return simbolo
        if simbolo is not None:               # existe, pero no es una función
            detalle = f"{nombre} es una variable y no puede llamarse como función"
            if self.tabla.buscar_funcion(nombre) is not None:
                detalle += f" (tapa a la función {nombre} declarada en el ámbito global)"
        else:
            detalle = f"La función {nombre} no fue declarada"
        self.error("Identificadores", "Inexistencia", linea, detalle)
        return None

    # REGLA SEMÁNTICA 2 (Andrade). Identificadores, Duplicidad.
    # Al declarar con var, const o := (también parámetros y funciones) el nombre no debe
    # existir ya en el mismo ámbito. Ejemplo de error a detectar
    #   var x int = 1
    #   var x string = "dos"
    def declarar(self, nombre, tipo, linea, clase="variable", constante=False):
        simbolo = Simbolo(nombre, tipo, linea, clase=clase, constante=constante)
        if nombre == "_":                     # identificador en blanco: no se guarda y puede repetirse
            return simbolo
        if not self.tabla.declarar(simbolo):
            previo = self.tabla.buscar_local(nombre)
            self.error("Identificadores", "Duplicidad", linea,
                       f"El nombre {nombre} ya fue declarado en este ámbito (línea {previo.linea})")
        return simbolo

    def declarar_funcion(self, nodo):
        _, nombre, params, retorno, _, linea = nodo
        simbolo = Simbolo(nombre, retorno, linea, clase="función", parametros=params, retorno=retorno)
        if nombre == "_":                     # func _() puede aparecer varias veces
            return
        if not self.tabla.declarar(simbolo):
            previo = self.tabla.buscar_local(nombre)
            self.error("Identificadores", "Duplicidad", linea,
                       f"La función {nombre} ya fue declarada (línea {previo.linea})")

    # Recorrido del programa

    def analizar(self, arbol):
        funciones = arbol[3] if arbol else []
        for f in funciones:               # primero todas las firmas, así se puede llamar
            self.declarar_funcion(f)      # a una función declarada más abajo
        for f in funciones:
            self.visitar_funcion(f)
        self.errores.sort(key=lambda e: e["linea"])  # estable, conserva el orden dentro de la línea

    def visitar_funcion(self, nodo):
        _, nombre, params, retorno, cuerpo, linea = nodo
        self.tabla.entrar(nombre)
        self.funcion = (nombre, retorno)
        self.nivel_ciclo = 0
        self.hay_return = False
        for pnombre, ptipo in params:
            self.declarar(pnombre, ptipo, linea, clase="parámetro")
        for sentencia in cuerpo:
            self.visitar(sentencia)
        verificar_return_presente(self, nodo)       # regla de Burgos
        self.tabla.salir()
        self.funcion = None

    def visitar(self, nodo):
        if not isinstance(nodo, tuple) or not nodo:
            return
        manejador = getattr(self, "_s_" + str(nodo[0]), None)
        if manejador:                     # los nodos de recuperación de errores se ignoran
            manejador(nodo)

    def visitar_bloque(self, sentencias):
        for s in sentencias or []:
            self.visitar(s)

    # Sentencias

    def _s_decl_corta(self, n):
        _, nombre, valor, linea = n
        tipo = self.tipo_de(valor)                 # el valor se evalúa antes de declarar el nombre
        if nombre == "_":                          # _ := valor no declara nada nuevo (error en Go)
            self.error("Identificadores", "Duplicidad", linea,
                       "No hay variables nuevas a la izquierda de :=, el identificador _ no declara ningún nombre")
            return
        self.declarar(nombre, tipo, linea)

    def _s_var(self, n):
        _, nombre, tipo, valor, linea = n
        if valor is not None:
            verificar_asignacion(self, tipo, self.tipo_de(valor), linea, f"la variable {nombre}")   # Mora
        self.declarar(nombre, tipo, linea)

    def _s_const(self, n):
        _, nombre, tipo, valor, linea = n
        verificar_asignacion(self, tipo, self.tipo_de(valor), linea, f"la constante {nombre}")      # Mora
        self.verificar_valor_constante(nombre, valor, linea)
        self.declarar(nombre, tipo, linea, clase="constante", constante=True)

    def _s_asignacion(self, n):
        _, destino, valor, linea = n
        tipo_valor = self.tipo_de(valor)
        if destino[0] == "id" and destino[1] == "_":   # _ = valor descarta el valor, es válido
            return
        simbolo, tipo_destino, etiqueta = self.destino(destino)
        if verificar_constante(self, simbolo, linea):                                               # Mora
            return
        verificar_asignacion(self, tipo_destino, tipo_valor, linea, etiqueta)                       # Mora

    def _s_asig_comp(self, n):
        _, op, destino, valor, linea = n
        tipo_valor = self.tipo_de(valor)
        simbolo, tipo_destino, _ = self.destino(destino)
        if verificar_constante(self, simbolo, linea):                                               # Mora
            return
        verificar_operandos(self, op[0], tipo_destino, tipo_valor, linea)                           # Burgos

    def _s_inc_dec(self, n):
        _, op, destino, linea = n
        simbolo, tipo_destino, _ = self.destino(destino)
        if verificar_constante(self, simbolo, linea):                                               # Mora
            return
        verificar_incremento(self, op, tipo_destino, linea)                                         # Burgos

    def _s_leer(self, n):
        _, nombre, linea = n
        simbolo = self.buscar_variable(nombre, linea)
        verificar_constante(self, simbolo, linea)                                                   # Mora

    def _s_imprimir(self, n):
        for argumento in n[1]:
            self.tipo_de(argumento)

    def _s_llamada(self, n):
        self.tipo_llamada(n, como_valor=False)

    def _s_return(self, n):
        verificar_return(self, n)                                                                   # Burgos

    def _s_break(self, n):
        verificar_break(self, n[1])                                                                 # Mora

    def _s_if(self, n):
        _, condicion, bloque, resto, linea = n
        verificar_condicion(self, self.tipo_de(condicion), linea, "if")                             # Mora
        self.bloque(bloque)
        if isinstance(resto, list):
            self.bloque(resto)
        elif isinstance(resto, tuple):
            self.visitar(resto)

    def _s_for(self, n):
        _, inicio, condicion, posterior, bloque, linea = n
        self.tabla.abrir_bloque()                  # la variable del for solo existe dentro del for
        self.visitar(inicio)
        if condicion is not None:
            verificar_condicion(self, self.tipo_de(condicion), linea, "for")                        # Mora
        self.visitar(posterior)
        self.nivel_ciclo += 1
        self.bloque(bloque)
        self.nivel_ciclo -= 1
        self.tabla.cerrar_bloque()

    def _s_switch(self, n):
        _, expresion, casos, _ = n
        tipo_switch = self.tipo_de(expresion)
        vistos = {}                                # valores constantes ya usados en un case
        self.nivel_ciclo += 1
        for caso in casos:
            if caso[0] == "case":
                for valor in caso[1]:
                    verificar_case(self, tipo_switch, self.tipo_de(valor), valor, vistos, caso[3])  # Mora
                self.bloque(caso[2])
            elif caso[0] == "default":
                self.bloque(caso[1])
        self.nivel_ciclo -= 1

    def bloque(self, sentencias):
        """Recorre las sentencias de un bloque { ... } en un ámbito propio."""
        self.tabla.abrir_bloque()
        self.visitar_bloque(sentencias)
        self.tabla.cerrar_bloque()

    # Una constante solo puede inicializarse con literales u otras constantes
    def verificar_valor_constante(self, nombre, valor, linea):
        culpable = self._no_constante(valor)
        if culpable:
            self.error("Asignación de tipo", "Asignación estricta", linea,
                       f"La constante {nombre} solo puede inicializarse con valores constantes, y {culpable} no lo es")

    def _no_constante(self, e):
        """Texto de la primera parte no constante de la expresión, o None si es constante."""
        if not isinstance(e, tuple) or not e:
            return None
        clase = e[0]
        if clase == "id":
            simbolo = self.tabla.buscar(e[1])
            if simbolo is None or simbolo.constante:
                return None
            return f"la función {e[1]}" if simbolo.clase == "función" else f"la variable {e[1]}"
        if clase == "llamada":
            return f"la llamada a {e[1]}"
        if clase == "acceso":
            return f"el acceso a un elemento de {self._raiz(e)}"
        if clase in ("arreglo", "matriz", "mapa"):
            return f"el literal de {clase}"
        if clase in ("neg", "not"):
            return self._no_constante(e[1])
        if clase == "binop":
            return self._no_constante(e[2]) or self._no_constante(e[3])
        return None

    # Destinos de una asignación (variable o elemento de arreglo, matriz o mapa)

    def destino(self, nodo):
        """Devuelve (símbolo, tipo del destino, texto para el mensaje)."""
        if nodo[0] == "id":
            simbolo = self.buscar_variable(nodo[1], nodo[2])
            return simbolo, (simbolo.tipo if simbolo else None), f"la variable {nodo[1]}"
        return None, self.tipo_acceso(nodo), f"un elemento de {self._raiz(nodo)}"

    @staticmethod
    def _raiz(acceso):
        while not isinstance(acceso, str):
            acceso = acceso[1]
        return acceso

    # Tipos de las expresiones

    def tipo_de(self, e):
        """Tipo de una expresión (None si es desconocido). Recorre todo el árbol de la expresión
        para detectar identificadores sin declarar."""
        if not isinstance(e, tuple) or not e:
            return None
        clase = e[0]
        if clase == "entero":
            return "int"
        if clase == "flotante":
            return "float64"
        if clase == "cadena":
            return "string"
        if clase == "booleano":
            return "bool"
        if clase == "id":
            simbolo = self.buscar_variable(e[1], e[2])
            return simbolo.tipo if simbolo else None
        if clase == "acceso":
            return self.tipo_acceso(e)
        if clase == "llamada":
            return self.tipo_llamada(e)
        if clase == "neg":
            return verificar_signo_negativo(self, self.tipo_de(e[1]), e[2])                         # Burgos
        if clase == "not":
            return verificar_negacion(self, self.tipo_de(e[1]), e[2])                               # Burgos
        if clase == "binop":
            _, op, izq, der, linea = e
            tipo_izq, tipo_der = self.tipo_de(izq), self.tipo_de(der)
            if op in ("+", "-", "*", "/", "%"):
                return verificar_operandos(self, op, tipo_izq, tipo_der, linea)                     # Burgos
            if op in ("&&", "||"):
                return verificar_logico(self, op, tipo_izq, tipo_der, linea)                        # Burgos
            return verificar_comparacion(self, op, tipo_izq, tipo_der, linea)                       # Burgos
        if clase in ("arreglo", "matriz", "mapa"):
            return verificar_literal(self, e)                                                       # Mora
        return None

    def tipo_acceso(self, n):
        _, base, indice, linea = n
        if isinstance(base, str):
            simbolo = self.buscar_variable(base, linea)
            tipo = simbolo.tipo if simbolo else None
        else:
            tipo = self.tipo_acceso(base)
        tipo_indice = self.tipo_de(indice)
        return verificar_indexado(self, tipo, tipo_indice, indice, linea)                           # Burgos

    def tipo_llamada(self, n, como_valor=True):
        """Tipo de una llamada. Como sentencia (como_valor=False) puede no devolver nada."""
        _, nombre, argumentos, linea = n
        tipos = [self.tipo_de(argumento) for argumento in argumentos]
        funcion = self.buscar_funcion(nombre, linea)
        if funcion is None:
            return None
        verificar_argumentos(self, nombre, funcion, tipos, linea)                                   # Mora
        if como_valor:
            verificar_valor_de_llamada(self, nombre, funcion, linea)                                # Burgos
        return funcion.retorno


def analizar_semantico(arbol):
    """Devuelve (tabla de símbolos, errores semánticos) a partir del árbol sintáctico."""
    analizador = AnalizadorSemantico()
    analizador.analizar(arbol)
    return analizador.tabla, analizador.errores
# FIN aporte: ANDRADE (tabla de símbolos, recorrido del árbol e identificadores)


# INICIO aporte: BURGOS (operaciones permitidas y retorno de funciones)

# REGLA SEMÁNTICA 3 (Burgos). Operaciones permitidas, operandos compatibles.
# Las operaciones aritméticas solo se permiten entre operandos numéricos del mismo tipo,
# salvo + entre dos cadenas (concatenación). No se pueden mezclar cadenas con números y
# % solo se permite entre enteros, como en Go. Ejemplo de error a detectar
#   total := "hola" + 518
def verificar_operandos(ctx, op, tipo_izq, tipo_der, linea):
    """Devuelve el tipo del resultado, o None si hay un error o un operando desconocido."""
    if tipo_izq is None or tipo_der is None:
        return None                       # ya se informó otro error, no se repite en cascada
    if op == "+" and tipo_izq == "string" and tipo_der == "string":
        return "string"
    if tipo_izq == "string" and tipo_der == "string":
        ctx.error("Operaciones permitidas", "Operandos compatibles", linea,
                  f"El operador {op} no se permite entre cadenas, solo + para concatenar")
        return None
    if tipo_izq not in NUMERICOS or tipo_der not in NUMERICOS or tipo_izq != tipo_der:
        ctx.error("Operaciones permitidas", "Operandos compatibles", linea,
                  f"No se puede operar {tipo_izq} con {tipo_der} usando el operador {op}")
        return None
    if op == "%" and tipo_izq != "int":
        ctx.error("Operaciones permitidas", "Operandos compatibles", linea,
                  f"El operador % solo se permite entre enteros, se encontró {tipo_izq} y {tipo_der}")
        return None
    return tipo_izq


# Comparaciones: == y != exigen operandos del mismo tipo; < <= > >= además solo admiten números o
# cadenas. El resultado siempre es bool, aunque haya error, para no generar errores en cascada.
def verificar_comparacion(ctx, op, tipo_izq, tipo_der, linea):
    if tipo_izq is None or tipo_der is None:
        return "bool"
    if tipo_izq != tipo_der:
        ctx.error("Operaciones permitidas", "Operandos compatibles", linea,
                  f"No se puede comparar {tipo_izq} con {tipo_der} usando el operador {op}")
    elif op in ("<", "<=", ">", ">=") and tipo_izq not in NUMERICOS and tipo_izq != "string":
        ctx.error("Operaciones permitidas", "Operandos compatibles", linea,
                  f"El operador {op} solo se permite entre números o cadenas, se encontró {tipo_izq}")
    return "bool"


# Conectores lógicos: && y || solo admiten booleanos, y ! también.
def verificar_logico(ctx, op, tipo_izq, tipo_der, linea):
    intrusos = [t for t in (tipo_izq, tipo_der) if t not in (None, "bool")]
    if intrusos:
        ctx.error("Operaciones permitidas", "Operandos compatibles", linea,
                  f"El operador {op} solo se permite entre booleanos, se encontró {' y '.join(intrusos)}")
    return "bool"


def verificar_negacion(ctx, tipo, linea):
    if tipo not in (None, "bool"):
        ctx.error("Operaciones permitidas", "Operandos compatibles", linea,
                  f"El operador ! solo se puede aplicar a booleanos, se encontró {tipo}")
    return "bool"


# ++ y -- solo se aplican a números.
def verificar_incremento(ctx, op, tipo, linea):
    if tipo is not None and tipo not in NUMERICOS:
        ctx.error("Operaciones permitidas", "Operandos compatibles", linea,
                  f"El operador {op} solo se puede aplicar a números, se encontró {tipo}")


# Indexación: solo se indexan arreglos, matrices y mapas; el índice de un arreglo es int, la
# clave de un mapa tiene el tipo declarado, y un índice constante debe estar dentro del arreglo.
# Devuelve el tipo del elemento (None si hay error o el tipo base es desconocido).
def verificar_indexado(ctx, tipo_base, tipo_indice, indice, linea):
    if tipo_base is None:
        return None
    elemento = tipo_elemento(tipo_base)
    if elemento is None:
        ctx.error("Operaciones permitidas", "Operandos compatibles", linea,
                  f"No se puede indexar un valor de tipo {tipo_base}")
        return None
    clave = tipo_clave(tipo_base)
    if tipo_indice is not None and tipo_indice != clave:
        ctx.error("Operaciones permitidas", "Operandos compatibles", linea,
                  f"El índice de {tipo_base} debe ser {clave}, se encontró {tipo_indice}")
        return elemento
    tamano = tamano_coleccion(tipo_base)
    if tamano is not None and isinstance(indice, tuple) and indice[0] == "entero" and indice[1] >= tamano:
        ctx.error("Operaciones permitidas", "Operandos compatibles", linea,
                  f"El índice {indice[1]} está fuera del rango de {tipo_base} (tamaño {tamano})")
    return elemento


# El signo negativo también es una operación aritmética, solo admite números.
def verificar_signo_negativo(ctx, tipo, linea):
    if tipo is None:
        return None
    if tipo not in NUMERICOS:
        ctx.error("Operaciones permitidas", "Operandos compatibles", linea,
                  f"El signo - solo se puede aplicar a números, se encontró {tipo}")
        return None
    return tipo


# REGLA SEMÁNTICA 4 (Burgos). Retorno de funciones, retorno coherente.
# El tipo de los valores de return debe coincidir con el declarado en la función y una
# función con retorno debe incluir un return. Ejemplo de error a detectar
#   func f() int {
#       return "a"
#   }
def verificar_return(ctx, nodo):
    _, valor, linea = nodo
    nombre, esperado = ctx.funcion
    ctx.hay_return = True
    tipo_valor = ctx.tipo_de(valor) if valor is not None else None
    if esperado is None and valor is not None:
        ctx.error("Retorno de funciones", "Retorno coherente", linea,
                  f"La función {nombre} no declara un tipo de retorno y no puede devolver un valor")
    elif esperado is not None and valor is None:
        ctx.error("Retorno de funciones", "Retorno coherente", linea,
                  f"La función {nombre} debe devolver un valor de tipo {esperado}")
    elif esperado is not None and tipo_valor is not None and tipo_valor != esperado:
        ctx.error("Retorno de funciones", "Retorno coherente", linea,
                  f"El return devuelve {tipo_valor} pero la función {nombre} declara {esperado}")


# El valor de una llamada solo se puede usar si la función declara un retorno.
# Ejemplo de error a detectar   x := saludar()   (saludar no devuelve nada)
def verificar_valor_de_llamada(ctx, nombre, funcion, linea):
    if funcion.retorno is None:
        ctx.error("Retorno de funciones", "Retorno coherente", linea,
                  f"La función {nombre} no devuelve ningún valor y no puede usarse en una expresión")


def verificar_return_presente(ctx, nodo_funcion):
    _, nombre, _, retorno, _, linea = nodo_funcion
    if retorno is not None and not ctx.hay_return:
        ctx.error("Retorno de funciones", "Retorno coherente", linea,
                  f"La función {nombre} declara retorno {retorno} pero no incluye un return")
# FIN aporte: BURGOS (operaciones permitidas y retorno de funciones)


# INICIO aporte: MORA (asignación de tipo, estructuras de control y ejecución por fases)

# REGLA SEMÁNTICA 5 (Mora). Asignación de tipo, asignación estricta.
# El valor asignado debe coincidir con el tipo declarado de la variable. Ejemplo de error
#   var x int = "hola"
def verificar_asignacion(ctx, tipo_destino, tipo_valor, linea, etiqueta):
    if tipo_destino is None or tipo_valor is None:
        return
    if tipo_destino != tipo_valor:
        ctx.error("Asignación de tipo", "Asignación estricta", linea,
                  f"No se puede asignar un valor {tipo_valor} a {etiqueta} de tipo {tipo_destino}")


# Las llamadas también asignan: cada argumento debe coincidir con el tipo del parámetro y la
# cantidad debe ser la declarada. Ejemplo de error a detectar
#   func f(a int) {}    f("hola")
def verificar_argumentos(ctx, nombre, funcion, tipos, linea):
    parametros = funcion.parametros
    if len(tipos) != len(parametros):
        ctx.error("Asignación de tipo", "Asignación estricta", linea,
                  f"La función {nombre} espera {len(parametros)} argumento(s) y se recibieron {len(tipos)}")
        return
    for numero, ((pnombre, ptipo), tipo) in enumerate(zip(parametros, tipos), start=1):
        if tipo is not None and ptipo is not None and tipo != ptipo:
            ctx.error("Asignación de tipo", "Asignación estricta", linea,
                      f"El argumento {numero} de la llamada a {nombre} debe ser {ptipo} "
                      f"(parámetro {pnombre}) y se encontró {tipo}")


# Los literales de arreglo, matriz y mapa también son asignaciones: cada elemento debe tener el
# tipo del elemento y no puede haber más elementos que el tamaño. Ejemplo de error a detectar
#   notas := [3]int{1, "dos", 3}
def verificar_literal(ctx, nodo):
    clase, tipo, elementos, linea = nodo
    if clase == "mapa":
        m = _RE_MAPA_KV.match(tipo)
        clave_t, valor_t = m.groups() if m else (None, None)
        for clave, valor in elementos:
            verificar_asignacion(ctx, clave_t, ctx.tipo_de(clave), linea_de(clave, linea), "una clave del mapa")
            verificar_asignacion(ctx, valor_t, ctx.tipo_de(valor), linea_de(valor, linea), "un valor del mapa")
        return tipo
    m = _RE_TAMANO.match(tipo)
    filas, filas_max, columnas_max, base = None, None, None, None
    if clase == "arreglo" and m:
        filas, columnas_max, base = [elementos], int(m.group(1)), m.group(2)
    elif clase == "matriz" and m:
        interior = _RE_TAMANO.match(m.group(2))
        if interior:
            filas, filas_max, columnas_max, base = elementos, int(m.group(1)), int(interior.group(1)), interior.group(2)
    if filas is None:                          # tipo que no se pudo descomponer, solo se evalúan los valores
        for fila in elementos:
            for x in (fila if isinstance(fila, list) else [fila]):
                ctx.tipo_de(x)
        return tipo
    if filas_max is not None and len(filas) > filas_max:
        ctx.error("Asignación de tipo", "Asignación estricta", linea,
                  f"El literal {tipo} admite {filas_max} fila(s) y se escribieron {len(filas)}")
    for fila in filas:
        if len(fila) > columnas_max:
            ctx.error("Asignación de tipo", "Asignación estricta", linea,
                      f"El literal {tipo} admite {columnas_max} elemento(s) por fila y se escribieron {len(fila)}")
        for x in fila:
            verificar_asignacion(ctx, base, ctx.tipo_de(x), linea_de(x, linea), "un elemento del literal")
    return tipo


# Una constante no puede modificarse (con =, +=, ++, -- ni al leer con fmt.Scanln).
# Ejemplo de error a detectar
#   const MAX int = 100
#   MAX = 5
# Devuelve True si informó el error, para no repetir otro error en la misma línea.
def verificar_constante(ctx, simbolo, linea):
    if simbolo is not None and simbolo.constante:
        ctx.error("Asignación de tipo", "Asignación estricta", linea,
                  f"La constante {simbolo.nombre} no puede modificarse")
        return True
    return False


# REGLA SEMÁNTICA 6 (Mora). Estructuras de control, control con sentido lógico.
# El break solo puede estar dentro de un for o un switch. Ejemplo de error a detectar
#   break   (en una función, fuera de cualquier for o switch)
def verificar_break(ctx, linea):
    if ctx.nivel_ciclo == 0:
        ctx.error("Estructuras de control", "Control con sentido lógico", linea,
                  "El break solo puede usarse dentro de un for o un switch")


# Las condiciones de if y for deben ser booleanas. Ejemplo de error a detectar
#   x := 5
#   if x {   }
def verificar_condicion(ctx, tipo, linea, estructura):
    if tipo not in (None, "bool"):
        ctx.error("Estructuras de control", "Control con sentido lógico", linea,
                  f"La condición del {estructura} debe ser bool, se encontró {tipo}")


# Cada case debe tener el tipo de la expresión del switch y no repetir un valor constante.
# Ejemplo de error a detectar   switch n { case "uno": ... }   con n de tipo int
def verificar_case(ctx, tipo_switch, tipo_valor, valor, vistos, linea):
    if tipo_switch is not None and tipo_valor is not None and tipo_switch != tipo_valor:
        ctx.error("Estructuras de control", "Control con sentido lógico", linea,
                  f"El valor del case es {tipo_valor} pero el switch evalúa una expresión {tipo_switch}")
        return
    if isinstance(valor, tuple) and valor[0] in ("entero", "flotante", "cadena", "booleano"):
        clave = (valor[0], valor[1])
        if clave in vistos:
            ctx.error("Estructuras de control", "Control con sentido lógico", linea,
                      f"El valor {valor[1]} ya aparece en otro case de este switch (línea {vistos[clave]})")
        else:
            vistos[clave] = linea


# EJECUCIÓN POR FASES
# El análisis trabaja siempre sobre el código tal cual está escrito. Los comentarios los descarta
# el analizador léxico y no influyen en ningún resultado: no existe ninguna marca ni comentario
# que active, desactive o recorte una validación semántica.


def analizar_completo_semantico(codigo):
    """Ejecuta léxico, sintáctico y semántico en orden. Cada fase solo corre si la anterior
    terminó sin errores."""
    from generar_log_sintactico import analizar_completo   # evita importar el parser al cargar el módulo

    resultado = analizar_completo(codigo)
    resultado.update({
        "semantico_ejecutado": False,
        "motivo": None,
        "tabla": [],
        "errores_semanticos": [],
    })
    if resultado["errores_lexicos"]:
        resultado["motivo"] = "Existen errores léxicos en el código fuente."
    elif resultado["errores_sintacticos"]:
        resultado["motivo"] = "Existen errores sintácticos en el código fuente."
    elif resultado["arbol"] is None:
        resultado["motivo"] = "El parser no pudo construir un árbol completo."
    else:
        tabla, errores = analizar_semantico(resultado["arbol"])
        resultado.update({
            "semantico_ejecutado": True,
            "tabla": tabla.filas(),
            "errores_semanticos": errores,
        })
    return resultado


if __name__ == "__main__":
    # Cada prueba desde la línea de comandos también genera su log en logs/
    #   py semantic.py algoritmos/algoritmo1.go [usuarioGit]
    if len(sys.argv) not in (2, 3):
        print("Uso: py semantic.py archivo.go [usuarioGit]")
        sys.exit(1)
    ruta = Path(sys.argv[1])
    codigo = ruta.read_text(encoding="utf-8")
    resultado = analizar_completo_semantico(codigo)
    print(f"Archivo analizado: {ruta}")
    print(f"Errores léxicos: {len(resultado['errores_lexicos'])}")
    print(f"Errores sintácticos: {len(resultado['errores_sintacticos'])}")
    if not resultado["semantico_ejecutado"]:
        print(f"Análisis semántico NO EJECUTADO. {resultado['motivo']}")
    else:
        print(f"Errores semánticos: {len(resultado['errores_semanticos'])}")
        for e in resultado["errores_semanticos"]:
            print(f"  - {e['mensaje']}")
        if not resultado["errores_semanticos"]:
            print("Análisis semántico correcto.")
    from generar_log_semantico import guardar_log_semantico
    from generar_log_sintactico import usuario_git_de, usuario_git_valido
    usuario = sys.argv[2] if len(sys.argv) == 3 else usuario_git_de(ruta)
    if usuario_git_valido(usuario):
        destino, _ = guardar_log_semantico(codigo, ruta.as_posix(), usuario)
        print(f"Log guardado en logs/{destino.name}")
    else:
        print("No se generó el log. Indica el usuario de Git (py semantic.py archivo.go usuarioGit).")
    sys.exit(1 if resultado["errores_semanticos"] else 0)
# FIN aporte: MORA (asignación de tipo, estructuras de control y ejecución por fases)