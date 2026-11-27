import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from database import conectar
def agregar_paciente(nombre_completo, edad, sexo, telefono, correo_electronico, direccion):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        """
        INSERT INTO pacientes (nombre_completo, edad, sexo, telefono, correo_electronico, direccion)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (nombre_completo, edad, sexo, telefono, correo_electronico, direccion),
    )
    conexion.commit()
    conexion.close()


def listar_pacientes():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM pacientes ORDER BY nombre_completo")
    pacientes = cursor.fetchall()
    conexion.close()
    return pacientes


def buscar_pacientes(texto):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT * FROM pacientes WHERE nombre_completo LIKE ? ORDER BY nombre_completo",
        (f"%{texto}%",),
    )
    pacientes = cursor.fetchall()
    conexion.close()
    return pacientes


def actualizar_paciente(id_paciente, nombre_completo, edad, sexo, telefono, correo_electronico, direccion):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        """
        UPDATE pacientes
        SET nombre_completo = ?, edad = ?, sexo = ?, telefono = ?,
            correo_electronico = ?, direccion = ?
        WHERE id = ?
        """,
        (nombre_completo, edad, sexo, telefono, correo_electronico, direccion, id_paciente),
    )
    conexion.commit()
    conexion.close()


def eliminar_paciente(id_paciente):
    """Devuelve True si se eliminó, False si el paciente tiene citas registradas."""
    conexion = conectar()
    cursor = conexion.cursor()
    try:
        cursor.execute("DELETE FROM pacientes WHERE id = ?", (id_paciente,))
        conexion.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conexion.close()
class PantallaPacientes(tk.Frame):
    def __init__(self, padre):
        super().__init__(padre, bg="#E8F6F3")
        self.id_seleccionado = None
        self.filas = {}
        self.crear_formulario()
        self.crear_tabla()
        self.cargar_pacientes()

    def crear_formulario(self):
        marco = tk.LabelFrame(self, text="Datos del paciente", bg="#E8F6F3", padx=10, pady=10)
        marco.pack(fill="x", padx=10, pady=10)

        etiquetas = ["Nombre completo", "Edad", "Sexo", "Teléfono", "Correo electrónico", "Dirección"]
        self.campos = {}
        for i, texto in enumerate(etiquetas):
            fila, col = i // 2, (i % 2) * 2
            tk.Label(marco, text=texto, bg="#E8F6F3").grid(row=fila, column=col, sticky="e", padx=5, pady=5)
            if texto == "Sexo":
                entrada = ttk.Combobox(marco, values=["M", "F"], state="readonly", width=27)
            else:
                entrada = tk.Entry(marco, width=30)
            entrada.grid(row=fila, column=col + 1, padx=5, pady=5)
            self.campos[texto] = entrada

        botones = tk.Frame(marco, bg="#E8F6F3")
        botones.grid(row=3, column=0, columnspan=4, pady=(10, 0))
        tk.Button(botones, text="Guardar", width=12, command=self.guardar).pack(side="left", padx=5)
        tk.Button(botones, text="Actualizar", width=12, command=self.actualizar).pack(side="left", padx=5)
        tk.Button(botones, text="Eliminar", width=12, command=self.eliminar).pack(side="left", padx=5)
        tk.Button(botones, text="Limpiar", width=12, command=self.limpiar).pack(side="left", padx=5)

    def crear_tabla(self):
        buscador = tk.Frame(self, bg="#E8F6F3")
        buscador.pack(fill="x", padx=10)
        tk.Label(buscador, text="Buscar por nombre:", bg="#E8F6F3").pack(side="left")
        self.entrada_busqueda = tk.Entry(buscador, width=30)
        self.entrada_busqueda.pack(side="left", padx=5)
        self.entrada_busqueda.bind("<KeyRelease>", lambda e: self.cargar_pacientes())

        columnas = ("id", "nombre", "edad", "sexo", "telefono", "correo", "direccion")
        self.tabla = ttk.Treeview(self, columns=columnas, show="headings", height=10)
        encabezados = ["ID", "Nombre", "Edad", "Sexo", "Teléfono", "Correo", "Dirección"]
        anchos = [40, 200, 50, 50, 110, 170, 200]
        for col, texto, ancho in zip(columnas, encabezados, anchos):
            self.tabla.heading(col, text=texto)
            self.tabla.column(col, width=ancho)
        self.tabla.pack(fill="both", expand=True, padx=10, pady=10)
        self.tabla.bind("<<TreeviewSelect>>", self.seleccionar)

    def cargar_pacientes(self):
        texto = self.entrada_busqueda.get().strip()
        pacientes = buscar_pacientes(texto) if texto else listar_pacientes()

        self.tabla.delete(*self.tabla.get_children())
        self.filas = {}
        for p in pacientes:
            fila = ["" if valor is None else valor for valor in p]
            iid = str(fila[0])
            self.filas[iid] = fila
            self.tabla.insert("", "end", iid=iid, values=fila)

    def obtener_datos(self):
        nombre = self.campos["Nombre completo"].get().strip()
        if not nombre:
            messagebox.showwarning("Falta información", "El nombre es obligatorio.")
            return None

        edad_texto = self.campos["Edad"].get().strip()
        if edad_texto and not edad_texto.isdigit():
            messagebox.showwarning("Dato inválido", "La edad debe ser un número.")
            return None
        edad = int(edad_texto) if edad_texto else None

        return (
            nombre,
            edad,
            self.campos["Sexo"].get(),
            self.campos["Teléfono"].get().strip(),
            self.campos["Correo electrónico"].get().strip(),
            self.campos["Dirección"].get().strip(),
        )

    def guardar(self):
        datos = self.obtener_datos()
        if datos is None:
            return
        agregar_paciente(*datos)
        self.limpiar()
        self.cargar_pacientes()
        messagebox.showinfo("Listo", "Paciente guardado correctamente.")

    def actualizar(self):
        if self.id_seleccionado is None:
            messagebox.showwarning("Selecciona un paciente", "Elige un paciente de la tabla primero.")
            return
        datos = self.obtener_datos()
        if datos is None:
            return
        actualizar_paciente(self.id_seleccionado, *datos)
        self.limpiar()
        self.cargar_pacientes()
        messagebox.showinfo("Listo", "Paciente actualizado correctamente.")

    def eliminar(self):
        if self.id_seleccionado is None:
            messagebox.showwarning("Selecciona un paciente", "Elige un paciente de la tabla primero.")
            return
        if not messagebox.askyesno("Confirmar", "¿Seguro que quieres eliminar este paciente?"):
            return
        if eliminar_paciente(self.id_seleccionado):
            self.limpiar()
            self.cargar_pacientes()
        else:
            messagebox.showerror("No se pudo eliminar", "Este paciente tiene citas registradas.")

    def seleccionar(self, evento):
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        fila = self.filas[seleccion[0]]
        self.id_seleccionado = fila[0]
        nombres = ["Nombre completo", "Edad", "Sexo", "Teléfono", "Correo electrónico", "Dirección"]
        for nombre, valor in zip(nombres, fila[1:]):
            campo = self.campos[nombre]
            if isinstance(campo, ttk.Combobox):
                campo.set(valor)
            else:
                campo.delete(0, tk.END)
                campo.insert(0, valor)

    def limpiar(self):
        self.id_seleccionado = None
        for nombre, campo in self.campos.items():
            if isinstance(campo, ttk.Combobox):
                campo.set("")
            else:
                campo.delete(0, tk.END)
        self.tabla.selection_remove(self.tabla.selection())