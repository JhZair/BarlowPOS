from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.database import get_db_connection

bp = Blueprint('mesas', __name__, url_prefix='/mesas')

@bp.route('/')
def lista():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT m.id_mesa, m.numero, m.estado, a.nombre AS nombre_ambiente
            FROM mesas m
            JOIN ambientes a ON m.id_ambiente = a.id_ambiente
            ORDER BY m.numero ASC
        """
        cursor.execute(sql)
        mesas = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('mesas/index.html', mesas=mesas)
    return "Error de conexión a BD"

@bp.route('/crear')
def crear():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id_ambiente, nombre FROM ambientes ORDER BY nombre")
        ambientes = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('mesas/crear.html', ambientes=ambientes)
    return "Error de BD"

@bp.route('/guardar', methods=['POST'])
def guardar():
    numero = request.form['numero']
    estado = request.form['estado']
    id_ambiente = request.form['id_ambiente']
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COALESCE(MAX(id_mesa), 0) + 1 FROM mesas")
        nuevo_id = cursor.fetchone()[0]
        
        sql = "INSERT INTO mesas (id_mesa, numero, estado, id_ambiente) VALUES (%s, %s, %s, %s)"
        try:
            cursor.execute(sql, (nuevo_id, numero, estado, id_ambiente))
            conn.commit()
        except Exception as e:
            print(f"Error al guardar mesa: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('mesas.lista'))
    return "Error de conexión"

@bp.route('/editar/<int:id>')
def editar(id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM mesas WHERE id_mesa = %s", (id,))
        mesa = cursor.fetchone()
        
        cursor.execute("SELECT id_ambiente, nombre FROM ambientes ORDER BY nombre")
        ambientes = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        if mesa:
            return render_template('mesas/editar.html', mesa=mesa, ambientes=ambientes)
    return "Error o mesa no encontrada"

@bp.route('/actualizar', methods=['POST'])
def actualizar():
    id_mesa = request.form['id_mesa']
    numero = request.form['numero']
    estado = request.form['estado']
    id_ambiente = request.form['id_ambiente']
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        sql = """
            UPDATE mesas 
            SET numero = %s, estado = %s, id_ambiente = %s
            WHERE id_mesa = %s
        """
        try:
            cursor.execute(sql, (numero, estado, id_ambiente, id_mesa))
            conn.commit()
        except Exception as e:
            print(f"Error al actualizar: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('mesas.lista'))
    return "Error de conexión"

@bp.route('/eliminar/<int:id>')
def eliminar(id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM mesas WHERE id_mesa = %s", (id,))
            conn.commit()
        except Exception as e:
            print(f"No se puede eliminar (probablemente tiene pedidos): {e}")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('mesas.lista'))
    return "Error de conexión"