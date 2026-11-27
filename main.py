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
    estilo = ttk.Style()
    estilo.theme_use("clam")
    estilo.configure("TNotebook", background="#E8F6F3")
    estilo.configure("TNotebook.Tab", background="#E8F6F3", foreground="black")
    estilo.configure("TCombobox", fieldbackground="white", foreground="black")
    estilo.map("TCombobox", fieldbackground=[("readonly", "white")], foreground=[("readonly", "black")])
    estilo.configure("Treeview", background="white", fieldbackground="white", foreground="black")
    estilo.configure("Treeview.Heading", background="#E8F6F3", foreground="black")
    estilo.map("Treeview", background=[("selected", "#cde9fd")], foreground=[("selected", "black")])
    pestanas = ttk.Notebook(ventana)
    pestanas.pack(fill="both", expand=False)
    pestanas.add(PantallaPacientes(pestanas), text="Pacientes")
    pestanas.add(PantallaMedicos(pestanas), text="Médicos")
    ventana.mainloop()

if __name__ == "__main__":
    main()