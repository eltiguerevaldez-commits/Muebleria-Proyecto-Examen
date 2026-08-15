import tkinter as tk
from tkinter import ttk, messagebox
from app.db.conexion import obtener_conexion
from app.utilidades import (COLOR_FONDO, COLOR_PANEL, COLOR_PRIMARIO, ITBIS,
                             FUENTE_SUBTITULO, FUENTE_NORMAL, FUENTE_BOTON, moneda)


class VentanaPuntoVenta(tk.Frame):
    """Punto de venta: arma el carrito, calcula totales y genera la factura
    (contado o credito a 30/45/60 dias) contra la base de datos."""

    def __init__(self, master, usuario, volver_al_menu):
        super().__init__(master, bg=COLOR_FONDO)
        self.usuario = usuario
        self.volver_al_menu = volver_al_menu
        self.clientes = {}     # "nombre - cedula" -> id_cliente
        self.productos = {}    # "nombre" -> dict(id, precio, stock)
        self.carrito = []      # lista de dict(id_producto, nombre, cantidad, precio, subtotal)
        self._construir_interfaz()
        self._cargar_clientes()
        self._cargar_productos()

    def _construir_interfaz(self):
        barra = tk.Frame(self, bg=COLOR_PRIMARIO, height=50)
        barra.pack(fill="x")
        tk.Label(barra, text="Punto de Venta — Generar Factura", font=FUENTE_SUBTITULO,
                 bg=COLOR_PRIMARIO, fg="white").pack(side="left", padx=15, pady=10)
        tk.Button(barra, text="← Menú principal", command=self.volver_al_menu,
                  relief="flat", bg=COLOR_PRIMARIO, fg="white", cursor="hand2").pack(side="right", padx=15)

        cuerpo = tk.Frame(self, bg=COLOR_FONDO)
        cuerpo.pack(fill="both", expand=True, padx=15, pady=15)

        # ---- Datos de la venta ----
        panel_datos = tk.LabelFrame(cuerpo, text="Datos de la venta", font=FUENTE_NORMAL,
                                     bg=COLOR_PANEL, padx=15, pady=10)
        panel_datos.pack(fill="x")

        tk.Label(panel_datos, text="Cliente*", bg=COLOR_PANEL, font=FUENTE_NORMAL).grid(row=0, column=0, sticky="w")
        self.combo_cliente = ttk.Combobox(panel_datos, state="readonly", width=30)
        self.combo_cliente.grid(row=1, column=0, padx=(0, 15), pady=(0, 8))

        tk.Label(panel_datos, text="Tipo de venta*", bg=COLOR_PANEL, font=FUENTE_NORMAL).grid(row=0, column=1, sticky="w")
        self.combo_tipo = ttk.Combobox(panel_datos, state="readonly", width=15,
                                        values=["Contado", "Credito"])
        self.combo_tipo.set("Contado")
        self.combo_tipo.grid(row=1, column=1, padx=(0, 15), pady=(0, 8))
        self.combo_tipo.bind("<<ComboboxSelected>>", self._al_cambiar_tipo_venta)

        tk.Label(panel_datos, text="Plazo (días)", bg=COLOR_PANEL, font=FUENTE_NORMAL).grid(row=0, column=2, sticky="w")
        self.combo_plazo = ttk.Combobox(panel_datos, state="disabled", width=10, values=[30, 45, 60])
        self.combo_plazo.grid(row=1, column=2, padx=(0, 15), pady=(0, 8))

        tk.Label(panel_datos, text="Método de pago", bg=COLOR_PANEL, font=FUENTE_NORMAL).grid(row=0, column=3, sticky="w")
        self.combo_metodo = ttk.Combobox(panel_datos, state="readonly", width=15,
                                          values=["Efectivo", "Tarjeta", "Transferencia"])
        self.combo_metodo.set("Efectivo")
        self.combo_metodo.grid(row=1, column=3, padx=(0, 15), pady=(0, 8))

        # ---- Agregar productos ----
        panel_producto = tk.LabelFrame(cuerpo, text="Agregar producto", font=FUENTE_NORMAL,
                                        bg=COLOR_PANEL, padx=15, pady=10)
        panel_producto.pack(fill="x", pady=10)

        tk.Label(panel_producto, text="Producto*", bg=COLOR_PANEL, font=FUENTE_NORMAL).grid(row=0, column=0, sticky="w")
        self.combo_producto = ttk.Combobox(panel_producto, state="readonly", width=35)
        self.combo_producto.grid(row=1, column=0, padx=(0, 15))
        self.combo_producto.bind("<<ComboboxSelected>>", self._mostrar_precio_stock)

        tk.Label(panel_producto, text="Cantidad*", bg=COLOR_PANEL, font=FUENTE_NORMAL).grid(row=0, column=1, sticky="w")
        self.entrada_cantidad = tk.Entry(panel_producto, font=FUENTE_NORMAL, width=8)
        self.entrada_cantidad.grid(row=1, column=1, padx=(0, 15))

        self.etiqueta_info = tk.Label(panel_producto, text="Precio: -    Stock: -",
                                       bg=COLOR_PANEL, font=FUENTE_NORMAL)
        self.etiqueta_info.grid(row=1, column=2, padx=(0, 15))

        tk.Button(panel_producto, text="Agregar al carrito", font=FUENTE_BOTON, bg=COLOR_PRIMARIO,
                  fg="white", relief="flat", padx=10, pady=5, cursor="hand2",
                  command=self._agregar_al_carrito).grid(row=1, column=3)

        # ---- Carrito ----
        columnas = ("producto", "cantidad", "precio", "subtotal")
        self.tabla_carrito = ttk.Treeview(cuerpo, columns=columnas, show="headings", height=8)
        for col, texto in zip(columnas, ["Producto", "Cantidad", "Precio", "Subtotal"]):
            self.tabla_carrito.heading(col, text=texto)
            self.tabla_carrito.column(col, width=150, anchor="center")
        self.tabla_carrito.pack(fill="both", expand=True, pady=(0, 10))

        pie = tk.Frame(cuerpo, bg=COLOR_FONDO)
        pie.pack(fill="x")

        tk.Button(pie, text="Quitar seleccionado", font=FUENTE_BOTON, bg="#a3372f", fg="white",
                  relief="flat", padx=10, pady=6, cursor="hand2",
                  command=self._quitar_del_carrito).pack(side="left")

        self.etiqueta_totales = tk.Label(pie, text="Subtotal: RD$ 0.00   ITBIS: RD$ 0.00   Total: RD$ 0.00",
                                          font=FUENTE_SUBTITULO, bg=COLOR_FONDO)
        self.etiqueta_totales.pack(side="left", padx=30)

        tk.Button(pie, text="Generar Factura", font=FUENTE_BOTON, bg="#3a7d44", fg="white",
                  relief="flat", padx=15, pady=6, cursor="hand2",
                  command=self._generar_factura).pack(side="right")

    # ---------------------------------------------------------------
    def _al_cambiar_tipo_venta(self, evento):
        if self.combo_tipo.get() == "Credito":
            self.combo_plazo.config(state="readonly")
            self.combo_plazo.set(30)
        else:
            self.combo_plazo.set("")
            self.combo_plazo.config(state="disabled")

    def _cargar_clientes(self):
        conexion = obtener_conexion()
        if conexion is None:
            return
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT id_cliente, nombre, apellido, cedula FROM clientes ORDER BY nombre")
            filas = cursor.fetchall()
            cursor.close()
            self.clientes = {}
            valores = []
            for c in filas:
                etiqueta = f"{c['nombre']} {c['apellido'] or ''} - {c['cedula']}".strip()
                self.clientes[etiqueta] = c["id_cliente"]
                valores.append(etiqueta)
            self.combo_cliente["values"] = valores
        finally:
            conexion.close()

    def _cargar_productos(self):
        conexion = obtener_conexion()
        if conexion is None:
            return
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT id_producto, nombre, precio, stock FROM productos ORDER BY nombre")
            filas = cursor.fetchall()
            cursor.close()
            self.productos = {p["nombre"]: p for p in filas}
            self.combo_producto["values"] = list(self.productos.keys())
        finally:
            conexion.close()

    def _mostrar_precio_stock(self, evento):
        nombre = self.combo_producto.get()
        p = self.productos.get(nombre)
        if p:
            self.etiqueta_info.config(text=f"Precio: {moneda(p['precio'])}    Stock: {p['stock']}")

    def _agregar_al_carrito(self):
        nombre = self.combo_producto.get()
        if not nombre:
            messagebox.showwarning("Falta producto", "Seleccione un producto.")
            return
        try:
            cantidad = int(self.entrada_cantidad.get().strip())
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Cantidad inválida", "Ingrese una cantidad numérica mayor a cero.")
            return

        producto = self.productos[nombre]
        # Sumar lo que ya está en el carrito de este mismo producto
        ya_en_carrito = sum(item["cantidad"] for item in self.carrito if item["id_producto"] == producto["id_producto"])
        if cantidad + ya_en_carrito > producto["stock"]:
            messagebox.showwarning("Stock insuficiente",
                                    f"Solo hay {producto['stock']} unidades disponibles de '{nombre}'.")
            return

        subtotal = cantidad * float(producto["precio"])
        self.carrito.append({
            "id_producto": producto["id_producto"],
            "nombre": nombre,
            "cantidad": cantidad,
            "precio": float(producto["precio"]),
            "subtotal": subtotal
        })
        self.tabla_carrito.insert("", "end", values=(nombre, cantidad, moneda(producto["precio"]), moneda(subtotal)))
        self.entrada_cantidad.delete(0, tk.END)
        self._actualizar_totales()

    def _quitar_del_carrito(self):
        seleccion = self.tabla_carrito.selection()
        if not seleccion:
            return
        indice = self.tabla_carrito.index(seleccion[0])
        self.tabla_carrito.delete(seleccion[0])
        del self.carrito[indice]
        self._actualizar_totales()

    def _calcular_totales(self):
        subtotal = sum(item["subtotal"] for item in self.carrito)
        itbis = subtotal * ITBIS
        total = subtotal + itbis
        return subtotal, itbis, total

    def _actualizar_totales(self):
        subtotal, itbis, total = self._calcular_totales()
        self.etiqueta_totales.config(
            text=f"Subtotal: {moneda(subtotal)}   ITBIS (18%): {moneda(itbis)}   Total: {moneda(total)}"
        )

    def _generar_factura(self):
        if not self.carrito:
            messagebox.showwarning("Carrito vacío", "Agregue al menos un producto.")
            return
        cliente_etiqueta = self.combo_cliente.get()
        if not cliente_etiqueta:
            messagebox.showwarning("Falta cliente", "Seleccione un cliente.")
            return
        tipo_venta = self.combo_tipo.get()
        plazo = None
        if tipo_venta == "Credito":
            plazo = self.combo_plazo.get()
            if not plazo:
                messagebox.showwarning("Falta plazo", "Seleccione el plazo de crédito (30, 45 o 60 días).")
                return
            plazo = int(plazo)

        subtotal, itbis, total = self._calcular_totales()
        id_cliente = self.clientes[cliente_etiqueta]

        conexion = obtener_conexion()
        if conexion is None:
            return
        try:
            cursor = conexion.cursor()
            cursor.execute(
                """INSERT INTO facturas (id_cliente, id_usuario, tipo_venta, plazo_dias,
                   subtotal, itbis, total, metodo_pago)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
                (id_cliente, self.usuario["id_usuario"], tipo_venta, plazo,
                 subtotal, itbis, total, self.combo_metodo.get())
            )
            id_factura = cursor.lastrowid

            for item in self.carrito:
                cursor.execute(
                    """INSERT INTO detalle_factura (id_factura, id_producto, cantidad, precio, subtotal)
                       VALUES (%s,%s,%s,%s,%s)""",
                    (id_factura, item["id_producto"], item["cantidad"], item["precio"], item["subtotal"])
                )
            conexion.commit()
            cursor.close()

            mensaje = f"Factura #{id_factura} generada correctamente.\nTotal: {moneda(total)}"
            if tipo_venta == "Credito":
                mensaje += f"\nVenta a crédito a {plazo} días. Se registró en Cuentas por Cobrar."
            messagebox.showinfo("Factura generada", mensaje)

            self._limpiar_venta()
            self._cargar_productos()  # refrescar stock

        except Exception as e:
            conexion.rollback()
            messagebox.showerror("Error", f"No se pudo generar la factura:\n{e}")
        finally:
            conexion.close()

    def _limpiar_venta(self):
        self.carrito = []
        for fila in self.tabla_carrito.get_children():
            self.tabla_carrito.delete(fila)
        self.combo_cliente.set("")
        self.combo_tipo.set("Contado")
        self.combo_plazo.set("")
        self.combo_plazo.config(state="disabled")
        self._actualizar_totales()
