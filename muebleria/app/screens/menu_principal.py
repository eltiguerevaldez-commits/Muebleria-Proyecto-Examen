import tkinter as tk
from app.utilidades import (COLOR_FONDO, COLOR_PANEL, COLOR_PRIMARIO, COLOR_ACENTO,
                             COLOR_TEXTO, FUENTE_TITULO, FUENTE_NORMAL, FUENTE_BOTON)


class VentanaMenuPrincipal(tk.Frame):
    """Menu principal: da acceso a todos los modulos del sistema."""

    def __init__(self, master, usuario, navegar_a, cerrar_sesion):
        super().__init__(master, bg=COLOR_FONDO)
        self.usuario = usuario
        self.navegar_a = navegar_a
        self.cerrar_sesion = cerrar_sesion
        self._construir_interfaz()

    def _construir_interfaz(self):
        barra_superior = tk.Frame(self, bg=COLOR_PRIMARIO, height=60)
        barra_superior.pack(fill="x", side="top")
        tk.Label(barra_superior, text="Caribbean Furniture Store SRL — Menú Principal",
                 font=FUENTE_TITULO, bg=COLOR_PRIMARIO, fg="white").pack(side="left", padx=20, pady=10)
        tk.Label(barra_superior, text=f"Usuario: {self.usuario['nombre']} ({self.usuario['rol']})",
                 font=FUENTE_NORMAL, bg=COLOR_PRIMARIO, fg="white").pack(side="right", padx=20)

        contenedor = tk.Frame(self, bg=COLOR_FONDO)
        contenedor.place(relx=0.5, rely=0.55, anchor="center")

        opciones = [
            ("👤  Clientes", "clientes"),
            ("🛋️  Productos", "productos"),
            ("🧾  Punto de Venta / Factura", "punto_venta"),
            ("📊  Consultas y Reportes", "reportes"),
            ("💰  Cuentas por Cobrar", "cuentas_por_cobrar"),
        ]

        for i, (texto, destino) in enumerate(opciones):
            fila, col = divmod(i, 3)
            boton = tk.Button(
                contenedor, text=texto, font=FUENTE_BOTON, bg=COLOR_PANEL, fg=COLOR_TEXTO,
                activebackground=COLOR_ACENTO, relief="flat", width=24, height=4,
                cursor="hand2", command=lambda d=destino: self.navegar_a(d)
            )
            boton.grid(row=fila, column=col, padx=12, pady=12)

        boton_salir = tk.Button(self, text="Cerrar sesión", font=FUENTE_BOTON, bg="#a3372f",
                                 fg="white", relief="flat", padx=10, pady=6, cursor="hand2",
                                 command=self.cerrar_sesion)
        boton_salir.pack(side="bottom", pady=20)
