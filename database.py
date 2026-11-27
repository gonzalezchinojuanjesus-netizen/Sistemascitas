import os
import sqlite3

def conectar():
    os.makedirs("database", exist_ok=True)
    conexion = sqlite3.connect("database/clinica.db")
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion

def crear_tablas():
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pacientes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_completo TEXT NOT NULL,
        edad INTEGER,
        sexo TEXT,
        telefono TEXT,
        correo_electronico TEXT,
        direccion TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS medicos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_completo TEXT NOT NULL,
        especialidad TEXT,
        consultorio TEXT,
        telefono TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS citas(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        paciente_id INTEGER,
        medico_id INTEGER,
        fecha TEXT,
        hora TEXT,
        motivo TEXT,
        estado TEXT DEFAULT 'Programada',
        estado_de_salud TEXT,
        FOREIGN KEY(paciente_id) REFERENCES pacientes(id),
        FOREIGN KEY(medico_id) REFERENCES medicos(id)
    )
    """)

    conexion.commit()
    conexion.close()