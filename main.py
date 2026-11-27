import tkinter as tk
from tkinter import ttk
from database import crear_tablas
from pacientes import PantallaPacientes
from medicos import PantallaMedicos


def main():
    crear_tablas()

    ventana = tk.Tk()
    ventana.title("Sistema de Citas Médicas")
    ventana.geometry("900x600")
    ventana.configure(bg="#E8F6F3")

    pestanas = ttk.Notebook(ventana)
    pestanas.pack(fill="both", expand=True)
    pestanas.add(PantallaPacientes(pestanas), text="Pacientes")
    pestanas.add(PantallaMedicos(pestanas), text="Médicos")

    ventana.mainloop()


if __name__ == "__main__":
    main()