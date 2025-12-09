from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.database import get_db_connection

bp = Blueprint('clientes', __name__, url_prefix='/clientes')

# 1. READ (Leer datos unidos de las 2 entidades)
@bp.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # JOIN para traer datos de 'clientes' y 'personas_naturales'
    query = """
        SELECT c.id_cliente, pn.dni, pn.nombres, pn.apellidos, 
               c.telefono, c.email, c.direccion
        FROM clientes c
        JOIN personas_naturales pn ON c.id_cliente = pn.id_cliente
        ORDER BY c.id_cliente ASC
    """
    cursor.execute(query)
    clientes = cursor.fetchall()
    conn.close()
    return render_template('clientes/index.html', clientes=clientes)

# 2. CREATE (Insertar en las 2 entidades)
@bp.route('/crear', methods=['GET', 'POST'])
def crear():
    if request.method == 'POST':
        # Datos para Entidad 1 (Clientes)
        # Generamos ID manual (simulación auto-increment si no lo tienes en DB)
        # Ojo: En tu script SQL id_cliente NO es auto_increment, así que calculamos el siguiente.
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            conn.start_transaction()

            # Calcular nuevo ID
            cursor.execute("SELECT COALESCE(MAX(id_cliente), 0) + 1 AS nuevo_id FROM clientes")
            row = cursor.fetchone()
            nuevo_id = row['nuevo_id']

            # Datos Formulario
            dni = request.form['dni']
            nombres = request.form['nombres']
            apellidos = request.form['apellidos']
            telefono = request.form['telefono']
            direccion = request.form['direccion']
            email = request.form['email']

            # INSERT ENTIDAD 1: Clientes
            cursor.execute("""
                INSERT INTO clientes (id_cliente, direccion, telefono, email) 
                VALUES (%s, %s, %s, %s)
            """, (nuevo_id, direccion, telefono, email))

            # INSERT ENTIDAD 2: Personas Naturales
            cursor.execute("""
                INSERT INTO personas_naturales (id_cliente, dni, nombres, apellidos) 
                VALUES (%s, %s, %s, %s)
            """, (nuevo_id, dni, nombres, apellidos))

            conn.commit()
            flash('Cliente registrado exitosamente.', 'success')
            return redirect(url_for('clientes.index'))

        except Exception as e:
            conn.rollback()
            flash(f'Error al registrar: {e}', 'danger')
        finally:
            conn.close()

    return render_template('clientes/crear.html')

# 3. UPDATE (Actualizar las 2 entidades)
@bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        try:
            conn.start_transaction()
            
            # Datos Formulario
            dni = request.form['dni']
            nombres = request.form['nombres']
            apellidos = request.form['apellidos']
            telefono = request.form['telefono']
            direccion = request.form['direccion']
            email = request.form['email']

            # UPDATE ENTIDAD 1: Clientes
            cursor.execute("""
                UPDATE clientes 
                SET direccion=%s, telefono=%s, email=%s 
                WHERE id_cliente=%s
            """, (direccion, telefono, email, id))

            # UPDATE ENTIDAD 2: Personas Naturales
            cursor.execute("""
                UPDATE personas_naturales 
                SET dni=%s, nombres=%s, apellidos=%s 
                WHERE id_cliente=%s
            """, (dni, nombres, apellidos, id))

            conn.commit()
            flash('Cliente actualizado correctamente.', 'success')
            return redirect(url_for('clientes.index'))

        except Exception as e:
            conn.rollback()
            flash(f'Error al editar: {e}', 'danger')

    # GET: Cargar datos actuales
    cursor.execute("""
        SELECT c.*, pn.dni, pn.nombres, pn.apellidos
        FROM clientes c
        JOIN personas_naturales pn ON c.id_cliente = pn.id_cliente
        WHERE c.id_cliente = %s
    """, (id,))
    cliente = cursor.fetchone()
    conn.close()

    return render_template('clientes/editar.html', cliente=cliente)

# 4. DELETE (Borrar padre borra hijo por Cascada)
@bp.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Al borrar el cliente, el "ON DELETE CASCADE" de tu SQL
        # borrará automáticamente el registro en personas_naturales.
        cursor.execute("DELETE FROM clientes WHERE id_cliente = %s", (id,))
        conn.commit()
        flash('Cliente eliminado.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error al eliminar: {e}', 'danger')
    finally:
        conn.close()
    return redirect(url_for('clientes.index'))