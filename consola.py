# -*- coding: utf-8 -*-
"""
consola.py - Consola interactiva y simulación de entrada/salida (Avance 2)
ConsolaInteractiva y SimuladorEjecucion
"""
import tkinter as tk
from tkinter import ttk

FUENTE_CONSOLA = ("Consolas", 11)
PROMPT = "> "


# Consola interactiva
class ConsolaInteractiva(tk.Frame):
    """Consola con entrada por teclado. Todo lo escrito antes de la marca 'entrada' es de solo lectura."""

    COMANDOS = {"ayuda": "Comandos: ayuda, limpiar. Con una simulación activa se pide un dato por Scanln.",
                "limpiar": None}

    def __init__(self, master):
        super().__init__(master, background="#0f172a")
        self.texto = tk.Text(self, wrap="word", height=6, padx=8, pady=4,
                             background="#0f172a", foreground="#f8fafc",
                             insertbackground="#3b82f6", borderwidth=0, highlightthickness=0,
                             font=FUENTE_CONSOLA)
        self.texto.tag_configure("salida", foreground="#f8fafc")
        self.texto.tag_configure("prompt", foreground="#38bdf8")
        self.texto.tag_configure("entrada", foreground="#4ade80")
        self.texto.tag_configure("sistema", foreground="#94a3b8")
        self.texto.tag_configure("error", foreground="#f87171")
        barra = ttk.Scrollbar(self, orient="vertical", command=self.texto.yview)
        self.texto.configure(yscrollcommand=barra.set)
        self.texto.grid(row=0, column=0, sticky="nsew")
        barra.grid(row=0, column=1, sticky="ns")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self._callback = None  # función que espera el dato del Scanln
        self.texto.bind("<Return>", self._al_enter)
        self.texto.bind("<KP_Enter>", self._al_enter)
        self.texto.bind("<BackSpace>", self._al_borrar)
        self.texto.bind("<Left>", self._al_borrar)
        self.texto.bind("<Home>", self._al_inicio)
        self.texto.bind("<Key>", self._al_tecla)
        self.texto.bind("<Button-1>", lambda e: self.texto.after_idle(self._proteger_cursor))
        self.mensaje_inicial()

    # Escritura
    def mensaje_inicial(self):
        self.escribir("Consola interactiva. Escribe 'ayuda' para ver los comandos.\n", "sistema")
        self._nuevo_prompt()

    def escribir(self, texto, etiqueta="salida"):
        """Agrega texto de salida antes de la línea de entrada actual."""
        if self._tiene_marca():
            # la marca tiene gravedad izquierda; se avanza para que el prompt quede siempre al final
            self.texto.insert("entrada_inicio_linea", texto, etiqueta)
            self.texto.mark_set("entrada_inicio_linea", f"entrada_inicio_linea +{len(texto)}c")
        else:
            self.texto.insert("end", texto, etiqueta)
        self.texto.see("end")

    def _tiene_marca(self):
        return "entrada_inicio_linea" in self.texto.mark_names()

    def _nuevo_prompt(self, texto=PROMPT):
        self.texto.mark_set("entrada_inicio_linea", "end-1c")
        self.texto.mark_gravity("entrada_inicio_linea", "left")
        self.texto.insert("end", texto, "prompt")
        self.texto.mark_set("entrada", "end-1c")
        self.texto.mark_gravity("entrada", "left")
        self.texto.mark_set("insert", "end")
        self.texto.see("end")

    def limpiar(self):
        self.texto.delete("1.0", "end")
        for marca in ("entrada_inicio_linea", "entrada"):
            if marca in self.texto.mark_names():
                self.texto.mark_unset(marca)
        self._callback = None
        self.mensaje_inicial()

    # Entrada
    def solicitar_entrada(self, callback, prompt="Ingrese un valor: "):
        """Pide un dato (fmt.Scanln simulado). callback(valor) se llama al presionar Enter."""
        self._callback = callback
        self._reemplazar_prompt(prompt)
        self.texto.focus_set()

    def _reemplazar_prompt(self, prompt):
        self.texto.delete("entrada_inicio_linea", "end-1c")  # end-1c evita borrar el \n anterior
        self._nuevo_prompt(prompt)

    def _al_enter(self, evento=None):
        valor = self.texto.get("entrada", "end-1c")
        self.texto.insert("end", "\n", "entrada")
        self.texto.tag_add("entrada", "entrada", "end-1c")
        callback, self._callback = self._callback, None
        self._nuevo_prompt()
        if callback:
            callback(valor.strip())
        else:
            self._ejecutar_comando(valor.strip())
        return "break"  # evita que Tk inserte otro salto de línea

    def _ejecutar_comando(self, comando):
        if not comando:
            return
        if comando.lower() == "limpiar":
            self.limpiar()
        elif comando.lower() == "ayuda":
            self.escribir(self.COMANDOS["ayuda"] + "\n", "sistema")
        else:
            self.escribir(f"Sin ejecución activa. '{comando}' no es un comando (escribe 'ayuda').\n", "error")

    # Protección de la zona de solo lectura
    def _proteger_cursor(self):
        if self.texto.compare("insert", "<", "entrada"):
            self.texto.mark_set("insert", "end")

    def _al_tecla(self, evento):
        if evento.keysym in ("Up", "Down", "Right", "Prior", "Next", "End",
                             "Shift_L", "Shift_R", "Control_L", "Control_R"):
            return None
        self._proteger_cursor()
        return None

    def _al_borrar(self, evento=None):
        if self.texto.compare("insert", "<=", "entrada"):
            return "break"
        return None

    def _al_inicio(self, evento=None):
        self.texto.mark_set("insert", "entrada")
        return "break"


