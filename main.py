import tkinter as tk
from database import crear_tablas

def main():
    crear_tablas()
    print("Base de datos creada correctamente.")

ventana = tk.Tk()
ventana.title("Sistema de Citas Médicas")
ventana.geometry("900x600")
ventana.configure(bg="#E8F6F3")
ventana.mainloop()

if __name__ == "__main__":
    main()