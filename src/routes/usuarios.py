from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.database import get_db_connection

bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')

@bp.route('/')
def lista():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        
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
    
@bp.route('/crear', methods=['GET'])
def crear():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id_rol, nombre FROM roles")
        roles = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('usuarios/crear.html', roles=roles)
    return "Error de conexión"

@bp.route('/guardar', methods=['POST'])
def guardar():
    nombre = request.form['nombre']
    credenciales = request.form['credenciales']
    id_rol = request.form['id_rol']
    acceso = request.form['acceso']

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        sql = """
            INSERT INTO usuarios (id_usuario, nombre, credenciales, acceso, id_rol)
            VALUES (%s, %s, %s, %s, %s)
        """
        
        cursor.execute("SELECT COALESCE(MAX(id_usuario), 0) + 1 FROM usuarios")
        siguiente_id = cursor.fetchone()[0]

        values = (siguiente_id, nombre, credenciales, acceso, id_rol)
        
        try:
            cursor.execute(sql, values)
            conn.commit()
        except Exception as e:
            print(f"Error al guardar: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
        
        return redirect(url_for('usuarios.lista'))
    
    return "Error de conexión"

@bp.route('/editar/<int:id>', methods=['GET'])
def editar(id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (id,))
        usuario = cursor.fetchone()
        
        cursor.execute("SELECT id_rol, nombre FROM roles")
        roles = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        if usuario:
            return render_template('usuarios/editar.html', usuario=usuario, roles=roles)
        else:
            return "Usuario no encontrado"
    return "Error de conexión"

@bp.route('/actualizar', methods=['POST'])
def actualizar():
    id_usuario = request.form['id_usuario']
    nombre = request.form['nombre']
    id_rol = request.form['id_rol']
    acceso = request.form['acceso']
    

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

@bp.route('/eliminar/<int:id>')
def eliminar(id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM usuarios WHERE id_usuario = %s", (id,))
            conn.commit()
        except Exception as e:
            print(f"No se puede eliminar: {e}")
        finally:
            cursor.close()
            conn.close()
        
        return redirect(url_for('usuarios.lista'))