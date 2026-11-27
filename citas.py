from database import conectar


def horario_ocupado(medico_id, fecha, hora):
    """True si el médico ya tiene una cita programada en esa fecha y hora."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        """
        SELECT 1 FROM citas
        WHERE medico_id = ? AND fecha = ? AND hora = ? AND estado = 'Programada'
        """,
        (medico_id, fecha, hora),
    )
    ocupado = cursor.fetchone() is not None
    conexion.close()
    return ocupado


def agendar_cita(paciente_id, medico_id, fecha, hora, motivo, estado_de_salud=""):
    """Devuelve True si se agendó, False si el médico ya tiene cita a esa hora."""
    if horario_ocupado(medico_id, fecha, hora):
        return False
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        """
        INSERT INTO citas (paciente_id, medico_id, fecha, hora, motivo, estado_de_salud)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (paciente_id, medico_id, fecha, hora, motivo, estado_de_salud),
    )
    conexion.commit()
    conexion.close()
    return True


def listar_citas():
    """Citas con el nombre del paciente y del médico ya incluidos."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        """
        SELECT c.id, p.nombre_completo, m.nombre_completo, m.especialidad,
               c.fecha, c.hora, c.motivo, c.estado
        FROM citas c
        JOIN pacientes p ON c.paciente_id = p.id
        JOIN medicos m ON c.medico_id = m.id
        ORDER BY c.fecha, c.hora
        """
    )
    citas = cursor.fetchall()
    conexion.close()
    return citas


def citas_de_paciente(paciente_id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        """
        SELECT c.id, m.nombre_completo, m.especialidad, c.fecha, c.hora, c.motivo, c.estado
        FROM citas c
        JOIN medicos m ON c.medico_id = m.id
        WHERE c.paciente_id = ?
        ORDER BY c.fecha, c.hora
        """,
        (paciente_id,),
    )
    citas = cursor.fetchall()
    conexion.close()
    return citas


def cancelar_cita(cita_id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("UPDATE citas SET estado = 'Cancelada' WHERE id = ?", (cita_id,))
    conexion.commit()
    conexion.close()