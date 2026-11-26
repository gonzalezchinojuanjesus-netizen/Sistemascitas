import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from database import conectar


def agregar_medico(nombre_completo, especialidad, consultorio, telefono):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        """
        INSERT INTO medicos (nombre_completo, especialidad, consultorio, telefono)
        VALUES (?, ?, ?, ?)
        """,
        (nombre_completo, especialidad, consultorio, telefono),
    )
    conexion.commit()
    conexion.close()


def listar_medicos():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM medicos ORDER BY nombre_completo")
    medicos = cursor.fetchall()
    conexion.close()
    return medicos


def buscar_medicos(texto):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        """
        SELECT * FROM medicos
        WHERE nombre_completo LIKE ? OR especialidad LIKE ?
        ORDER BY nombre_completo
        """,
        (f"%{texto}%", f"%{texto}%"),
    )
    medicos = cursor.fetchall()
    conexion.close()
    return medicos


def actualizar_medico(id_medico, nombre_completo, especialidad, consultorio, telefono):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        """
        UPDATE medicos
        SET nombre_completo = ?, especialidad = ?, consultorio = ?, telefono = ?
        WHERE id = ?
        """,
        (nombre_completo, especialidad, consultorio, telefono, id_medico),
    )
    conexion.commit()
    conexion.close()


def eliminar_medico(id_medico):
    """Devuelve True si se eliminó, False si el médico tiene citas registradas."""
    conexion = conectar()
    cursor = conexion.cursor()
    try:
        cursor.execute("DELETE FROM medicos WHERE id = ?", (id_medico,))
        conexion.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conexion.close()


class PantallaMedicos(tk.Frame):
    def __init__(self, padre):
        super().__init__(padre, bg="#E8F6F3")
        self.id_seleccionado = None
        self.filas = {}
        self.crear_formulario()
        self.crear_tabla()
        self.cargar_medicos()

    def crear_formulario(self):
        marco = tk.LabelFrame(self, text="Datos del médico", bg="#E8F6F3", padx=10, pady=10)
        marco.pack(fill="x", padx=10, pady=10)

        etiquetas = ["Nombre completo", "Especialidad", "Consultorio", "Teléfono"]
        self.campos = {}
        for i, texto in enumerate(etiquetas):
            fila, col = i // 2, (i % 2) * 2
            tk.Label(marco, text=texto, bg="#E8F6F3").grid(row=fila, column=col, sticky="e", padx=5, pady=5)
            entrada = tk.Entry(marco, width=30)
            entrada.grid(row=fila, column=col + 1, padx=5, pady=5)
            self.campos[texto] = entrada

        botones = tk.Frame(marco, bg="#E8F6F3")
        botones.grid(row=2, column=0, columnspan=4, pady=(10, 0))
        tk.Button(botones, text="Guardar", width=12, command=self.guardar).pack(side="left", padx=5)
        tk.Button(botones, text="Actualizar", width=12, command=self.actualizar).pack(side="left", padx=5)
        tk.Button(botones, text="Eliminar", width=12, command=self.eliminar).pack(side="left", padx=5)
        tk.Button(botones, text="Limpiar", width=12, command=self.limpiar).pack(side="left", padx=5)

    def crear_tabla(self):
        buscador = tk.Frame(self, bg="#E8F6F3")
        buscador.pack(fill="x", padx=10)
        tk.Label(buscador, text="Buscar por nombre o especialidad:", bg="#E8F6F3").pack(side="left")
        self.entrada_busqueda = tk.Entry(buscador, width=30)
        self.entrada_busqueda.pack(side="left", padx=5)
        self.entrada_busqueda.bind("<KeyRelease>", lambda e: self.cargar_medicos())

        columnas = ("id", "nombre", "especialidad", "consultorio", "telefono")
        self.tabla = ttk.Treeview(self, columns=columnas, show="headings", height=10)
        encabezados = ["ID", "Nombre", "Especialidad", "Consultorio", "Teléfono"]
        anchos = [40, 250, 180, 120, 120]
        for col, texto, ancho in zip(columnas, encabezados, anchos):
            self.tabla.heading(col, text=texto)
            self.tabla.column(col, width=ancho)
        self.tabla.pack(fill="both", expand=True, padx=10, pady=10)
        self.tabla.bind("<<TreeviewSelect>>", self.seleccionar)

    def cargar_medicos(self):
        texto = self.entrada_busqueda.get().strip()
        medicos = buscar_medicos(texto) if texto else listar_medicos()

        self.tabla.delete(*self.tabla.get_children())
        self.filas = {}
        for m in medicos:
            fila = ["" if valor is None else valor for valor in m]
            iid = str(fila[0])
            self.filas[iid] = fila
            self.tabla.insert("", "end", iid=iid, values=fila)

    def obtener_datos(self):
        nombre = self.campos["Nombre completo"].get().strip()
        if not nombre:
            messagebox.showwarning("Falta información", "El nombre es obligatorio.")
            return None
        return (
            nombre,
            self.campos["Especialidad"].get().strip(),
            self.campos["Consultorio"].get().strip(),
            self.campos["Teléfono"].get().strip(),
        )

    def guardar(self):
        datos = self.obtener_datos()
        if datos is None:
            return
        agregar_medico(*datos)
        self.limpiar()
        self.cargar_medicos()
        messagebox.showinfo("Listo", "Médico guardado correctamente.")

    def actualizar(self):
        if self.id_seleccionado is None:
            messagebox.showwarning("Selecciona un médico", "Elige un médico de la tabla primero.")
            return
        datos = self.obtener_datos()
        if datos is None:
            return
        actualizar_medico(self.id_seleccionado, *datos)
        self.limpiar()
        self.cargar_medicos()
        messagebox.showinfo("Listo", "Médico actualizado correctamente.")

    def eliminar(self):
        if self.id_seleccionado is None:
            messagebox.showwarning("Selecciona un médico", "Elige un médico de la tabla primero.")
            return
        if not messagebox.askyesno("Confirmar", "¿Seguro que quieres eliminar este médico?"):
            return
        if eliminar_medico(self.id_seleccionado):
            self.limpiar()
            self.cargar_medicos()
        else:
            messagebox.showerror("No se pudo eliminar", "Este médico tiene citas registradas.")

    def seleccionar(self, evento):
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        fila = self.filas[seleccion[0]]
        self.id_seleccionado = fila[0]
        nombres = ["Nombre completo", "Especialidad", "Consultorio", "Teléfono"]
        for nombre, valor in zip(nombres, fila[1:]):
            campo = self.campos[nombre]
            campo.delete(0, tk.END)
            campo.insert(0, valor)

    def limpiar(self):
        self.id_seleccionado = None
        for campo in self.campos.values():
            campo.delete(0, tk.END)
        self.tabla.selection_remove(self.tabla.selection())