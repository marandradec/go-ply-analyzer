# -*- coding: utf-8 -*-
"""
interfaz.py - Ventana principal del analizador (Tkinter)

Parte de Andrade: ventana, botones y editor de código con numeración de líneas.
Los paneles de Burgos (tokens) y Mora (mensajes y barra de estado) tienen su
sección marcada con INICIO/FIN, igual que en lexer.py.
"""
import os
import re
import sys
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

try:
    import ttkbootstrap as tb
except ImportError:  # sin ttkbootstrap la aplicación sigue funcionando con Tk clásico
    tb = None

from consola import ConsolaInteractiva, SimuladorEjecucion
from generar_log import guardar_log
from generar_log_sintactico import (USUARIOS_GIT, analizar_completo, generar_logs_de_prueba,
                                    guardar_log_sintactico, usuario_git_valido)
from lexer import analizar

FUENTE_CODIGO = ("Consolas", 11)
TEXTO_CONFIRMACION_LOGS = "Se ejecutarán todos los archivos de prueba, ¿está seguro/a?"

# Autor de cada archivo de prueba, para nombrar el log sin preguntar
AUTORES = {
    "algoritmo1": "MariaAndrade", "errores_andrade": "MariaAndrade",
    "algoritmo2": "JoshuaBurgos", "errores_burgos": "JoshuaBurgos",
    "algoritmo3": "JoseMora", "errores_mora": "JoseMora",
}