# simulación de entrada y salida
class SimuladorEjecucion:
    """Simula fmt.Println y fmt.Scanln de main siguiendo el orden del código."""

    def __init__(self, consola, al_terminar=None):
        self.consola = consola
        self.al_terminar = al_terminar
        self.entorno = {}
        self.pasos = []
        self.indice = 0

    def iniciar(self, funciones):
        main = next((f for f in funciones if f[1] == "main"), None)
        self.consola.escribir("\n--- Inicio de la simulación (main) ---\n", "sistema")
        if main is None:
            self.consola.escribir("No existe la función main.\n", "error")
            return self._terminar()
        self.pasos = list(main[4])
        self.indice = 0
        self._avanzar()

    def _avanzar(self):
        while self.indice < len(self.pasos):
            nodo = self.pasos[self.indice]
            self.indice += 1
            tipo = nodo[0] if isinstance(nodo, tuple) and nodo else None
            if tipo == "imprimir":
                texto = " ".join(self._texto(self._evaluar(a)) for a in nodo[1])
                self.consola.escribir(texto + "\n")
            elif tipo == "leer":
                variable = nodo[1]
                self.consola.solicitar_entrada(lambda dato, v=variable: self._recibir(v, dato),
                                               prompt=f"{variable} = ")
                return  # se continúa cuando el usuario presiona Enter
            elif tipo in ("decl_corta", "var", "const"):
                self._declarar(nodo)
            elif tipo == "asignacion" and nodo[1][0] == "id":
                self.entorno[nodo[1][1]] = self._evaluar(nodo[2])
            elif tipo in ("if", "for", "switch"):
                self.consola.escribir(f"(línea {nodo[-1]}: la estructura '{tipo}' no se simula)\n", "sistema")
        self._terminar()

    def _recibir(self, variable, dato):
        self.entorno[variable] = self._convertir(dato)
        self.consola.escribir(f"(se guardó {variable} = {self._texto(self.entorno[variable])})\n", "sistema")
        self._avanzar()

    def _terminar(self):
        self.consola.escribir("--- Fin de la simulación ---\n", "sistema")
        if self.al_terminar:
            self.al_terminar()

    # Evaluación mínima de expresiones
    def _declarar(self, nodo):
        if nodo[0] == "decl_corta":
            self.entorno[nodo[1]] = self._evaluar(nodo[2])
        elif nodo[0] == "const":
            self.entorno[nodo[1]] = self._evaluar(nodo[3])
        elif nodo[3] is not None:  # var con valor inicial
            self.entorno[nodo[1]] = self._evaluar(nodo[3])
        else:
            self.entorno[nodo[1]] = 0 if nodo[2] in ("int", "float64") else ("" if nodo[2] == "string" else None)

    def _evaluar(self, expr):
        if not isinstance(expr, tuple):
            return expr
        tipo = expr[0]
        if tipo in ("entero", "flotante", "booleano"):
            return expr[1] == "true" if tipo == "booleano" else expr[1]
        if tipo == "cadena":
            return str(expr[1]).strip('"')
        if tipo == "id":
            return self.entorno.get(expr[1], f"<{expr[1]}>")
        if tipo == "neg":
            valor = self._evaluar(expr[1])
            return -valor if isinstance(valor, (int, float)) else "<expresión>"
        if tipo == "not":
            valor = self._evaluar(expr[1])
            return (not valor) if isinstance(valor, bool) else "<expresión>"
        if tipo == "binop":
            return self._operar(expr[1], self._evaluar(expr[2]), self._evaluar(expr[3]))
        return "<expresión>"

    @staticmethod
    def _operar(op, a, b):
        if isinstance(a, str) and a.startswith("<") or isinstance(b, str) and b.startswith("<"):
            return "<expresión>"  # algún operando no se pudo calcular
        comparaciones = {"==": lambda: a == b, "!=": lambda: a != b, "<": lambda: a < b,
                         ">": lambda: a > b, "<=": lambda: a <= b, ">=": lambda: a >= b,
                         "&&": lambda: a and b, "||": lambda: a or b}
        if op in comparaciones:
            try:
                return comparaciones[op]()
            except TypeError:
                return "<expresión>"
        numerico = all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in (a, b))
        try:
            if op == "+" and isinstance(a, str) and isinstance(b, str):
                return a + b
            if numerico and op in ("+", "-", "*", "/", "%"):
                if op == "/":
                    return a // b if isinstance(a, int) and isinstance(b, int) else a / b
                return {"+": a + b, "-": a - b, "*": a * b, "%": a % b if op == "%" else 0}[op]
        except ZeroDivisionError:
            return "<división por cero>"
        return "<expresión>"

    @staticmethod
    def _convertir(dato):
        for tipo in (int, float):
            try:
                return tipo(dato)
            except ValueError:
                pass
        return {"true": True, "false": False}.get(dato.lower(), dato)

    @staticmethod
    def _texto(valor):
        if isinstance(valor, bool):
            return "true" if valor else "false"
        return str(valor)
