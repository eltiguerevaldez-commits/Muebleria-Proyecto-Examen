import tkinter as tk
from tkinter import ttk, messagebox
from app.db.conexion import obtener_conexion
from app.utilidades import (COLOR_FONDO, COLOR_PANEL, COLOR_PRIMARIO,
                             FUENTE_SUBTITULO, FUENTE_NORMAL, FUENTE_BOTON)


class VentanaClientes(tk.Frame):
    """CRUD completo de clientes (crear, consultar, actualizar, eliminar)."""

    def __init__(self, master, volver_al_menu):
        super().__init__(master, bg=COLOR_FONDO)
        self.volver_al_menu = volver_al_menu
        self.id_seleccionado = None
        self._construir_interfaz()
        self._cargar_clientes()

    def _construir_interfaz(self):
        barra = tk.Frame(self, bg=COLOR_PRIMARIO, height=50)
        barra.pack(fill="x")
        tk.Label(barra, text="Gestión de Clientes", font=FUENTE_SUBTITULO,
                 bg=COLOR_PRIMARIO, fg="white").pack(side="left", padx=15, pady=10)
        tk.Button(barra, text="← Menú principal", command=self.volver_al_menu,
                  relief="flat", bg=COLOR_PRIMARIO, fg="white", cursor="hand2").pack(side="right", padx=15)

        cuerpo = tk.Frame(self, bg=COLOR_FONDO)
        cuerpo.pack(fill="both", expand=True, padx=15, pady=15)

        # ---- Formulario ----
        formulario = tk.LabelFrame(cuerpo, text="Datos del cliente", font=FUENTE_NORMAL,
                                    bg=COLOR_PANEL, padx=15, pady=15)
        formulario.pack(fill="x", pady=(0, 10))

        etiquetas = ["Nombre*", "Apellido", "Cédula*", "Teléfono", "Dirección", "Correo", "Límite de crédito"]
        self.campos = {}
        for i, etiqueta in enumerate(etiquetas):
            fila, col = divmod(i, 4)
            tk.Label(formulario, text=etiqueta, bg=COLOR_PANEL, font=FUENTE_NORMAL).grid(
                row=fila * 2, column=col, sticky="w", padx=5, pady=(4, 0))
            entrada = tk.Entry(formulario, font=FUENTE_NORMAL, width=22)
            entrada.grid(row=fila * 2 + 1, column=col, padx=5, pady=(0, 8))
            self.campos[etiqueta] = entrada

        botones = tk.Frame(formulario, bg=COLOR_PANEL)
        botones.grid(row=4, column=0, columnspan=4, pady=(10, 0), sticky="w")
        tk.Button(botones, text="Guardar / Crear", font=FUENTE_BOTON, bg=COLOR_PRIMARIO, fg="white",
                  relief="flat", padx=10, pady=5, cursor="hand2", command=self._guardar).pack(side="left", padx=4)
        tk.Button(botones, text="Actualizar", font=FUENTE_BOTON, bg="#3a7d44", fg="white",
                  relief="flat", padx=10, pady=5, cursor="hand2", command=self._actualizar).pack(side="left", padx=4)
        tk.Button(botones, text="Eliminar", font=FUENTE_BOTON, bg="#a3372f", fg="white",
                  relief="flat", padx=10, pady=5, cursor="hand2", command=self._eliminar).pack(side="left", padx=4)
        tk.Button(botones, text="Limpiar", font=FUENTE_BOTON, bg="#888", fg="white",
                  relief="flat", padx=10, pady=5, cursor="hand2", command=self._limpiar).pack(side="left", padx=4)

        # ---- Tabla ----
        columnas = ("id", "nombre", "apellido", "cedula", "telefono", "correo", "limite")
        self.tabla = ttk.Treeview(cuerpo, columns=columnas, show="headings", height=12)
        encabezados = ["ID", "Nombre", "Apellido", "Cédula", "Teléfono", "Correo", "Límite crédito"]
        for col, texto in zip(columnas, encabezados):
            self.tabla.heading(col, text=texto)
            self.tabla.column(col, width=110, anchor="center")
        self.tabla.pack(fill="both", expand=True)
        self.tabla.bind("<<TreeviewSelect>>", self._seleccionar_fila)

    # ---------------------------------------------------------------
    def _cargar_clientes(self):
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
        conexion = obtener_conexion()
        if conexion is None:
            return
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM clientes ORDER BY id_cliente DESC")
            for c in cursor.fetchall():
                self.tabla.insert("", "end", values=(
                    c["id_cliente"], c["nombre"], c["apellido"] or "", c["cedula"],
                    c["telefono"] or "", c["correo"] or "", f"{c['limite_credito']:.2f}"
                ))
            cursor.close()
        finally:
            conexion.close()

    def _seleccionar_fila(self, evento):
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        valores = self.tabla.item(seleccion[0])["values"]
        self.id_seleccionado = valores[0]
        self.campos["Nombre*"].delete(0, tk.END); self.campos["Nombre*"].insert(0, valores[1])
        self.campos["Apellido"].delete(0, tk.END); self.campos["Apellido"].insert(0, valores[2])
        self.campos["Cédula*"].delete(0, tk.END); self.campos["Cédula*"].insert(0, valores[3])
        self.campos["Teléfono"].delete(0, tk.END); self.campos["Teléfono"].insert(0, valores[4])
        self.campos["Correo"].delete(0, tk.END); self.campos["Correo"].insert(0, valores[5])
        self.campos["Límite de crédito"].delete(0, tk.END); self.campos["Límite de crédito"].insert(0, valores[6])

    def _obtener_datos_formulario(self):
        nombre = self.campos["Nombre*"].get().strip()
        cedula = self.campos["Cédula*"].get().strip()
        if not nombre or not cedula:
            messagebox.showwarning("Datos incompletos", "Nombre y cédula son obligatorios.")
            return None
        try:
            limite = float(self.campos["Límite de crédito"].get().strip() or 0)
        except ValueError:
            messagebox.showwarning("Dato inválido", "El límite de crédito debe ser numérico.")
            return None
        return (
            nombre,
            self.campos["Apellido"].get().strip(),
            cedula,
            self.campos["Teléfono"].get().strip(),
            self.campos["Dirección"].get().strip(),
            self.campos["Correo"].get().strip(),
            limite,
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
                """INSERT INTO clientes (nombre, apellido, cedula, telefono, direccion, correo, limite_credito)
                   VALUES (%s,%s,%s,%s,%s,%s,%s)""", datos
            )
            conexion.commit()
            cursor.close()
            messagebox.showinfo("Éxito", "Cliente creado correctamente.")
            self._limpiar()
            self._cargar_clientes()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el cliente:\n{e}")
        finally:
            conexion.close()

    def _actualizar(self):
        if self.id_seleccionado is None:
            messagebox.showwarning("Sin selección", "Seleccione un cliente de la tabla primero.")
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
                """UPDATE clientes SET nombre=%s, apellido=%s, cedula=%s, telefono=%s,
                   direccion=%s, correo=%s, limite_credito=%s WHERE id_cliente=%s""",
                datos + (self.id_seleccionado,)
            )
            conexion.commit()
            cursor.close()
            messagebox.showinfo("Éxito", "Cliente actualizado correctamente.")
            self._limpiar()
            self._cargar_clientes()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el cliente:\n{e}")
        finally:
            conexion.close()

    def _eliminar(self):
        if self.id_seleccionado is None:
            messagebox.showwarning("Sin selección", "Seleccione un cliente de la tabla primero.")
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar este cliente?"):
            return
        conexion = obtener_conexion()
        if conexion is None:
            return
        try:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM clientes WHERE id_cliente=%s", (self.id_seleccionado,))
            conexion.commit()
            cursor.close()
            self._limpiar()
            self._cargar_clientes()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar (puede tener facturas asociadas):\n{e}")
        finally:
            conexion.close()

    def _limpiar(self):
        for entrada in self.campos.values():
            entrada.delete(0, tk.END)
        self.id_seleccionado = None
