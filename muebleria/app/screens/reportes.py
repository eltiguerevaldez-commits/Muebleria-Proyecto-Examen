import tkinter as tk
from tkinter import ttk
from app.db.conexion import obtener_conexion
from app.utilidades import (COLOR_FONDO, COLOR_PANEL, COLOR_PRIMARIO,
                             FUENTE_SUBTITULO, FUENTE_NORMAL, FUENTE_BOTON, moneda)


class VentanaReportes(tk.Frame):
    """Consultas y reportes de ventas: todas, por tipo, y resumen del dia."""

    def __init__(self, master, volver_al_menu):
        super().__init__(master, bg=COLOR_FONDO)
        self.volver_al_menu = volver_al_menu
        self._construir_interfaz()
        self._cargar_reporte()

    def _construir_interfaz(self):
        barra = tk.Frame(self, bg=COLOR_PRIMARIO, height=50)
        barra.pack(fill="x")
        tk.Label(barra, text="Consultas y Reportes de Ventas", font=FUENTE_SUBTITULO,
                 bg=COLOR_PRIMARIO, fg="white").pack(side="left", padx=15, pady=10)
        tk.Button(barra, text="← Menú principal", command=self.volver_al_menu,
                  relief="flat", bg=COLOR_PRIMARIO, fg="white", cursor="hand2").pack(side="right", padx=15)

        filtro = tk.Frame(self, bg=COLOR_FONDO)
        filtro.pack(fill="x", padx=15, pady=10)
        tk.Label(filtro, text="Filtrar por tipo de venta:", bg=COLOR_FONDO, font=FUENTE_NORMAL).pack(side="left")
        self.combo_filtro = ttk.Combobox(filtro, state="readonly", width=15,
                                          values=["Todas", "Contado", "Credito"])
        self.combo_filtro.set("Todas")
        self.combo_filtro.pack(side="left", padx=10)
        tk.Button(filtro, text="Consultar", font=FUENTE_BOTON, bg=COLOR_PRIMARIO, fg="white",
                  relief="flat", padx=10, pady=4, cursor="hand2",
                  command=self._cargar_reporte).pack(side="left")

        self.etiqueta_resumen = tk.Label(self, text="", font=FUENTE_SUBTITULO, bg=COLOR_FONDO)
        self.etiqueta_resumen.pack(anchor="w", padx=15)

        columnas = ("id", "fecha", "cliente", "tipo", "plazo", "metodo", "subtotal", "itbis", "total")
        self.tabla = ttk.Treeview(self, columns=columnas, show="headings", height=16)
        encabezados = ["Factura", "Fecha", "Cliente", "Tipo", "Plazo", "Método pago", "Subtotal", "ITBIS", "Total"]
        for col, texto in zip(columnas, encabezados):
            self.tabla.heading(col, text=texto)
            self.tabla.column(col, width=110, anchor="center")
        self.tabla.pack(fill="both", expand=True, padx=15, pady=10)

    def _cargar_reporte(self):
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        conexion = obtener_conexion()
        if conexion is None:
            return
        try:
            cursor = conexion.cursor(dictionary=True)
            filtro = self.combo_filtro.get()
            consulta = """SELECT f.id_factura, f.fecha, CONCAT(c.nombre,' ',IFNULL(c.apellido,'')) AS cliente,
                                 f.tipo_venta, f.plazo_dias, f.metodo_pago, f.subtotal, f.itbis, f.total
                          FROM facturas f JOIN clientes c ON f.id_cliente = c.id_cliente
                          WHERE f.estado = 'Activa' """
            parametros = ()
            if filtro != "Todas":
                consulta += " AND f.tipo_venta=%s"
                parametros = (filtro,)
            consulta += " ORDER BY f.fecha DESC"

            cursor.execute(consulta, parametros)
            filas = cursor.fetchall()

            total_general = 0
            for f in filas:
                self.tabla.insert("", "end", values=(
                    f["id_factura"], f["fecha"].strftime("%d/%m/%Y %H:%M"), f["cliente"],
                    f["tipo_venta"], f["plazo_dias"] or "-", f["metodo_pago"],
                    f"{f['subtotal']:.2f}", f"{f['itbis']:.2f}", f"{f['total']:.2f}"
                ))
                total_general += float(f["total"])

            self.etiqueta_resumen.config(
                text=f"Total de facturas: {len(filas)}    Monto total vendido: {moneda(total_general)}"
            )
            cursor.close()
        finally:
            conexion.close()
