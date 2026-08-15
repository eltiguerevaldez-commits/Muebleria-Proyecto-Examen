"""
Sistema de Gestión de Ventas - Mueblería
Examen Final - Programación II

Para ejecutar:
    1. Crear la base de datos con database/muebleria_mysql.sql
    2. Configurar usuario/clave en app/db/conexion.py
    3. pip install mysql-connector-python
    4. python main.py

Usuario de prueba: admin / 1234
"""
import tkinter as tk

from app.screens.login import VentanaLogin
from app.screens.menu_principal import VentanaMenuPrincipal
from app.screens.clientes import VentanaClientes
from app.screens.productos import VentanaProductos
from app.screens.punto_venta import VentanaPuntoVenta
from app.screens.reportes import VentanaReportes
from app.screens.cuentas_por_cobrar import VentanaCuentasPorCobrar
from app.utilidades import COLOR_FONDO


class Aplicacion(tk.Tk):
    """Ventana principal que controla la navegación entre pantallas (frames)."""

    def __init__(self):
        super().__init__()
        self.title("Caribbean furniture store SRL - Sistema de Ventas")
        self.geometry("1100x680")
        self.minsize(1000, 620)
        self.configure(bg=COLOR_FONDO)

        self.usuario_actual = None
        self.pantalla_actual = None

        self._mostrar_login()

    # ------------------------------------------------------------
    def _limpiar_pantalla(self):
        if self.pantalla_actual is not None:
            self.pantalla_actual.destroy()

    def _mostrar_login(self):
        self._limpiar_pantalla()
        self.pantalla_actual = VentanaLogin(self, self._al_iniciar_sesion)
        self.pantalla_actual.pack(fill="both", expand=True)

    def _al_iniciar_sesion(self, usuario):
        self.usuario_actual = usuario
        self._mostrar_menu_principal()

    def _mostrar_menu_principal(self):
        self._limpiar_pantalla()
        self.pantalla_actual = VentanaMenuPrincipal(
            self, self.usuario_actual, self._navegar_a, self._cerrar_sesion
        )
        self.pantalla_actual.pack(fill="both", expand=True)

    def _cerrar_sesion(self):
        self.usuario_actual = None
        self._mostrar_login()

    def _navegar_a(self, destino):
        self._limpiar_pantalla()
        if destino == "clientes":
            self.pantalla_actual = VentanaClientes(self, self._mostrar_menu_principal)
        elif destino == "productos":
            self.pantalla_actual = VentanaProductos(self, self._mostrar_menu_principal)
        elif destino == "punto_venta":
            self.pantalla_actual = VentanaPuntoVenta(self, self.usuario_actual, self._mostrar_menu_principal)
        elif destino == "reportes":
            self.pantalla_actual = VentanaReportes(self, self._mostrar_menu_principal)
        elif destino == "cuentas_por_cobrar":
            self.pantalla_actual = VentanaCuentasPorCobrar(self, self._mostrar_menu_principal)
        else:
            self.pantalla_actual = VentanaMenuPrincipal(
                self, self.usuario_actual, self._navegar_a, self._cerrar_sesion
            )
        self.pantalla_actual.pack(fill="both", expand=True)


if __name__ == "__main__":
    app = Aplicacion()
    app.mainloop()
