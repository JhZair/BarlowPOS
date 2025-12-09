from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.database import get_db_connection

bp = Blueprint('pedidos', __name__, url_prefix='/pedidos')

# --- 1. VISUALIZAR (Lectura de Pedidos + Usuarios + Mesas) ---
@bp.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT p.id_pedido, p.fecha, p.total, 
               u.nombre AS nombre_mesero, 
               m.numero AS numero_mesa,
               m.estado AS estado_mesa
        FROM pedidos p
        JOIN usuarios u ON p.id_usuario = u.id_usuario
        JOIN mesas m ON p.id_mesa = m.id_mesa
        ORDER BY p.fecha DESC
    """
    cursor.execute(query)
    pedidos = cursor.fetchall()
    conn.close()
    return render_template('pedidos/index.html', pedidos=pedidos)

# Ver detalle interno (Lectura de Detalles + Productos)
@bp.route('/<int:id>')
def ver_detalle(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Cabecera
    cursor.execute("""
        SELECT p.*, u.nombre as mesero, m.numero as mesa
        FROM pedidos p
        JOIN usuarios u ON p.id_usuario = u.id_usuario
        JOIN mesas m ON p.id_mesa = m.id_mesa
        WHERE p.id_pedido = %s
    """, (id,))
    pedido = cursor.fetchone()
    
    # Detalles
    cursor.execute("""
        SELECT d.*, pr.nombre 
        FROM detalles_de_ventas d
        JOIN productos pr ON d.id_producto = pr.id_producto
        WHERE d.id_pedido = %s
    """, (id,))
    detalles = cursor.fetchall()
    conn.close()
    
    return render_template('pedidos/detalle.html', pedido=pedido, detalles=detalles)


# --- 2. INGRESAR (Afecta: Pedidos, Detalles, Mesas) ---
@bp.route('/nuevo', methods=['GET', 'POST'])
def nuevo_pedido():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    pedido_creado = False

    if request.method == 'POST':
        id_mesa = request.form['id_mesa']
        id_usuario = request.form['id_usuario']
        productos_ids = request.form.getlist('productos[]')
        cantidades = request.form.getlist('cantidades[]')

        try:
            conn.start_transaction()

            # A. Insertar Pedido
            cursor.execute("INSERT INTO pedidos (total, id_usuario, id_mesa, fecha) VALUES (0, %s, %s, NOW())", (id_usuario, id_mesa))
            id_nuevo_pedido = cursor.lastrowid

            total_acumulado = 0

            # B. Insertar Detalles (Loop)
            for i in range(len(productos_ids)):
                pid = productos_ids[i]
                cant = int(cantidades[i])
                if cant > 0:
                    cursor.execute("SELECT precio_base FROM productos WHERE id_producto = %s", (pid,))
                    prod_data = cursor.fetchone()
                    precio = prod_data['precio_base']
                    total_acumulado += (precio * cant)

                    cursor.execute("INSERT INTO detalles_de_ventas (id_pedido, id_producto, cantidad, precio_unitario) VALUES (%s, %s, %s, %s)", 
                                   (id_nuevo_pedido, pid, cant, precio))

            cursor.execute("UPDATE pedidos SET total = %s WHERE id_pedido = %s", (total_acumulado, id_nuevo_pedido))

            # C. Actualizar Mesa (Entidad 3)
            cursor.execute("UPDATE mesas SET estado = 'ocupada' WHERE id_mesa = %s", (id_mesa,))

            conn.commit()
            flash('Pedido creado y mesa ocupada.', 'success')
            pedido_creado = True

        except Exception as e:
            conn.rollback()
            flash(f'Error: {e}', 'danger')

    if pedido_creado:
        cursor.close()
        conn.close()
        return redirect(url_for('pedidos.index'))

    # Cargar datos para el formulario GET
    cursor.execute("SELECT * FROM mesas WHERE estado = 'disponible'")
    mesas = cursor.fetchall()
    cursor.execute("SELECT * FROM usuarios WHERE acceso = 'activo'")
    usuarios = cursor.fetchall()
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    conn.close()
    
    return render_template('pedidos/crear.html', mesas=mesas, usuarios=usuarios, productos=productos)


# --- 3. EDITAR (Afecta: Pedidos, Mesa Vieja, Mesa Nueva) ---
@bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_pedido(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        nueva_mesa_id = request.form['id_mesa']
        try:
            conn.start_transaction()
            
            # Obtener mesa actual
            cursor.execute("SELECT id_mesa FROM pedidos WHERE id_pedido = %s", (id,))
            row = cursor.fetchone()
            vieja_mesa_id = row['id_mesa']

            if str(vieja_mesa_id) != str(nueva_mesa_id):
                # A. Actualizar Pedido
                cursor.execute("UPDATE pedidos SET id_mesa = %s WHERE id_pedido = %s", (nueva_mesa_id, id))
                # B. Liberar mesa vieja
                cursor.execute("UPDATE mesas SET estado = 'disponible' WHERE id_mesa = %s", (vieja_mesa_id,))
                # C. Ocupar mesa nueva
                cursor.execute("UPDATE mesas SET estado = 'ocupada' WHERE id_mesa = %s", (nueva_mesa_id,))
                
                conn.commit()
                flash('Mesa del pedido actualizada.', 'success')
            else:
                flash('No hubo cambios de mesa.', 'info')

            return redirect(url_for('pedidos.index'))

        except Exception as e:
            conn.rollback()
            flash(f'Error al editar: {e}', 'danger')
        finally:
            cursor.close()
            conn.close()

    # GET
    cursor.execute("SELECT * FROM pedidos JOIN usuarios u ON pedidos.id_usuario = u.id_usuario WHERE id_pedido = %s", (id,))
    pedido = cursor.fetchone()
    
    # Traemos mesas disponibles + la actual
    cursor.execute("SELECT * FROM mesas WHERE estado = 'disponible' OR id_mesa = %s", (pedido['id_mesa'],))
    mesas = cursor.fetchall()
    conn.close()

    return render_template('pedidos/editar.html', pedido=pedido, mesas=mesas)


# --- 4. BORRAR (Afecta: Pedidos, Detalles(Cascade), Mesas) ---
@bp.route('/eliminar/<int:id>', methods=['POST'])
def eliminar_pedido(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        conn.start_transaction()
        
        # Obtener mesa para liberarla
        cursor.execute("SELECT id_mesa FROM pedidos WHERE id_pedido = %s", (id,))
        row = cursor.fetchone()
        
        if row:
            id_mesa = row['id_mesa']
            
            # A. Borrar Pedido (Entidad 1)
            # B. Borrar Detalles (Entidad 2 - Automático por ON DELETE CASCADE en MySQL)
            cursor.execute("DELETE FROM pedidos WHERE id_pedido = %s", (id,))
            
            # C. Actualizar Mesa (Entidad 3)
            cursor.execute("UPDATE mesas SET estado = 'disponible' WHERE id_mesa = %s", (id_mesa,))
            
            conn.commit()
            flash('Pedido eliminado y mesa liberada.', 'success')
        
    except Exception as e:
        conn.rollback()
        flash(f'Error al eliminar: {e}', 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('pedidos.index'))