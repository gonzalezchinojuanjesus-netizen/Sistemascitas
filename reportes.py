import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from database import conectar

REPORTES = {
    "Citas por médico": (
        ["Médico", "Especialidad", "Total", "Programadas", "Canceladas"],
        """SELECT m.nombre_completo, m.especialidad, COUNT(c.id),
           COALESCE(SUM(c.estado = 'Programada'), 0), COALESCE(SUM(c.estado = 'Cancelada'), 0)
           FROM medicos m LEFT JOIN citas c ON c.medico_id = m.id
           GROUP BY m.id ORDER BY COUNT(c.id) DESC""",
    ),
    "Citas por paciente": (
        ["Paciente", "Total", "Programadas", "Canceladas"],
        """SELECT p.nombre_completo, COUNT(c.id),
           COALESCE(SUM(c.estado = 'Programada'), 0), COALESCE(SUM(c.estado = 'Cancelada'), 0)
           FROM pacientes p LEFT JOIN citas c ON c.paciente_id = p.id
           GROUP BY p.id ORDER BY COUNT(c.id) DESC""",
    ),
    "Citas por estado": (
        ["Estado", "Total"],
        "SELECT estado, COUNT(*) FROM citas GROUP BY estado",
    ),
    "Listado completo de citas": (
        ["Paciente", "Médico", "Fecha", "Hora", "Motivo", "Estado"],
        """SELECT p.nombre_completo, m.nombre_completo, c.fecha, c.hora, c.motivo, c.estado
           FROM citas c JOIN pacientes p ON c.paciente_id = p.id
           JOIN medicos m ON c.medico_id = m.id ORDER BY c.fecha, c.hora""",
    ),
}


class PantallaReportes(tk.Frame):
    def __init__(self, padre):
        super().__init__(padre, bg="#E8F6F3")
        barra = tk.Frame(self, bg="#E8F6F3")
        barra.pack(fill="x", padx=10, pady=10)

        tk.Label(barra, text="Reporte:", bg="#E8F6F3").pack(side="left")
        self.combo = ttk.Combobox(barra, values=list(REPORTES), state="readonly", width=30)
        self.combo.current(0)
        self.combo.pack(side="left", padx=5)
        self.combo.bind("<<ComboboxSelected>>", lambda e: self.generar())
        tk.Button(barra, text="Actualizar", width=12, command=self.generar).pack(side="left", padx=5)
        tk.Button(barra, text="Exportar CSV", width=12, command=self.exportar).pack(side="left", padx=5)
        self.total = tk.Label(barra, bg="#E8F6F3")
        self.total.pack(side="right")

        self.tabla = ttk.Treeview(self, show="headings", height=15)
        self.tabla.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.generar()
        self.bind("<Map>", lambda e: self.generar())  # se actualiza al abrir la pestaña

    def generar(self):
        columnas, sql = REPORTES[self.combo.get()]
        conexion = conectar()
        filas = conexion.execute(sql).fetchall()
        conexion.close()

        self.tabla["columns"] = columnas
        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=120, anchor="w")
        self.tabla.delete(*self.tabla.get_children())
        for fila in filas:
            self.tabla.insert("", "end", values=["" if v is None else v for v in fila])
        self.total.config(text=f"Registros: {len(filas)}")

    def exportar(self):
        ruta = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV", "*.csv")],
            initialfile=self.combo.get().lower().replace(" ", "_"),
        )
        if not ruta:
            return
        with open(ruta, "w", newline="", encoding="utf-8-sig") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(self.tabla["columns"])
            for item in self.tabla.get_children():
                escritor.writerow(self.tabla.item(item, "values"))
        messagebox.showinfo("Listo", "Reporte exportado correctamente.")
        