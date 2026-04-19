"""
Sistema de Reservas para Espacios de Trabajo
TechNova Solutions - Dominio 1
"""

import os
import time
import threading
import mysql.connector
from flask import Flask, request, jsonify, render_template_string
from datetime import date

app = Flask(__name__)

# ─────────────────────────────────────────────
# Configuración de conexión a la base de datos
# Las credenciales vienen de variables de entorno (nunca hardcodeadas)
# ─────────────────────────────────────────────
def get_db():
    """Crea y retorna una conexión a MySQL usando variables de entorno."""
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        database=os.environ.get("DB_NAME", "technova_reservas"),
        port=int(os.environ.get("DB_PORT", 3306))
    )


# ─────────────────────────────────────────────
# Tarea pesada: simula el envío de correo de confirmación
# Se ejecuta en un hilo separado para no bloquear la respuesta
# ─────────────────────────────────────────────
def enviar_confirmacion(reserva_id, email_usuario):
    """
    Simula el proceso costoso de enviar un correo de confirmación.
    time.sleep(6) representa el tiempo que tomaría un servicio externo de email.
    """
    print(f"[TAREA PESADA] Iniciando envío de confirmación para reserva #{reserva_id}...")
    time.sleep(6)  # Simula proceso costoso (mínimo 5 segundos requerido)
    print(f"[TAREA PESADA] Correo de confirmación enviado a {email_usuario} para reserva #{reserva_id}")


