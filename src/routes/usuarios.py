from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.database import get_db_connection

# Creamos el grupo de rutas para "usuarios"
bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')

@bp.route('/')
def lista():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True) # dictionary=True permite llamar columnas por nombre
        
        # Hacemos un JOIN para mostrar el nombre del rol en vez del número
        sql = """
            SELECT u.id_usuario, u.nombre, u.acceso, r.nombre as nombre_rol
            FROM usuarios u
            JOIN roles r ON u.id_rol = r.id_rol
            ORDER BY u.id_usuario
        """
        cursor.execute(sql)
        usuarios = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return render_template('usuarios/lista.html', usuarios=usuarios)
    else:
        return "Error de conexión a la BD"
    
# --- NUEVA RUTA: Mostrar formulario de creación ---
@bp.route('/crear', methods=['GET'])
def crear():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        # Necesitamos los roles para el dropdown del formulario
        cursor.execute("SELECT id_rol, nombre FROM roles")
        roles = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('usuarios/crear.html', roles=roles)
    return "Error de conexión"

# --- NUEVA RUTA: Procesar el formulario (Guardar) ---
@bp.route('/guardar', methods=['POST'])
def guardar():
    # 1. Recibir datos del formulario HTML
    nombre = request.form['nombre']
    credenciales = request.form['credenciales'] # En un caso real, esto se encriptaría
    id_rol = request.form['id_rol']
    acceso = request.form['acceso']

    # 2. Conectar e Insertar
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        sql = """
            INSERT INTO usuarios (id_usuario, nombre, credenciales, acceso, id_rol)
            VALUES (%s, %s, %s, %s, %s)
        """
        # Para el ID, usaremos un truco simple: MAX(id) + 1 (o dejar que sea AUTO_INCREMENT si modificamos la tabla,
        # pero para seguir tu script original donde el ID es manual, calculémoslo o usémoslo al azar).
        # MEJOR OPCIÓN: Modificaremos la logica para calcular el siguiente ID disponible manualmente
        # ya que tu script NO tiene AUTO_INCREMENT definido explícitamente en el CREATE TABLE.
        
        # Paso extra: Obtener el siguiente ID
        cursor.execute("SELECT COALESCE(MAX(id_usuario), 0) + 1 FROM usuarios")
        siguiente_id = cursor.fetchone()[0]

        values = (siguiente_id, nombre, credenciales, acceso, id_rol)
        
        try:
            cursor.execute(sql, values)
            conn.commit() # ¡IMPORTANTE! Guardar cambios
            # flash("Usuario creado correctamente") # Opcional: mensajes flash
        except Exception as e:
            print(f"Error al guardar: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
        
        return redirect(url_for('usuarios.lista'))
    
    return "Error de conexión"

# --- RUTA: Mostrar formulario de EDICIÓN ---
@bp.route('/editar/<int:id>', methods=['GET'])
def editar(id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        # 1. Obtener los datos del usuario específico
        cursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (id,))
        usuario = cursor.fetchone()
        
        # 2. Obtener los roles (para llenar el select)
        cursor.execute("SELECT id_rol, nombre FROM roles")
        roles = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        if usuario:
            return render_template('usuarios/editar.html', usuario=usuario, roles=roles)
        else:
            return "Usuario no encontrado"
    return "Error de conexión"

# --- RUTA: Procesar la ACTUALIZACIÓN ---
@bp.route('/actualizar', methods=['POST'])
def actualizar():
    # Recibir datos del formulario (incluyendo el ID oculto)
    id_usuario = request.form['id_usuario']
    nombre = request.form['nombre']
    id_rol = request.form['id_rol']
    acceso = request.form['acceso']
    
    # Nota: No actualizamos la contraseña aquí para no complicar, 
    # pero podrías añadir un IF para ver si el campo vino vacío o no.

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        sql = """
            UPDATE usuarios 
            SET nombre = %s, id_rol = %s, acceso = %s
            WHERE id_usuario = %s
        """
        values = (nombre, id_rol, acceso, id_usuario)
        
        try:
            cursor.execute(sql, values)
            conn.commit()
        except Exception as e:
            print(f"Error al actualizar: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
        
        return redirect(url_for('usuarios.lista'))

# --- RUTA: ELIMINAR ---
@bp.route('/eliminar/<int:id>')
def eliminar(id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        # ¡CUIDADO! Si el usuario tiene pedidos o pagos, esto fallará por las Foreign Keys.
        # Lo correcto es usar un TRY-CATCH para avisar si no se puede borrar.
        try:
            cursor.execute("DELETE FROM usuarios WHERE id_usuario = %s", (id,))
            conn.commit()
        except Exception as e:
            print(f"No se puede eliminar: {e}")
            # Aquí podrías retornar un mensaje de error a la vista
        finally:
            cursor.close()
            conn.close()
        
        return redirect(url_for('usuarios.lista'))