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

from generar_log import guardar_log
from lexer import analizar

FUENTE_CODIGO = ("Consolas", 11)

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


class Aplicacion(tk.Tk):
    def __init__(self):
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

        for boton in (self.btn_analizar, self.btn_limpiar):
            boton.pack(side="left", padx=(0, 10))

    def _crear_cuerpo(self):
        cuerpo = tk.Frame(self, bg="#0f172a", padx=12, pady=4)
        cuerpo.grid(row=1, column=0, sticky="nsew")
        
        # Distribución en columnas profesionales
        cuerpo.columnconfigure(0, weight=1, minsize=230)
        cuerpo.columnconfigure(1, weight=3, minsize=420)
        cuerpo.columnconfigure(2, weight=2, minsize=360)
        cuerpo.rowconfigure(0, weight=3)
        cuerpo.rowconfigure(1, weight=1)

        # 1. Panel lateral izquierdo: Selector integrado de archivos .go
        marco_archivos = tk.LabelFrame(cuerpo, text=" Archivos del Proyecto ", font=("Segoe UI", 10, "bold"),
                                       bg="#1e293b", fg="#93c5fd", padx=8, pady=8, bd=1, relief="solid")
        marco_archivos.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 8), pady=(0, 8))
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
        self.vaciar_tokens()            # Burgos
        self.vaciar_mensajes()        # Mora
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


if __name__ == "__main__":
    Aplicacion().mainloop()