from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.database import get_db_connection

bp = Blueprint('clientes', __name__, url_prefix='/clientes')

@bp.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT c.id_cliente, c.telefono, c.email, c.direccion,
               pn.dni, pn.nombres, pn.apellidos,
               pj.ruc, pj.razon_social,
               CASE 
                   WHEN pn.id_cliente IS NOT NULL THEN 'Natural' 
                   ELSE 'Juridica' 
               END as tipo_cliente
        FROM clientes c
        LEFT JOIN personas_naturales pn ON c.id_cliente = pn.id_cliente
        LEFT JOIN personas_juridicas pj ON c.id_cliente = pj.id_cliente
        ORDER BY c.id_cliente ASC
    """
    cursor.execute(query)
    clientes = cursor.fetchall()
    conn.close()
    return render_template('clientes/index.html', clientes=clientes)

@bp.route('/crear', methods=['GET', 'POST'])
def crear():
    if request.method == 'POST':
        tipo = request.form['tipo_cliente'] # natural o juridica
        
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        email = request.form['email']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            conn.start_transaction()

            cursor.execute("SELECT COALESCE(MAX(id_cliente), 0) + 1 AS nuevo_id FROM clientes")
            nuevo_id = cursor.fetchone()['nuevo_id']

            cursor.execute("""
                INSERT INTO clientes (id_cliente, direccion, telefono, email) 
                VALUES (%s, %s, %s, %s)
            """, (nuevo_id, direccion, telefono, email))

            if tipo == 'natural':
                dni = request.form['dni']
                nombres = request.form['nombres']
                apellidos = request.form['apellidos']
                cursor.execute("""
                    INSERT INTO personas_naturales (id_cliente, dni, nombres, apellidos) 
                    VALUES (%s, %s, %s, %s)
                """, (nuevo_id, dni, nombres, apellidos))
            else:
                ruc = request.form['ruc']
                razon = request.form['razon_social']
                cursor.execute("""
                    INSERT INTO personas_juridicas (id_cliente, ruc, razon_social) 
                    VALUES (%s, %s, %s)
                """, (nuevo_id, ruc, razon))

            conn.commit()
            flash('Cliente registrado exitosamente.', 'success')
            return redirect(url_for('clientes.index'))

        except Exception as e:
            conn.rollback()
            print(f"Error: {e}") # Para ver en consola
            flash(f'Error al registrar: {e}', 'danger')
        finally:
            conn.close()

    return render_template('clientes/crear.html')

@bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT c.*, pn.dni, pn.nombres, pn.apellidos, pj.ruc, pj.razon_social,
        CASE WHEN pn.id_cliente IS NOT NULL THEN 'natural' ELSE 'juridica' END as tipo
        FROM clientes c
        LEFT JOIN personas_naturales pn ON c.id_cliente = pn.id_cliente
        LEFT JOIN personas_juridicas pj ON c.id_cliente = pj.id_cliente
        WHERE c.id_cliente = %s
    """, (id,))
    cliente = cursor.fetchone()

    if request.method == 'POST':
        try:
            conn.start_transaction()
            
            telefono = request.form['telefono']
            direccion = request.form['direccion']
            email = request.form['email']

            cursor.execute("""
                UPDATE clientes SET direccion=%s, telefono=%s, email=%s WHERE id_cliente=%s
            """, (direccion, telefono, email, id))

            if cliente['tipo'] == 'natural':
                dni = request.form['dni']
                nombres = request.form['nombres']
                apellidos = request.form['apellidos']
                cursor.execute("""
                    UPDATE personas_naturales SET dni=%s, nombres=%s, apellidos=%s WHERE id_cliente=%s
                """, (dni, nombres, apellidos, id))
            else:
                ruc = request.form['ruc']
                razon = request.form['razon_social']
                cursor.execute("""
                    UPDATE personas_juridicas SET ruc=%s, razon_social=%s WHERE id_cliente=%s
                """, (ruc, razon, id))

            conn.commit()
            flash('Cliente actualizado.', 'success')
            return redirect(url_for('clientes.index'))

        except Exception as e:
            conn.rollback()
            flash(f'Error al editar: {e}', 'danger')

    conn.close()
    return render_template('clientes/editar.html', cliente=cliente)

@bp.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM clientes WHERE id_cliente = %s", (id,))
        conn.commit()
        flash('Cliente eliminado.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error al eliminar: {e}', 'danger')
    finally:
        conn.close()
    return redirect(url_for('clientes.index'))