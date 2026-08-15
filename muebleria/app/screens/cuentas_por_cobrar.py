import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from app.db.conexion import obtener_conexion
from app.utilidades import (COLOR_FONDO, COLOR_PANEL, COLOR_PRIMARIO,
                             FUENTE_SUBTITULO, FUENTE_NORMAL, FUENTE_BOTON, moneda)


class VentanaCuentasPorCobrar(tk.Frame):
    """Muestra las cuentas por cobrar (ventas a credito) y permite
    registrar pagos/abonos contra ellas."""

    def __init__(self, master, volver_al_menu):
        super().__init__(master, bg=COLOR_FONDO)
        self.volver_al_menu = volver_al_menu
        self.cxc_seleccionada = None
        self._construir_interfaz()
        self._actualizar_vencidas()
        self._cargar_cuentas()

    def _construir_interfaz(self):
        barra = tk.Frame(self, bg=COLOR_PRIMARIO, height=50)
        barra.pack(fill="x")
        tk.Label(barra, text="Cuentas por Cobrar", font=FUENTE_SUBTITULO,
                 bg=COLOR_PRIMARIO, fg="white").pack(side="left", padx=15, pady=10)
        tk.Button(barra, text="← Menú principal", command=self.volver_al_menu,
                  relief="flat", bg=COLOR_PRIMARIO, fg="white", cursor="hand2").pack(side="right", padx=15)

        columnas = ("id", "factura", "cliente", "emision", "vencimiento", "total", "saldo", "estado")
        self.tabla = ttk.Treeview(self, columns=columnas, show="headings", height=14)
        encabezados = ["ID CxC", "Factura", "Cliente", "F. Emisión", "F. Vencimiento", "Monto total", "Saldo", "Estado"]
        for col, texto in zip(columnas, encabezados):
            self.tabla.heading(col, text=texto)
            self.tabla.column(col, width=115, anchor="center")
        self.tabla.pack(fill="both", expand=True, padx=15, pady=10)
        self.tabla.bind("<<TreeviewSelect>>", self._seleccionar_fila)

        panel_pago = tk.LabelFrame(self, text="Registrar pago / abono", font=FUENTE_NORMAL,
                                    bg=COLOR_PANEL, padx=15, pady=10)
        panel_pago.pack(fill="x", padx=15, pady=(0, 15))

        tk.Label(panel_pago, text="Monto a pagar:", bg=COLOR_PANEL, font=FUENTE_NORMAL).grid(row=0, column=0, padx=5)
        self.entrada_monto = tk.Entry(panel_pago, font=FUENTE_NORMAL, width=15)
        self.entrada_monto.grid(row=0, column=1, padx=5)

        tk.Label(panel_pago, text="Método de pago:", bg=COLOR_PANEL, font=FUENTE_NORMAL).grid(row=0, column=2, padx=5)
        self.combo_metodo = ttk.Combobox(panel_pago, state="readonly", width=15,
                                          values=["Efectivo", "Tarjeta", "Transferencia"])
        self.combo_metodo.set("Efectivo")
        self.combo_metodo.grid(row=0, column=3, padx=5)

        tk.Button(panel_pago, text="Registrar pago", font=FUENTE_BOTON, bg="#3a7d44", fg="white",
                  relief="flat", padx=10, pady=5, cursor="hand2",
                  command=self._registrar_pago).grid(row=0, column=4, padx=15)

    # ---------------------------------------------------------------
    def _actualizar_vencidas(self):
        """Marca como 'Vencida' las cuentas pendientes cuya fecha ya paso."""
        conexion = obtener_conexion()
        if conexion is None:
            return
        try:
            cursor = conexion.cursor()
            cursor.execute(
                """UPDATE cuentas_por_cobrar
                   SET estado='Vencida'
                   WHERE estado='Pendiente' AND fecha_vencimiento < %s""",
                (date.today(),)
            )
            conexion.commit()
            cursor.close()
        finally:
            conexion.close()

    def _cargar_cuentas(self):
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
        conexion = obtener_conexion()
        if conexion is None:
            return
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute(
                """SELECT cxc.id_cxc, cxc.id_factura, CONCAT(c.nombre,' ',IFNULL(c.apellido,'')) AS cliente,
                          cxc.fecha_emision, cxc.fecha_vencimiento, cxc.monto_total,
                          cxc.saldo_pendiente, cxc.estado
                   FROM cuentas_por_cobrar cxc JOIN clientes c ON cxc.id_cliente = c.id_cliente
                   ORDER BY cxc.fecha_vencimiento ASC"""
            )
            for c in cursor.fetchall():
                self.tabla.insert("", "end", values=(
                    c["id_cxc"], c["id_factura"], c["cliente"],
                    c["fecha_emision"].strftime("%d/%m/%Y"), c["fecha_vencimiento"].strftime("%d/%m/%Y"),
                    f"{c['monto_total']:.2f}", f"{c['saldo_pendiente']:.2f}", c["estado"]
                ))
            cursor.close()
        finally:
            conexion.close()

    def _seleccionar_fila(self, evento):
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        valores = self.tabla.item(seleccion[0])["values"]
        self.cxc_seleccionada = valores[0]

    def _registrar_pago(self):
        if self.cxc_seleccionada is None:
            messagebox.showwarning("Sin selección", "Seleccione una cuenta por cobrar de la tabla.")
            return
        try:
            monto = float(self.entrada_monto.get().strip())
            if monto <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Monto inválido", "Ingrese un monto numérico mayor a cero.")
            return

        conexion = obtener_conexion()
        if conexion is None:
            return
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT saldo_pendiente FROM cuentas_por_cobrar WHERE id_cxc=%s",
                            (self.cxc_seleccionada,))
            fila = cursor.fetchone()
            if fila is None:
                messagebox.showerror("Error", "Cuenta no encontrada.")
                return
            if monto > float(fila["saldo_pendiente"]):
                messagebox.showwarning("Monto excede el saldo",
                                        f"El saldo pendiente es {moneda(fila['saldo_pendiente'])}.")
                return

            cursor.execute(
                "INSERT INTO pagos (id_cxc, monto, metodo_pago) VALUES (%s,%s,%s)",
                (self.cxc_seleccionada, monto, self.combo_metodo.get())
            )
            conexion.commit()
            cursor.close()
            messagebox.showinfo("Éxito", "Pago registrado correctamente.")
            self.entrada_monto.delete(0, tk.END)
            self._actualizar_vencidas()
            self._cargar_cuentas()
        except Exception as e:
            conexion.rollback()
            messagebox.showerror("Error", f"No se pudo registrar el pago:\n{e}")
        finally:
            conexion.close()