# ===== INICIO aporte: ANDRADE (editor con numeración de líneas) =====
class EditorConLineas(tk.Frame):
    """Cuadro de texto con una columna de números de línea a la izquierda."""

    def __init__(self, master):
        super().__init__(master, background="#1e293b")

        # Columna de números: estilo IDE oscuro profesional
        self.numeros = tk.Text(self, width=4, padx=6, takefocus=0, wrap="none",
                               borderwidth=0, highlightthickness=0,
                               background="#1e293b", foreground="#64748b",
                               font=FUENTE_CODIGO, state="disabled")
        self.numeros.tag_configure("derecha", justify="right")

        # Cuadro donde se escribe el código (Fondo oscuro profundo y tipografía nítida)
        self.texto = tk.Text(self, wrap="none", undo=True, padx=8, pady=4,
                             borderwidth=0, highlightthickness=0,
                             background="#0f172a", foreground="#f8fafc",
                             insertbackground="#3b82f6",
                             font=FUENTE_CODIGO)

        self.barra_y = ttk.Scrollbar(self, orient="vertical", command=self._desplazar)
        self.barra_x = ttk.Scrollbar(self, orient="horizontal", command=self.texto.xview)
        self.texto.configure(yscrollcommand=self._al_desplazar,
                             xscrollcommand=self.barra_x.set)

        self.numeros.grid(row=0, column=0, sticky="ns")
        self.texto.grid(row=0, column=1, sticky="nsew")
        self.barra_y.grid(row=0, column=2, sticky="ns")
        self.barra_x.grid(row=1, column=1, sticky="ew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # Cada vez que cambia el texto, se vuelven a dibujar los números
        self.texto.bind("<<Modified>>", self._al_modificar)
        self._actualizar_numeros()

    def _desplazar(self, *args):
        """Mueve el texto y los números juntos cuando se usa la barra."""
        self.texto.yview(*args)
        self.numeros.yview(*args)

    def _al_desplazar(self, primero, ultimo):
        """Mantiene los números alineados cuando se usa la rueda del mouse."""
        self.barra_y.set(primero, ultimo)
        self.numeros.yview_moveto(primero)

    def _al_modificar(self, evento=None):
        self._actualizar_numeros()
        self.texto.edit_modified(False)

    def _actualizar_numeros(self):
        total = int(self.texto.index("end-1c").split(".")[0])
        self.numeros.configure(state="normal")
        self.numeros.delete("1.0", "end")
        self.numeros.insert("1.0", "\n".join(str(n) for n in range(1, total + 1)), "derecha")
        self.numeros.configure(state="disabled")
        self.numeros.yview_moveto(self.texto.yview()[0])

    # Funciones que usará el resto de la aplicación
    def obtener_codigo(self):
        return self.texto.get("1.0", "end-1c")

    def poner_codigo(self, codigo):
        self.texto.delete("1.0", "end")
        self.texto.insert("1.0", codigo)

    def limpiar(self):
        self.texto.delete("1.0", "end")
# ===== FIN aporte: ANDRADE (editor con numeración de líneas) =====


class Aplicacion(tb.Window if tb else tk.Tk):
    def __init__(self):
        if tb:
            super().__init__(themename="darkly")
        else:
            super().__init__()
        self.title("Analizador Go | Léxico · Sintáctico · Semántico")
        
        # Maximizado compatible entre plataformas (Windows vs Linux)
        if sys.platform.startswith("win"):
            self.state("zoomed")
        else:
            self.attributes("-zoomed", True)

        self.minsize(950, 600)
        
        self.ruta_actual = None
        self.codigo_analizado = None  # código del último análisis (para guardar el log)
        self.autor = None  # solo se pide si el archivo no está en AUTORES
        self.usuario_git = None  # solo se pide si el archivo no está en USUARIOS_GIT

        # Configurar colores generales de la ventana (Fondo oscuro corporativo)
        self.configure(bg="#0f172a")

        # Aplicar estilos con ttk adaptados al tema oscuro profesional
        self._configurar_estilos()

        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        self._crear_barra_superior()
        self._crear_cuerpo()
        self._crear_barra_estado()

    def _configurar_estilos(self):
        estilo = ttk.Style()
        if not tb:  # ttkbootstrap ya aplica su propio tema
            estilo.theme_use("clam")
        
        # Estilo para la tabla (Treeview) con paleta oscura elegante
        estilo.configure("Treeview",
                         background="#0f172a",
                         foreground="#f8fafc",
                         rowheight=26,
                         fieldbackground="#0f172a",
                         borderwidth=0,
                         font=("Segoe UI", 10))
        estilo.configure("Treeview.Heading",
                         background="#1e293b",
                         foreground="#f8fafc",
                         relief="flat",
                         font=("Segoe UI", 10, "bold"))
        estilo.map("Treeview", background=[('selected', '#2563eb')], foreground=[('selected', '#ffffff')])

    # ===== INICIO aporte: ANDRADE (ventana, botones y editor) =====
    def _crear_barra_superior(self):
        barra = tk.Frame(self, bg="#0f172a", padx=12, pady=10)
        barra.grid(row=0, column=0, sticky="ew")

        # Botones con estilo moderno azul corporativo
        estilo_boton = {
            "font": ("Segoe UI", 10, "bold"),
            "bg": "#2563eb",
            "fg": "#ffffff",
            "activebackground": "#1d4ed8",
            "activeforeground": "#ffffff",
            "relief": "flat",
            "padx": 14,
            "pady": 8,
            "cursor": "hand2"
        }

        self.btn_analizar = tk.Button(barra, text="▶ Analizar léxico", command=self.ejecutar_analisis, **estilo_boton)
        # Botón limpiar con un tono slate oscuro elegante y sofisticado
        self.btn_limpiar = tk.Button(barra, text="🧹 Limpiar", command=self.limpiar,
                                     font=("Segoe UI", 10, "bold"), bg="#334155", fg="#f8fafc",
                                     activebackground="#475569", activeforeground="#ffffff",
                                     relief="flat", padx=14, pady=8, cursor="hand2")

        self.btn_analizar.pack(side="left", padx=(0, 10))

        # Avance 2: botones del análisis sintáctico, simulación y logs de prueba
        self._crear_botones_sintacticos(barra)

        # Limpiar va siempre al final de la barra, después de Logs de prueba
        self.btn_limpiar.pack(side="left", padx=(0, 10))

    def _crear_cuerpo(self):
        cuerpo = tk.Frame(self, bg="#0f172a", padx=12, pady=4)
        cuerpo.grid(row=1, column=0, sticky="nsew")
        
        # Distribución en columnas profesionales
        cuerpo.columnconfigure(0, weight=1, minsize=230)
        cuerpo.columnconfigure(1, weight=3, minsize=420)
        cuerpo.columnconfigure(2, weight=2, minsize=360)
        cuerpo.rowconfigure(0, weight=3)
        cuerpo.rowconfigure(1, weight=1)
        cuerpo.rowconfigure(2, weight=2)

        # 1. Panel lateral izquierdo: Selector integrado de archivos .go
        marco_archivos = tk.LabelFrame(cuerpo, text=" Archivos del Proyecto ", font=("Segoe UI", 10, "bold"),
                                       bg="#1e293b", fg="#93c5fd", padx=8, pady=8, bd=1, relief="solid")
        marco_archivos.grid(row=0, column=0, rowspan=3, sticky="nsew", padx=(0, 8), pady=(0, 8))
        marco_archivos.rowconfigure(0, weight=1)
        marco_archivos.columnconfigure(0, weight=1)

        self.lista_archivos = tk.Listbox(marco_archivos, font=("Consolas", 10),
                                         bg="#0f172a", fg="#f8fafc", selectbackground="#2563eb",
                                         selectforeground="#ffffff", borderwidth=0, highlightthickness=0)
        scroll_archivos = ttk.Scrollbar(marco_archivos, orient="vertical", command=self.lista_archivos.yview)
        self.lista_archivos.configure(yscrollcommand=scroll_archivos.set)
        
        self.lista_archivos.grid(row=0, column=0, sticky="nsew")
        scroll_archivos.grid(row=0, column=1, sticky="ns")
        
        self.lista_archivos.bind("<Double-Button-1>", self.cargar_archivo_seleccionado)
        self._cargar_lista_algoritmos()

        # 2. Panel central: Editor de código fuente
        marco_codigo = tk.LabelFrame(cuerpo, text=" Código fuente (Go) ", font=("Segoe UI", 10, "bold"),
                                     bg="#1e293b", fg="#93c5fd", padx=8, pady=8, bd=1, relief="solid")
        marco_codigo.grid(row=0, column=1, sticky="nsew", padx=(0, 8), pady=(0, 8))
        marco_codigo.rowconfigure(0, weight=1)
        marco_codigo.columnconfigure(0, weight=1)
        self.editor = EditorConLineas(marco_codigo)
        self.editor.grid(row=0, column=0, sticky="nsew")

        # 3. Paneles derechos e inferiores
        self._crear_panel_tokens(cuerpo)    # Burgos
        self._crear_panel_mensajes(cuerpo)    # Mora
        self._crear_panel_sintactico(cuerpo)  # Avance 2: log sintáctico y consola

    def _cargar_lista_algoritmos(self):
        carpeta_algoritmos = os.path.join(os.path.dirname(os.path.abspath(__file__)), "algoritmos")
        if os.path.exists(carpeta_algoritmos):
            archivos_go = [f for f in os.listdir(carpeta_algoritmos) if f.endswith(".go")]
            archivos_go.sort()
            for arch in archivos_go:
                self.lista_archivos.insert("end", arch)

    def cargar_archivo_seleccionado(self, event=None):
        seleccion = self.lista_archivos.curselection()
        if not seleccion:
            return
        nombre_archivo = self.lista_archivos.get(seleccion[0])
        carpeta_algoritmos = os.path.join(os.path.dirname(os.path.abspath(__file__)), "algoritmos")
        ruta_completa = os.path.join(carpeta_algoritmos, nombre_archivo)
        
        try:
            with open(ruta_completa, encoding="utf-8") as archivo:
                codigo = archivo.read()
        except (OSError, UnicodeDecodeError) as error:
            messagebox.showerror("Error al abrir", f"No se pudo leer el archivo:\n{error}")
            return
        
        self.editor.poner_codigo(codigo)
        self.ruta_actual = ruta_completa
        self.estado.set(f"Estado: archivo abierto · {nombre_archivo}")

    def limpiar(self):
        self.editor.limpiar()
        self.vaciar_tokens()          # Burgos
        self.vaciar_mensajes()        # Mora
        self.vaciar_log_sintactico()  # Avance 2
        self.consola.limpiar()        # Avance 2
        self.ruta_actual = None
        self.codigo_analizado = None
        self.estado.set("Estado: listo")
    # ===== FIN aporte: ANDRADE (ventana, botones y editor) =====

    # ===== INICIO aporte: BURGOS (panel de tokens y ejecución del análisis) =====
    def _crear_panel_tokens(self, cuerpo):
        self.panel_tokens = tk.LabelFrame(cuerpo, text=" Tokens reconocidos ", font=("Segoe UI", 10, "bold"),
                                          bg="#1e293b", fg="#93c5fd", padx=8, pady=8, bd=1, relief="solid")
        self.panel_tokens.grid(row=0, column=2, sticky="nsew", padx=(0, 0), pady=(0, 8))
        self.panel_tokens.rowconfigure(0, weight=1)
        self.panel_tokens.columnconfigure(0, weight=1)

        columnas = ("Tipo", "Valor", "Línea")
        self.tabla_tokens = ttk.Treeview(self.panel_tokens, columns=columnas, show="headings")
        self.tabla_tokens.heading("Tipo", text="Tipo")
        self.tabla_tokens.heading("Valor", text="Valor")
        self.tabla_tokens.heading("Línea", text="Línea")
        self.tabla_tokens.column("Tipo", width=150, anchor="w")
        self.tabla_tokens.column("Valor", width=100, anchor="w")
        self.tabla_tokens.column("Línea", width=70, anchor="center")

        scroll_tokens = ttk.Scrollbar(self.panel_tokens, orient="vertical", command=self.tabla_tokens.yview)
        self.tabla_tokens.configure(yscrollcommand=scroll_tokens.set)
        self.tabla_tokens.grid(row=0, column=0, sticky="nsew")
        scroll_tokens.grid(row=0, column=1, sticky="ns")

    def vaciar_tokens(self):
        for item in self.tabla_tokens.get_children():
            self.tabla_tokens.delete(item)

    def ejecutar_analisis(self):
        codigo = self.editor.obtener_codigo()
        if not codigo.strip():
            messagebox.showwarning("Advertencia", "El editor de código está vacío.")
            return

        # analizar() reinicia el contador de líneas y la lista de errores en cada ejecución
        tokens, errores = analizar(codigo)
        self.codigo_analizado = codigo

        self.vaciar_tokens()
        for tipo, valor, linea in tokens:
            self.tabla_tokens.insert("", "end", values=(tipo, valor, f"Línea {linea}"))

        self.mostrar_mensajes(errores)    # Mora
        if errores:
            self.estado.set(f"Estado: análisis léxico finalizado · {len(tokens)} tokens · "
                            f"{len(errores)} error(es) léxico(s)")
        else:
            self.estado.set(f"Estado: análisis léxico finalizado · {len(tokens)} tokens · sin errores")
        self.guardar_log()    # Mora
    # ===== FIN aporte: BURGOS (panel de tokens y ejecución del análisis) =====

    # ===== INICIO aporte: MORA (mensajes de error, barra de estado y log) =====
    def _crear_panel_mensajes(self, cuerpo):
        self.panel_mensajes = tk.LabelFrame(cuerpo, text=" Mensajes y Consola ", font=("Segoe UI", 10, "bold"),
                                          bg="#1e293b", fg="#93c5fd", padx=8, pady=8, bd=1, relief="solid")
        self.panel_mensajes.grid(row=1, column=1, columnspan=2, sticky="nsew", pady=(0, 0))
        self.panel_mensajes.rowconfigure(0, weight=1)
        self.panel_mensajes.columnconfigure(0, weight=1)

        self.texto_mensajes = tk.Text(self.panel_mensajes, height=6, wrap="word", state="disabled",
                                      background="#0f172a", foreground="#f8fafc",
                                      font=FUENTE_CODIGO, padx=8, pady=4, borderwidth=0, highlightthickness=0)
        self.texto_mensajes.tag_configure("lexico", foreground="#f87171")   # Rojo suave optimizado para modo oscuro
        self.texto_mensajes.tag_configure("ok", foreground="#4ade80")       # Verde suave optimizado para modo oscuro
        
        barra = ttk.Scrollbar(self.panel_mensajes, orient="vertical", command=self.texto_mensajes.yview)
        self.texto_mensajes.configure(yscrollcommand=barra.set)
        self.texto_mensajes.grid(row=0, column=0, sticky="nsew")
        barra.grid(row=0, column=1, sticky="ns")

    def vaciar_mensajes(self):
        self.texto_mensajes.config(state="normal")
        self.texto_mensajes.delete("1.0", "end")
        self.texto_mensajes.config(state="disabled")

    def mostrar_mensajes(self, errores):
        self.vaciar_mensajes()
        self.texto_mensajes.config(state="normal")
        if errores:
            for error in errores:
                self.texto_mensajes.insert("end", error["mensaje"] + "\n", "lexico")
        else:
            self.texto_mensajes.insert("end", "Análisis léxico sin errores.\n", "ok")
        self.texto_mensajes.config(state="disabled")

    def _crear_barra_estado(self):
        self.estado = tk.StringVar(value="Estado: listo")
        # Barra de estado inferior elegante en tono oscuro armonizado
        lbl_estado = tk.Label(self, textvariable=self.estado, anchor="w",
                              bg="#1e293b", fg="#94a3b8", font=("Segoe UI", 9, "bold"),
                              padx=14, pady=6, relief="flat")
        lbl_estado.grid(row=2, column=0, columnspan=3, sticky="ew")

    def guardar_log(self):
        if self.codigo_analizado is None:
            return
        archivo = os.path.basename(self.ruta_actual) if self.ruta_actual else "editor"
        autor = AUTORES.get(os.path.splitext(archivo)[0]) or self.autor
        if not autor:
            autor = simpledialog.askstring(
                "Autor del log", "Escribe tu NombreApellido, sin espacios ni tildes (ej. MariaAndrade):", parent=self)
            if autor is None:
                return
            autor = autor.strip()
            if not re.fullmatch(r"[A-Za-z]+", autor):
                messagebox.showerror("Nombre no válido", "Usa solo letras, por ejemplo MariaAndrade.")
                return
            self.autor = autor
        destino, _, _ = guardar_log(self.codigo_analizado, archivo, autor)
        self.estado.set(f"{self.estado.get().split(' · log ')[0]} · log {destino.name}")
    # ===== FIN aporte: MORA (mensajes de error, barra de estado y log) =====

    # ===== INICIO aporte: ANDRADE (Avance 2, botones, pestañas y confirmación de logs de prueba) =====
    def _crear_botones_sintacticos(self, barra):
        if tb:
            self.btn_sintaxis = tb.Button(barra, text="🔍 Analizar Sintaxis", bootstyle="warning",
                                          command=self.ejecutar_analisis_sintactico)
            self.btn_simular = tb.Button(barra, text="⌨ Simular ejecución", bootstyle="success",
                                         command=self.simular_ejecucion)
            self.btn_logs = tb.Button(barra, text="📄 Logs de prueba", bootstyle="info-outline",
                                      command=self.generar_logs_prueba)
        else:
            estilo = {"font": ("Segoe UI", 10, "bold"), "fg": "#ffffff", "relief": "flat",
                      "padx": 14, "pady": 8, "cursor": "hand2"}
            self.btn_sintaxis = tk.Button(barra, text="🔍 Analizar Sintaxis", bg="#d97706",
                                          command=self.ejecutar_analisis_sintactico, **estilo)
            self.btn_simular = tk.Button(barra, text="⌨ Simular ejecución", bg="#16a34a",
                                         command=self.simular_ejecucion, **estilo)
            self.btn_logs = tk.Button(barra, text="📄 Logs de prueba", bg="#0e7490",
                                      command=self.generar_logs_prueba, **estilo)
        for boton in (self.btn_sintaxis, self.btn_simular, self.btn_logs):
            boton.pack(side="left", padx=(0, 10))

    def _crear_panel_sintactico(self, cuerpo):
        """Panel inferior con dos pestañas: log sintáctico y consola interactiva."""
        self.pestanas = ttk.Notebook(cuerpo)
        self.pestanas.grid(row=2, column=1, columnspan=2, sticky="nsew", pady=(8, 0))

        marco_log = tk.Frame(self.pestanas, bg="#1e293b", padx=6, pady=6)
        marco_log.rowconfigure(0, weight=1)
        marco_log.columnconfigure(0, weight=1)
        self.texto_sintactico = tk.Text(marco_log, height=8, wrap="word", state="disabled",
                                        background="#0f172a", foreground="#f8fafc",
                                        font=FUENTE_CODIGO, padx=8, pady=4,
                                        borderwidth=0, highlightthickness=0)
        for etiqueta, color in (("titulo", "#93c5fd"), ("ok", "#4ade80"), ("lexico", "#f87171"),
                                ("sintactico", "#facc15"), ("detalle", "#94a3b8")):
            self.texto_sintactico.tag_configure(etiqueta, foreground=color)
        self.texto_sintactico.tag_configure("titulo", font=("Consolas", 11, "bold"))
        barra = ttk.Scrollbar(marco_log, orient="vertical", command=self.texto_sintactico.yview)
        self.texto_sintactico.configure(yscrollcommand=barra.set)
        self.texto_sintactico.grid(row=0, column=0, sticky="nsew")
        barra.grid(row=0, column=1, sticky="ns")
        self.pestanas.add(marco_log, text="  Log sintáctico  ")

        marco_consola = tk.Frame(self.pestanas, bg="#1e293b", padx=6, pady=6)
        marco_consola.rowconfigure(0, weight=1)
        marco_consola.columnconfigure(0, weight=1)
        self.consola = ConsolaInteractiva(marco_consola)
        self.consola.grid(row=0, column=0, sticky="nsew")
        self.pestanas.add(marco_consola, text="  Consola interactiva  ")

    def _confirmar_logs_prueba(self):
        """Pregunta (con advertencia) si se ejecutan todos los archivos de prueba. True solo con Sí."""
        if tb:
            from ttkbootstrap.dialogs import MessageDialog
            try:  # ttkbootstrap 1.x trae el icono de advertencia; la 2.x usa el nombre del glifo
                from ttkbootstrap.icons import Icon
                icono = Icon.warning
            except ImportError:
                icono = "exclamation-triangle-fill"
            dialogo = MessageDialog(message=TEXTO_CONFIRMACION_LOGS, title="Confirmar ejecución",
                                    buttons=["No:secondary", "Sí:warning"], icon=icono,
                                    parent=self, alert=True)
            dialogo.show()
            return dialogo.result == "Sí"
        return messagebox.askyesno("Confirmar ejecución", TEXTO_CONFIRMACION_LOGS,
                                   icon="warning", parent=self)

    def generar_logs_prueba(self):
        # Si el usuario responde No, se cancela la operación por completo
        if not self._confirmar_logs_prueba():
            return
        resumen = generar_logs_de_prueba()
        self.vaciar_log_sintactico()
        self.texto_sintactico.config(state="normal")
        self._escribir_log("LOGS DE PRUEBA (léxico + sintáctico)", "titulo")
        for nombre, tokens, lex, sint, destino in resumen:
            etiqueta = "ok" if not (lex or sint) else "sintactico"
            self._escribir_log(f"{nombre:20s} tokens {tokens:4d} · léxicos {lex} · sintácticos {sint} · {destino.name}",
                               etiqueta)
        self.texto_sintactico.config(state="disabled")
        self.pestanas.select(0)
        self.estado.set(f"Estado: {len(resumen)} logs de prueba generados en la carpeta logs")
    # ===== FIN aporte: ANDRADE (Avance 2, botones, pestañas y confirmación de logs de prueba) =====

    # ===== INICIO aporte: BURGOS (Avance 2, ejecución y visualización del análisis sintáctico) =====
    def vaciar_log_sintactico(self):
        self.texto_sintactico.config(state="normal")
        self.texto_sintactico.delete("1.0", "end")
        self.texto_sintactico.config(state="disabled")

    def _escribir_log(self, texto, etiqueta=None):
        self.texto_sintactico.insert("end", texto + "\n", etiqueta)

    def ejecutar_analisis_sintactico(self):
        codigo = self.editor.obtener_codigo()
        if not codigo.strip():
            messagebox.showwarning("Advertencia", "El editor de código está vacío.")
            return

        resultado = analizar_completo(codigo)
        self.codigo_analizado = codigo
        self.ultimo_resultado = resultado

        # La tabla de tokens y el panel de mensajes se mantienen al día con la fase léxica
        self.vaciar_tokens()
        for tipo, valor, linea in resultado["tokens"]:
            self.tabla_tokens.insert("", "end", values=(tipo, valor, f"Línea {linea}"))
        self.mostrar_mensajes(resultado["errores_lexicos"])

        self.mostrar_log_sintactico(resultado, codigo)
        self.pestanas.select(0)
        total = len(resultado["errores_sintacticos"])
        self.estado.set(f"Estado: análisis sintáctico finalizado · {len(resultado['tokens'])} tokens · "
                        + (f"{total} error(es) sintáctico(s)" if total else "sintaxis correcta"))
        self.guardar_log_sintactico()

    def mostrar_log_sintactico(self, resultado, codigo):
        lineas_codigo = codigo.splitlines()
        err_lex = resultado["errores_lexicos"]
        err_sin = resultado["errores_sintacticos"]
        self.vaciar_log_sintactico()
        self.texto_sintactico.config(state="normal")

        self._escribir_log("FASE 1 · ANÁLISIS LÉXICO", "titulo")
        self._escribir_log(f"Tokens reconocidos: {len(resultado['tokens'])}", "detalle")
        if err_lex:
            for error in err_lex:
                self._escribir_log("✘ " + error["mensaje"], "lexico")
        else:
            self._escribir_log("✔ Sin errores léxicos.", "ok")

        self._escribir_log("\nFASE 2 · ANÁLISIS SINTÁCTICO", "titulo")
        if err_sin:
            self._escribir_log(f"✘ Se encontraron {len(err_sin)} error(es) sintáctico(s).", "sintactico")
            for error in err_sin:
                self._escribir_log(f"✘ Línea {error['linea']} · token «{error.get('token') or '-'}»", "sintactico")
                self._escribir_log("    " + error["mensaje"], "sintactico")
                if 1 <= error["linea"] <= len(lineas_codigo):
                    self._escribir_log("    código: " + lineas_codigo[error["linea"] - 1].strip(), "detalle")
        else:
            self._escribir_log("✔ Análisis sintáctico correcto.", "ok")
        if resultado["omitidos"]:
            self._escribir_log(f"({resultado['omitidos']} error(es) sintáctico(s) omitido(s) por coincidir "
                               "con una línea con error léxico)", "detalle")
        for nombre, linea, n in ((f[1], f[5], len(f[4])) for f in resultado["funciones"]):
            self._escribir_log(f"✔ func {nombre} (línea {linea}) · {n} sentencia(s)", "ok")
        self.texto_sintactico.config(state="disabled")
    # ===== FIN aporte: BURGOS (Avance 2, ejecución y visualización del análisis sintáctico) =====

    # ===== INICIO aporte: MORA (Avance 2, log sintáctico por usuario de Git y simulación de ejecución) =====
    def _obtener_usuario_git(self, archivo):
        """Usuario de Git para nombrar el log. Los seis archivos del proyecto ya lo tienen asignado."""
        usuario = USUARIOS_GIT.get(os.path.splitext(archivo)[0]) or self.usuario_git
        if usuario:
            return usuario
        usuario = simpledialog.askstring(
            "Usuario de Git", "Escribe tu usuario de Git para nombrar el log (ej. marandradec):", parent=self)
        if usuario is None:
            return None
        usuario = usuario.strip()
        if not usuario_git_valido(usuario):
            messagebox.showerror("Usuario no válido", "Usa solo letras, números y guiones, por ejemplo marandradec.")
            return None
        self.usuario_git = usuario
        return usuario

    def guardar_log_sintactico(self):
        if self.codigo_analizado is None:
            return
        archivo = os.path.basename(self.ruta_actual) if self.ruta_actual else "editor"
        usuario = self._obtener_usuario_git(archivo)
        if not usuario:
            return
        destino, _ = guardar_log_sintactico(self.codigo_analizado, archivo, usuario)
        self.estado.set(f"{self.estado.get().split(' · log ')[0]} · log {destino.name}")

    def simular_ejecucion(self):
        codigo = self.editor.obtener_codigo()
        if not codigo.strip():
            messagebox.showwarning("Advertencia", "El editor de código está vacío.")
            return
        resultado = analizar_completo(codigo)
        self.pestanas.select(1)
        if resultado["errores_sintacticos"]:
            self.consola.escribir("No se puede simular. Corrige primero los errores sintácticos "
                                  "(botón Analizar Sintaxis).\n", "error")
            return
        self.btn_simular.config(state="disabled")
        SimuladorEjecucion(self.consola, al_terminar=lambda: self.btn_simular.config(state="normal")
                           ).iniciar(resultado["funciones"])
    # ===== FIN aporte: MORA (Avance 2, log sintáctico por usuario de Git y simulación de ejecución) =====


if __name__ == "__main__":
    Aplicacion().mainloop()