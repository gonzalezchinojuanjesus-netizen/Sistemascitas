import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import conectar
from pacientes import listar_pacientes
from medicos import listar_medicos


def ejecutar(sql, datos=(), leer=False):
    conexion = conectar()
    resultado = conexion.execute(sql, datos).fetchall() if leer else conexion.execute(sql, datos) and None
    conexion.commit()
    conexion.close()
    return resultado


def agendar_cita(paciente_id, medico_id, fecha, hora, motivo, salud=""):
    """Devuelve False si el médico ya tiene una cita programada a esa fecha y hora."""
    if ejecutar("SELECT 1 FROM citas WHERE medico_id=? AND fecha=? AND hora=? AND estado='Programada'",
                (medico_id, fecha, hora), leer=True):
        return False
    ejecutar("INSERT INTO citas (paciente_id, medico_id, fecha, hora, motivo, estado_de_salud) "
             "VALUES (?, ?, ?, ?, ?, ?)", (paciente_id, medico_id, fecha, hora, motivo, salud))
    return True


def listar_citas():
    return ejecutar("""SELECT c.id, p.nombre_completo, m.nombre_completo, m.especialidad,
                       c.fecha, c.hora, c.motivo, c.estado
                       FROM citas c JOIN pacientes p ON c.paciente_id = p.id
                       JOIN medicos m ON c.medico_id = m.id ORDER BY c.fecha, c.hora""", leer=True)


def cancelar_cita(cita_id):
    ejecutar("UPDATE citas SET estado = 'Cancelada' WHERE id = ?", (cita_id,))


class PantallaCitas(tk.Frame):
    def __init__(self, padre):
        super().__init__(padre, bg="#E8F6F3")
        marco = tk.LabelFrame(self, text="Agendar cita", bg="#E8F6F3", padx=10, pady=10)
        marco.pack(fill="x", padx=10, pady=10)

        self.campos = {}
        datos = [("Paciente", "Paciente", True), ("Médico", "Médico", True),
                 ("Fecha", "Fecha (AAAA-MM-DD)", False), ("Hora", "Hora (HH:MM)", False),
                 ("Motivo", "Motivo", False), ("Salud", "Estado de salud", False)]
        for i, (clave, etiqueta, es_combo) in enumerate(datos):
            fila, col = i // 2, (i % 2) * 2
            tk.Label(marco, text=etiqueta, bg="#E8F6F3").grid(row=fila, column=col, sticky="e", padx=5, pady=5)
            campo = ttk.Combobox(marco, state="readonly", width=32) if es_combo else tk.Entry(marco, width=34)
            campo.grid(row=fila, column=col + 1, padx=5, pady=5)
            self.campos[clave] = campo

        botones = tk.Frame(marco, bg="#E8F6F3")
        botones.grid(row=3, column=0, columnspan=4, pady=(10, 0))
        for texto, comando in [("Agendar", self.agendar), ("Cancelar cita", self.cancelar), ("Limpiar", self.limpiar)]:
            tk.Button(botones, text=texto, width=14, command=comando).pack(side="left", padx=5)

        buscador = tk.Frame(self, bg="#E8F6F3")
        buscador.pack(fill="x", padx=10)
        tk.Label(buscador, text="Buscar por paciente o médico:", bg="#E8F6F3").pack(side="left")
        self.busqueda = tk.Entry(buscador, width=30)
        self.busqueda.pack(side="left", padx=5)
        self.busqueda.bind("<KeyRelease>", lambda e: self.cargar_citas())

        columnas = [("ID", 40), ("Paciente", 150), ("Médico", 150), ("Especialidad", 110),
                    ("Fecha", 90), ("Hora", 60), ("Motivo", 140), ("Estado", 90)]
        self.tabla = ttk.Treeview(self, columns=[c[0] for c in columnas], show="headings", height=10)
        for nombre, ancho in columnas:
            self.tabla.heading(nombre, text=nombre)
            self.tabla.column(nombre, width=ancho)
        self.tabla.tag_configure("cancelada", foreground="gray")
        self.tabla.pack(fill="both", expand=True, padx=10, pady=10)

        self.cargar_listas()
        self.cargar_citas()
        self.bind("<Map>", lambda e: self.cargar_listas())  # actualiza los menús al abrir la pestaña

    def cargar_listas(self):
        self.pacientes = {f"{p[0]} - {p[1]}": p[0] for p in listar_pacientes()}
        self.medicos = {f"{m[0]} - {m[1]} ({m[2]})": m[0] for m in listar_medicos()}
        self.campos["Paciente"]["values"] = list(self.pacientes)
        self.campos["Médico"]["values"] = list(self.medicos)

    def cargar_citas(self):
        texto = self.busqueda.get().strip().lower()
        self.tabla.delete(*self.tabla.get_children())
        for c in listar_citas():
            if texto in f"{c[1]} {c[2]}".lower():
                self.tabla.insert("", "end", iid=str(c[0]), values=c,
                                  tags=("cancelada",) if c[7] == "Cancelada" else ())

    def agendar(self):
        d = {clave: campo.get().strip() for clave, campo in self.campos.items()}
        if not (d["Paciente"] and d["Médico"] and d["Motivo"]):
            return messagebox.showwarning("Falta información", "Paciente, médico y motivo son obligatorios.")
        try:
            fecha = datetime.strptime(d["Fecha"], "%Y-%m-%d").strftime("%Y-%m-%d")
            hora = datetime.strptime(d["Hora"], "%H:%M").strftime("%H:%M")
        except ValueError:
            return messagebox.showwarning("Dato inválido", "Fecha: AAAA-MM-DD (ej. 2026-12-05). Hora: HH:MM (ej. 10:30).")
        if not agendar_cita(self.pacientes[d["Paciente"]], self.medicos[d["Médico"]], fecha, hora, d["Motivo"], d["Salud"]):
            return messagebox.showerror("Horario ocupado", "Ese médico ya tiene una cita a esa fecha y hora.")
        self.limpiar()
        self.cargar_citas()
        messagebox.showinfo("Listo", "Cita agendada correctamente.")

    def cancelar(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            return messagebox.showwarning("Selecciona una cita", "Elige una cita de la tabla primero.")
        if self.tabla.item(seleccion[0], "values")[7] == "Cancelada":
            return messagebox.showinfo("Aviso", "Esa cita ya está cancelada.")
        if messagebox.askyesno("Confirmar", "¿Seguro que quieres cancelar esta cita?"):
            cancelar_cita(int(seleccion[0]))
            self.cargar_citas()

    def limpiar(self):
        for campo in self.campos.values():
            campo.set("") if isinstance(campo, ttk.Combobox) else campo.delete(0, tk.END)