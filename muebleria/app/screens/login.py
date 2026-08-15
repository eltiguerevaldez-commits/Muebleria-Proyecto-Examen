import tkinter as tk
from tkinter import messagebox
from app.db.conexion import obtener_conexion
from app.utilidades import (COLOR_FONDO, COLOR_PANEL, COLOR_PRIMARIO,
                             COLOR_TEXTO, FUENTE_TITULO, FUENTE_NORMAL, FUENTE_BOTON)


class VentanaLogin(tk.Frame):
    """Pantalla de acceso al sistema (autenticacion de usuario)."""

    def __init__(self, master, al_iniciar_sesion):
        super().__init__(master, bg=COLOR_FONDO)
        self.al_iniciar_sesion = al_iniciar_sesion
        self._construir_interfaz()

    def _construir_interfaz(self):
        panel = tk.Frame(self, bg=COLOR_PANEL, padx=40, pady=40,
                          highlightbackground=COLOR_PRIMARIO, highlightthickness=2)
        panel.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(panel, text="Caribbean Furniture Store SRL", font=FUENTE_TITULO,
                 bg=COLOR_PANEL, fg=COLOR_PRIMARIO).grid(row=0, column=0, columnspan=2, pady=(0, 5))
        tk.Label(panel, text="Sistema de Gestión de Ventas", font=FUENTE_NORMAL,
                 bg=COLOR_PANEL, fg=COLOR_TEXTO).grid(row=1, column=0, columnspan=2, pady=(0, 20))

        tk.Label(panel, text="Usuario:", font=FUENTE_NORMAL, bg=COLOR_PANEL).grid(
            row=2, column=0, sticky="w", pady=6)
        self.entrada_usuario = tk.Entry(panel, font=FUENTE_NORMAL, width=25)
        self.entrada_usuario.grid(row=2, column=1, pady=6)
        self.entrada_usuario.insert(0, "admin")

        tk.Label(panel, text="Contraseña:", font=FUENTE_NORMAL, bg=COLOR_PANEL).grid(
            row=3, column=0, sticky="w", pady=6)
        self.entrada_clave = tk.Entry(panel, font=FUENTE_NORMAL, width=25, show="*")
        self.entrada_clave.grid(row=3, column=1, pady=6)

        boton = tk.Button(panel, text="Iniciar sesión", font=FUENTE_BOTON, bg=COLOR_PRIMARIO,
                           fg="white", activebackground="#5a3620", relief="flat",
                           padx=10, pady=8, cursor="hand2", command=self._validar_acceso)
        boton.grid(row=4, column=0, columnspan=2, pady=(20, 0), sticky="ew")

        self.entrada_clave.bind("<Return>", lambda e: self._validar_acceso())

    def _validar_acceso(self):
        usuario = self.entrada_usuario.get().strip()
        clave = self.entrada_clave.get().strip()

        if not usuario or not clave:
            messagebox.showwarning("Campos vacíos", "Debe ingresar usuario y contraseña.")
            return

        conexion = obtener_conexion()
        if conexion is None:
            messagebox.showerror("Error de conexión",
                                  "No se pudo conectar a la base de datos MySQL.\n"
                                  "Verifique app/db/conexion.py")
            return

        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute(
                "SELECT id_usuario, nombre, usuario, rol FROM usuarios WHERE usuario=%s AND clave=%s",
                (usuario, clave)
            )
            fila = cursor.fetchone()
            cursor.close()
        finally:
            conexion.close()

        if fila:
            self.al_iniciar_sesion(fila)
        else:
            messagebox.showerror("Acceso denegado", "Usuario o contraseña incorrectos.")
