# -*- coding: utf-8 -*-
"""
interfaz.py - Ventana principal del analizador (Tkinter)

Parte de Andrade: ventana, botones y editor de código con numeración de líneas.
Los paneles de Burgos (tokens) y Mora (mensajes y barra de estado) tienen su
sección marcada con INICIO/FIN, igual que en lexer.py.
"""
import os
import tkinter as tk
from tkinter import filedialog, messagebox

FUENTE_CODIGO = ("Consolas", 11)


# ===== INICIO aporte: ANDRADE (editor con numeración de líneas) =====
class EditorConLineas(tk.Frame):
    """Cuadro de texto con una columna de números de línea a la izquierda."""

    def __init__(self, master):
        super().__init__(master)

        # Columna de números: solo lectura, se llena sola
        self.numeros = tk.Text(self, width=4, padx=6, takefocus=0, wrap="none",
                               borderwidth=0, highlightthickness=0,
                               background="#f0f0f0", foreground="#666666",
                               font=FUENTE_CODIGO, state="disabled")
        self.numeros.tag_configure("derecha", justify="right")

        # Cuadro donde se escribe el código
        self.texto = tk.Text(self, wrap="none", undo=True, padx=6,
                             borderwidth=0, highlightthickness=0,
                             font=FUENTE_CODIGO)

        self.barra_y = tk.Scrollbar(self, orient="vertical", command=self._desplazar)
        self.barra_x = tk.Scrollbar(self, orient="horizontal", command=self.texto.xview)
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
        self.geometry("1100x650")
        self.minsize(800, 500)
        self.ruta_actual = None

        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        self._crear_barra_superior()
        self._crear_cuerpo()
        self._crear_barra_estado()

    # ===== INICIO aporte: ANDRADE (ventana, botones y editor) =====
    def _crear_barra_superior(self):
        barra = tk.Frame(self, padx=8, pady=6)
        barra.grid(row=0, column=0, sticky="ew")

        self.btn_abrir = tk.Button(barra, text="Abrir archivo .go", command=self.abrir_archivo)
        self.btn_analizar = tk.Button(barra, text="Analizar", state="disabled")  # se conecta en el siguiente paso
        self.btn_limpiar = tk.Button(barra, text="Limpiar", command=self.limpiar)
        self.btn_guardar = tk.Button(barra, text="Guardar log", state="disabled")  # se conecta más adelante

        for boton in (self.btn_abrir, self.btn_analizar, self.btn_limpiar, self.btn_guardar):
            boton.pack(side="left", padx=4)

    def _crear_cuerpo(self):
        cuerpo = tk.Frame(self, padx=8)
        cuerpo.grid(row=1, column=0, sticky="nsew")
        cuerpo.columnconfigure(0, weight=3)
        cuerpo.columnconfigure(1, weight=2)
        cuerpo.rowconfigure(0, weight=3)
        cuerpo.rowconfigure(1, weight=1)

        marco_codigo = tk.LabelFrame(cuerpo, text="Código fuente (Go)")
        marco_codigo.grid(row=0, column=0, sticky="nsew", padx=(0, 4), pady=(0, 4))
        marco_codigo.rowconfigure(0, weight=1)
        marco_codigo.columnconfigure(0, weight=1)
        self.editor = EditorConLineas(marco_codigo)
        self.editor.grid(row=0, column=0, sticky="nsew")

        # ===== INICIO aporte: BURGOS (panel de tokens reconocidos) =====
        self.panel_tokens = tk.LabelFrame(cuerpo, text="Tokens reconocidos")
        self.panel_tokens.grid(row=0, column=1, sticky="nsew", padx=(4, 0), pady=(0, 4))
        # ===== FIN aporte: BURGOS (panel de tokens reconocidos) =====

        # ===== INICIO aporte: MORA (panel de mensajes de error) =====
        self.panel_mensajes = tk.LabelFrame(cuerpo, text="Mensajes")
        self.panel_mensajes.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(0, 4))
        # ===== FIN aporte: MORA (panel de mensajes de error) =====

    def abrir_archivo(self):
        ruta = filedialog.askopenfilename(
            title="Abrir archivo Go",
            filetypes=[("Archivos Go", "*.go"), ("Todos los archivos", "*.*")],
        )
        if not ruta:
            return
        try:
            with open(ruta, encoding="utf-8") as archivo:
                codigo = archivo.read()
        except (OSError, UnicodeDecodeError) as error:
            messagebox.showerror("Error al abrir", f"No se pudo leer el archivo:\n{error}")
            return
        self.editor.poner_codigo(codigo)
        self.ruta_actual = ruta
        self.estado.set(f"Estado: archivo abierto · {os.path.basename(ruta)}")

    def limpiar(self):
        self.editor.limpiar()
        self.ruta_actual = None
        self.estado.set("Estado: listo")
    # ===== FIN aporte: ANDRADE (ventana, botones y editor) =====

    # ===== INICIO aporte: MORA (barra de estado) =====
    def _crear_barra_estado(self):
        self.estado = tk.StringVar(value="Estado: listo")
        tk.Label(self, textvariable=self.estado, anchor="w", relief="sunken",
                 padx=8).grid(row=2, column=0, sticky="ew")
    # ===== FIN aporte: MORA (barra de estado) =====


if __name__ == "__main__":
    Aplicacion().mainloop()