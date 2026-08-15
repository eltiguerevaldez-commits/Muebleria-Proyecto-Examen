import tkinter as tk
from tkinter import ttk, messagebox
from app.db.conexion import obtener_conexion
from app.utilidades import (COLOR_FONDO, COLOR_PANEL, COLOR_PRIMARIO,
                             FUENTE_SUBTITULO, FUENTE_NORMAL, FUENTE_BOTON)


class VentanaProductos(tk.Frame):
    """CRUD completo de productos."""

    def __init__(self, master, volver_al_menu):
        super().__init__(master, bg=COLOR_FONDO)
        self.volver_al_menu = volver_al_menu
        self.id_seleccionado = None
        self.categorias = {}  # nombre -> id
        self._construir_interfaz()
        self._cargar_categorias()
        self._cargar_productos()

    def _construir_interfaz(self):
        barra = tk.Frame(self, bg=COLOR_PRIMARIO, height=50)
        barra.pack(fill="x")
        tk.Label(barra, text="Gestión de Productos", font=FUENTE_SUBTITULO,
                 bg=COLOR_PRIMARIO, fg="white").pack(side="left", padx=15, pady=10)
        tk.Button(barra, text="← Menú principal", command=self.volver_al_menu,
                  relief="flat", bg=COLOR_PRIMARIO, fg="white", cursor="hand2").pack(side="right", padx=15)

        cuerpo = tk.Frame(self, bg=COLOR_FONDO)
        cuerpo.pack(fill="both", expand=True, padx=15, pady=15)

        formulario = tk.LabelFrame(cuerpo, text="Datos del producto", font=FUENTE_NORMAL,
                                    bg=COLOR_PANEL, padx=15, pady=15)
        formulario.pack(fill="x", pady=(0, 10))

        tk.Label(formulario, text="Categoría*", bg=COLOR_PANEL, font=FUENTE_NORMAL).grid(
            row=0, column=0, sticky="w", padx=5)
        self.combo_categoria = ttk.Combobox(formulario, state="readonly", width=20)
        self.combo_categoria.grid(row=1, column=0, padx=5, pady=(0, 8))

        etiquetas = ["Nombre*", "Material", "Color", "Precio*", "Stock*"]
        self.campos = {}
        for i, etiqueta in enumerate(etiquetas):
            tk.Label(formulario, text=etiqueta, bg=COLOR_PANEL, font=FUENTE_NORMAL).grid(
                row=0, column=i + 1, sticky="w", padx=5)
            entrada = tk.Entry(formulario, font=FUENTE_NORMAL, width=18)
            entrada.grid(row=1, column=i + 1, padx=5, pady=(0, 8))
            self.campos[etiqueta] = entrada

        tk.Label(formulario, text="Descripción", bg=COLOR_PANEL, font=FUENTE_NORMAL).grid(
            row=2, column=0, sticky="w", padx=5)
        self.entrada_descripcion = tk.Entry(formulario, font=FUENTE_NORMAL, width=70)
        self.entrada_descripcion.grid(row=3, column=0, columnspan=6, sticky="w", padx=5, pady=(0, 8))

        botones = tk.Frame(formulario, bg=COLOR_PANEL)
        botones.grid(row=4, column=0, columnspan=6, pady=(10, 0), sticky="w")
        tk.Button(botones, text="Guardar / Crear", font=FUENTE_BOTON, bg=COLOR_PRIMARIO, fg="white",
                  relief="flat", padx=10, pady=5, cursor="hand2", command=self._guardar).pack(side="left", padx=4)
        tk.Button(botones, text="Actualizar", font=FUENTE_BOTON, bg="#3a7d44", fg="white",
                  relief="flat", padx=10, pady=5, cursor="hand2", command=self._actualizar).pack(side="left", padx=4)
        tk.Button(botones, text="Eliminar", font=FUENTE_BOTON, bg="#a3372f", fg="white",
                  relief="flat", padx=10, pady=5, cursor="hand2", command=self._eliminar).pack(side="left", padx=4)
        tk.Button(botones, text="Limpiar", font=FUENTE_BOTON, bg="#888", fg="white",
                  relief="flat", padx=10, pady=5, cursor="hand2", command=self._limpiar).pack(side="left", padx=4)

        columnas = ("id", "categoria", "nombre", "material", "color", "precio", "stock")
        self.tabla = ttk.Treeview(cuerpo, columns=columnas, show="headings", height=12)
        encabezados = ["ID", "Categoría", "Nombre", "Material", "Color", "Precio", "Stock"]
        for col, texto in zip(columnas, encabezados):
            self.tabla.heading(col, text=texto)
            self.tabla.column(col, width=110, anchor="center")
        self.tabla.pack(fill="both", expand=True)
        self.tabla.bind("<<TreeviewSelect>>", self._seleccionar_fila)

    # ---------------------------------------------------------------
    def _cargar_categorias(self):
        conexion = obtener_conexion()
        if conexion is None:
            return
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT id_categoria, nombre FROM categorias ORDER BY nombre")
            filas = cursor.fetchall()
            cursor.close()
            self.categorias = {f["nombre"]: f["id_categoria"] for f in filas}
            self.combo_categoria["values"] = list(self.categorias.keys())
        finally:
            conexion.close()

    def _cargar_productos(self):
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
        conexion = obtener_conexion()
        if conexion is None:
            return
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("""SELECT p.*, c.nombre AS categoria_nombre
                               FROM productos p JOIN categorias c ON p.id_categoria = c.id_categoria
                               ORDER BY p.id_producto DESC""")
            for p in cursor.fetchall():
                self.tabla.insert("", "end", values=(
                    p["id_producto"], p["categoria_nombre"], p["nombre"], p["material"] or "",
                    p["color"] or "", f"{p['precio']:.2f}", p["stock"]
                ))
            cursor.close()
        finally:
            conexion.close()

    def _seleccionar_fila(self, evento):
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        v = self.tabla.item(seleccion[0])["values"]
        self.id_seleccionado = v[0]
        self.combo_categoria.set(v[1])
        self.campos["Nombre*"].delete(0, tk.END); self.campos["Nombre*"].insert(0, v[2])
        self.campos["Material"].delete(0, tk.END); self.campos["Material"].insert(0, v[3])
        self.campos["Color"].delete(0, tk.END); self.campos["Color"].insert(0, v[4])
        self.campos["Precio*"].delete(0, tk.END); self.campos["Precio*"].insert(0, v[5])
        self.campos["Stock*"].delete(0, tk.END); self.campos["Stock*"].insert(0, v[6])

    def _obtener_datos_formulario(self):
        nombre = self.campos["Nombre*"].get().strip()
        categoria_nombre = self.combo_categoria.get()
        if not nombre or not categoria_nombre:
            messagebox.showwarning("Datos incompletos", "Nombre y categoría son obligatorios.")
            return None
        try:
            precio = float(self.campos["Precio*"].get().strip())
            stock = int(self.campos["Stock*"].get().strip())
        except ValueError:
            messagebox.showwarning("Dato inválido", "Precio y stock deben ser numéricos.")
            return None
        return (
            self.categorias[categoria_nombre],
            nombre,
            self.entrada_descripcion.get().strip(),
            self.campos["Material"].get().strip(),
            self.campos["Color"].get().strip(),
            precio,
            stock,
        )

    def _guardar(self):
        datos = self._obtener_datos_formulario()
        if datos is None:
            return
        conexion = obtener_conexion()
        if conexion is None:
            return
        try:
            cursor = conexion.cursor()
            cursor.execute(
                """INSERT INTO productos (id_categoria, nombre, descripcion, material, color, precio, stock)
                   VALUES (%s,%s,%s,%s,%s,%s,%s)""", datos
            )
            conexion.commit()
            cursor.close()
            messagebox.showinfo("Éxito", "Producto creado correctamente.")
            self._limpiar()
            self._cargar_productos()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el producto:\n{e}")
        finally:
            conexion.close()

    def _actualizar(self):
        if self.id_seleccionado is None:
            messagebox.showwarning("Sin selección", "Seleccione un producto de la tabla primero.")
            return
        datos = self._obtener_datos_formulario()
        if datos is None:
            return
        conexion = obtener_conexion()
        if conexion is None:
            return
        try:
            cursor = conexion.cursor()
            cursor.execute(
                """UPDATE productos SET id_categoria=%s, nombre=%s, descripcion=%s, material=%s,
                   color=%s, precio=%s, stock=%s WHERE id_producto=%s""",
                datos + (self.id_seleccionado,)
            )
            conexion.commit()
            cursor.close()
            messagebox.showinfo("Éxito", "Producto actualizado correctamente.")
            self._limpiar()
            self._cargar_productos()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el producto:\n{e}")
        finally:
            conexion.close()

    def _eliminar(self):
        if self.id_seleccionado is None:
            messagebox.showwarning("Sin selección", "Seleccione un producto de la tabla primero.")
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar este producto?"):
            return
        conexion = obtener_conexion()
        if conexion is None:
            return
        try:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM productos WHERE id_producto=%s", (self.id_seleccionado,))
            conexion.commit()
            cursor.close()
            self._limpiar()
            self._cargar_productos()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar (puede tener ventas asociadas):\n{e}")
        finally:
            conexion.close()

    def _limpiar(self):
        for entrada in self.campos.values():
            entrada.delete(0, tk.END)
        self.entrada_descripcion.delete(0, tk.END)
        self.combo_categoria.set("")
        self.id_seleccionado = None
