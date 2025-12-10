from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.database import get_db_connection

bp = Blueprint('ambientes', __name__, url_prefix='/ambientes')

@bp.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM ambientes ORDER BY id_ambiente ASC")
    ambientes = cursor.fetchall()
    conn.close()
    return render_template('ambientes/index.html', ambientes=ambientes)

@bp.route('/crear', methods=['GET', 'POST'])
def crear():
    if request.method == 'POST':
        id_ambiente = request.form['id_ambiente']
        nombre = request.form['nombre']

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO ambientes (id_ambiente, nombre) VALUES (%s, %s)", (id_ambiente, nombre))
            conn.commit()
            flash('Ambiente creado exitosamente.', 'success')
            return redirect(url_for('ambientes.index'))
        except Exception as e:
            conn.rollback()
            flash(f'Error: Es probable que el ID {id_ambiente} ya exista. ({e})', 'danger')
        finally:
            conn.close()

    return render_template('ambientes/crear.html')

@bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        nuevo_nombre = request.form['nombre']
        try:
            cursor.execute("UPDATE ambientes SET nombre = %s WHERE id_ambiente = %s", (nuevo_nombre, id))
            conn.commit()
            flash('Ambiente actualizado correctamente.', 'success')
            return redirect(url_for('ambientes.index'))
        except Exception as e:
            conn.rollback()
            flash(f'Error al editar: {e}', 'danger')
        finally:
            conn.close()
    
    cursor.execute("SELECT * FROM ambientes WHERE id_ambiente = %s", (id,))
    ambiente = cursor.fetchone()
    conn.close()
    return render_template('ambientes/editar.html', ambiente=ambiente)

@bp.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM ambientes WHERE id_ambiente = %s", (id,))
        conn.commit()
        flash('Ambiente eliminado.', 'success')
    except Exception as e:
        conn.rollback()
        flash('No se puede eliminar este ambiente porque tiene Mesas asignadas.', 'danger')
    finally:
        conn.close()
        
    return redirect(url_for('ambientes.index'))