# ─────────────────────────────────────────────
# Plantilla HTML principal — interfaz mínima funcional
# ─────────────────────────────────────────────
HTML_BASE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>TechNova - Reservas</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 900px; margin: 40px auto; padding: 0 20px; }
        h1 { color: #2c3e50; }
        h2 { color: #34495e; border-bottom: 1px solid #ccc; padding-bottom: 5px; }
        form { background: #f4f4f4; padding: 15px; border-radius: 6px; margin-bottom: 20px; }
        input, select { margin: 5px 0; padding: 6px; width: 100%; box-sizing: border-box; }
        button { background: #2980b9; color: white; padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #1a6fa0; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background: #2c3e50; color: white; }
        tr:nth-child(even) { background: #f9f9f9; }
        .nav a { margin-right: 15px; color: #2980b9; text-decoration: none; font-weight: bold; }
        .msg { padding: 10px; border-radius: 4px; margin: 10px 0; }
        .ok  { background: #d4edda; color: #155724; }
        .err { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <h1>TechNova Solutions — Sistema de Reservas</h1>
    <div class="nav">
        <a href="/">Inicio</a>
        <a href="/salas">Ver Salas</a>
        <a href="/reservas/hoy">Reservas de Hoy</a>
        <a href="/reservar">Nueva Reserva</a>
        <a href="/cancelar">Cancelar Reserva</a>
    </div>
    <hr>
    {% if mensaje %}
        <div class="msg {{ 'ok' if exito else 'err' }}">{{ mensaje }}</div>
    {% endif %}
    {{ contenido }}
</body>
</html>
"""


def render_page(contenido, mensaje=None, exito=True):
    """Renderiza la plantilla base con el contenido dado."""
    return render_template_string(
        HTML_BASE,
        contenido=contenido,
        mensaje=mensaje,
        exito=exito
    )


# ─────────────────────────────────────────────
# RUTA 1: Página de inicio
# ─────────────────────────────────────────────
@app.route("/")
def index():
    contenido = """
    <h2>Bienvenido</h2>
    <p>Usa el menú de arriba para navegar por el sistema.</p>
    <ul>
        <li><b>Ver Salas</b> — lista todas las salas disponibles</li>
        <li><b>Reservas de Hoy</b> — consulta las reservas activas del día</li>
        <li><b>Nueva Reserva</b> — registra una reserva</li>
        <li><b>Cancelar Reserva</b> — cancela una reserva existente</li>
    </ul>
    """
    return render_page(contenido)


# ─────────────────────────────────────────────
# RUTA 2 (GET): Listar todas las salas registradas
# ─────────────────────────────────────────────
@app.route("/salas", methods=["GET"])
def listar_salas():
    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        # Consulta parametrizada — sin concatenación de strings
        cursor.execute("SELECT id, nombre, capacidad, ubicacion FROM salas ORDER BY nombre")
        salas = cursor.fetchall()

        filas = "".join(
            f"<tr><td>{s['id']}</td><td>{s['nombre']}</td><td>{s['capacidad']}</td><td>{s['ubicacion']}</td></tr>"
            for s in salas
        )
        contenido = f"""
        <h2>Salas Disponibles</h2>
        <table>
            <tr><th>ID</th><th>Nombre</th><th>Capacidad</th><th>Ubicación</th></tr>
            {filas if filas else '<tr><td colspan="4">No hay salas registradas</td></tr>'}
        </table>
        <br><a href="/sala/nueva">+ Registrar nueva sala</a>
        """
        return render_page(contenido)

    except Exception as e:
        return render_page("<h2>Salas</h2>", mensaje=f"Error al consultar salas: {str(e)}", exito=False)
    finally:
        # Cierre apropiado de conexiones
        if cursor: cursor.close()
        if conn: conn.close()


# ─────────────────────────────────────────────
# RUTA 3 (GET/POST): Registrar una nueva sala
# ─────────────────────────────────────────────
@app.route("/sala/nueva", methods=["GET", "POST"])
def nueva_sala():
    if request.method == "GET":
        contenido = """
        <h2>Registrar Nueva Sala</h2>
        <form method="POST">
            <label>Nombre:</label>
            <input type="text" name="nombre" required>
            <label>Capacidad (personas):</label>
            <input type="number" name="capacidad" min="1" required>
            <label>Ubicación:</label>
            <input type="text" name="ubicacion" required>
            <button type="submit">Registrar Sala</button>
        </form>
        """
        return render_page(contenido)

    # POST: guardar la nueva sala
    conn = None
    cursor = None
    try:
        nombre = request.form.get("nombre", "").strip()
        capacidad = request.form.get("capacidad", "").strip()
        ubicacion = request.form.get("ubicacion", "").strip()

        # Validación básica de campos
        if not nombre or not capacidad or not ubicacion:
            raise ValueError("Todos los campos son obligatorios")

        conn = get_db()
        cursor = conn.cursor()
        # Uso de parámetros en la consulta SQL (nunca concatenación)
        cursor.execute(
            "INSERT INTO salas (nombre, capacidad, ubicacion) VALUES (%s, %s, %s)",
            (nombre, int(capacidad), ubicacion)
        )
        conn.commit()
        return render_page("", mensaje=f"Sala '{nombre}' registrada exitosamente.", exito=True)

    except Exception as e:
        return render_page("", mensaje=f"Error al registrar sala: {str(e)}", exito=False)
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


# ─────────────────────────────────────────────
# RUTA 4 (GET): Consultar reservas activas del día de hoy
# ─────────────────────────────────────────────
@app.route("/reservas/hoy", methods=["GET"])
def reservas_hoy():
    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        hoy = date.today().isoformat()

        # JOIN entre las 3 tablas para mostrar datos completos
        cursor.execute("""
            SELECT r.id, u.nombre AS usuario, u.email,
                   s.nombre AS sala, s.ubicacion,
                   r.fecha, r.hora_inicio, r.hora_fin, r.estado
            FROM reservas r
            JOIN usuarios u ON r.usuario_id = u.id
            JOIN salas    s ON r.sala_id    = s.id
            WHERE r.fecha = %s AND r.estado = 'activa'
            ORDER BY r.hora_inicio
        """, (hoy,))
        reservas = cursor.fetchall()

        filas = "".join(
            f"<tr><td>{r['id']}</td><td>{r['usuario']}</td><td>{r['sala']}</td>"
            f"<td>{r['ubicacion']}</td><td>{r['hora_inicio']}</td><td>{r['hora_fin']}</td></tr>"
            for r in reservas
        )
        contenido = f"""
        <h2>Reservas Activas — Hoy ({hoy})</h2>
        <table>
            <tr><th>ID</th><th>Usuario</th><th>Sala</th><th>Ubicación</th><th>Inicio</th><th>Fin</th></tr>
            {filas if filas else '<tr><td colspan="6">No hay reservas activas hoy</td></tr>'}
        </table>
        """
        return render_page(contenido)

    except Exception as e:
        return render_page("<h2>Reservas de Hoy</h2>", mensaje=f"Error al consultar reservas: {str(e)}", exito=False)
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


# ─────────────────────────────────────────────
# RUTA 5 (GET/POST): Hacer una nueva reserva
# Al confirmar, lanza la tarea pesada en un hilo separado
# ─────────────────────────────────────────────
@app.route("/reservar", methods=["GET", "POST"])
def hacer_reserva():
    if request.method == "GET":
        conn = None
        cursor = None
        try:
            conn = get_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, nombre FROM usuarios ORDER BY nombre")
            usuarios = cursor.fetchall()
            cursor.execute("SELECT id, nombre, capacidad FROM salas ORDER BY nombre")
            salas = cursor.fetchall()

            opts_usuarios = "".join(f'<option value="{u["id"]}">{u["nombre"]}</option>' for u in usuarios)
            opts_salas    = "".join(f'<option value="{s["id"]}">{s["nombre"]} (cap. {s["capacidad"]})</option>' for s in salas)

            contenido = f"""
            <h2>Nueva Reserva</h2>
            <form method="POST">
                <label>Usuario:</label>
                <select name="usuario_id" required>{opts_usuarios}</select>
                <label>Sala:</label>
                <select name="sala_id" required>{opts_salas}</select>
                <label>Fecha:</label>
                <input type="date" name="fecha" required>
                <label>Hora inicio:</label>
                <input type="time" name="hora_inicio" required>
                <label>Hora fin:</label>
                <input type="time" name="hora_fin" required>
                <button type="submit">Confirmar Reserva</button>
            </form>
            """
            return render_page(contenido)

        except Exception as e:
            return render_page("", mensaje=f"Error al cargar formulario: {str(e)}", exito=False)
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    # POST: guardar la reserva y lanzar tarea pesada
    conn = None
    cursor = None
    try:
        usuario_id  = request.form.get("usuario_id")
        sala_id     = request.form.get("sala_id")
        fecha       = request.form.get("fecha")
        hora_inicio = request.form.get("hora_inicio")
        hora_fin    = request.form.get("hora_fin")

        if not all([usuario_id, sala_id, fecha, hora_inicio, hora_fin]):
            raise ValueError("Todos los campos son obligatorios")

        if hora_inicio >= hora_fin:
            raise ValueError("La hora de inicio debe ser anterior a la hora de fin")

        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        # Verificar que no exista conflicto de horario en la misma sala
        cursor.execute("""
            SELECT id FROM reservas
            WHERE sala_id = %s AND fecha = %s AND estado = 'activa'
              AND NOT (hora_fin <= %s OR hora_inicio >= %s)
        """, (sala_id, fecha, hora_inicio, hora_fin))

        if cursor.fetchone():
            raise ValueError("La sala ya está reservada en ese horario")

        # Insertar la reserva con parámetros (sin concatenación)
        cursor.execute("""
            INSERT INTO reservas (usuario_id, sala_id, fecha, hora_inicio, hora_fin)
            VALUES (%s, %s, %s, %s, %s)
        """, (usuario_id, sala_id, fecha, hora_inicio, hora_fin))
        conn.commit()
        reserva_id = cursor.lastrowid

        # Obtener email del usuario para la confirmación
        cursor.execute("SELECT email FROM usuarios WHERE id = %s", (usuario_id,))
        usuario = cursor.fetchone()
        email = usuario["email"] if usuario else "desconocido"

        # Lanzar tarea pesada en hilo separado (no bloquea la respuesta HTTP)
        hilo = threading.Thread(target=enviar_confirmacion, args=(reserva_id, email))
        hilo.daemon = True
        hilo.start()

        return render_page("", mensaje=f"Reserva #{reserva_id} creada exitosamente. Confirmación en proceso (revisa los logs del contenedor).", exito=True)

    except Exception as e:
        return render_page("", mensaje=f"Error al crear reserva: {str(e)}", exito=False)
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


# ─────────────────────────────────────────────
# RUTA 6 (GET/POST): Cancelar una reserva existente
# ─────────────────────────────────────────────
@app.route("/cancelar", methods=["GET", "POST"])
def cancelar_reserva():
    if request.method == "GET":
        conn = None
        cursor = None
        try:
            conn = get_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT r.id, u.nombre AS usuario, s.nombre AS sala, r.fecha, r.hora_inicio
                FROM reservas r
                JOIN usuarios u ON r.usuario_id = u.id
                JOIN salas    s ON r.sala_id    = s.id
                WHERE r.estado = 'activa'
                ORDER BY r.fecha, r.hora_inicio
            """)
            reservas = cursor.fetchall()

            opts = "".join(
                f'<option value="{r["id"]}">#{r["id"]} — {r["usuario"]} | {r["sala"]} | {r["fecha"]} {r["hora_inicio"]}</option>'
                for r in reservas
            )
            contenido = f"""
            <h2>Cancelar Reserva</h2>
            <form method="POST">
                <label>Selecciona la reserva a cancelar:</label>
                <select name="reserva_id" required>
                    {'<option value="">-- Sin reservas activas --</option>' if not reservas else opts}
                </select>
                <button type="submit" {'disabled' if not reservas else ''}>Cancelar Reserva</button>
            </form>
            """
            return render_page(contenido)

        except Exception as e:
            return render_page("", mensaje=f"Error al cargar reservas: {str(e)}", exito=False)
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    # POST: marcar la reserva como cancelada
    conn = None
    cursor = None
    try:
        reserva_id = request.form.get("reserva_id")
        if not reserva_id:
            raise ValueError("Debes seleccionar una reserva")

        conn = get_db()
        cursor = conn.cursor()
        # Actualización parametrizada
        cursor.execute(
            "UPDATE reservas SET estado = 'cancelada' WHERE id = %s AND estado = 'activa'",
            (reserva_id,)
        )
        conn.commit()

        if cursor.rowcount == 0:
            raise ValueError("La reserva no existe o ya fue cancelada")

        return render_page("", mensaje=f"Reserva #{reserva_id} cancelada exitosamente.", exito=True)

    except Exception as e:
        return render_page("", mensaje=f"Error al cancelar reserva: {str(e)}", exito=False)
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


# ─────────────────────────────────────────────
# RUTA 7 (GET): API JSON — todas las reservas (para evidencia de consulta)
# ─────────────────────────────────────────────
@app.route("/api/reservas", methods=["GET"])
def api_reservas():
    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT r.id, u.nombre AS usuario, u.email,
                   s.nombre AS sala, s.ubicacion, s.capacidad,
                   r.fecha, CAST(r.hora_inicio AS CHAR) AS hora_inicio,
                   CAST(r.hora_fin AS CHAR) AS hora_fin, r.estado
            FROM reservas r
            JOIN usuarios u ON r.usuario_id = u.id
            JOIN salas    s ON r.sala_id    = s.id
            ORDER BY r.fecha DESC, r.hora_inicio
        """)
        reservas = cursor.fetchall()
        # Convertir fecha a string para que sea serializable en JSON
        for r in reservas:
            r["fecha"] = str(r["fecha"])
        return jsonify({"total": len(reservas), "reservas": reservas})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


# ─────────────────────────────────────────────
# Punto de entrada
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
