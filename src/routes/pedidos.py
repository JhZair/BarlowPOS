from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.database import get_db_connection

bp = Blueprint('pedidos', __name__, url_prefix='/pedidos')

# 1. VISUALIZAR LISTA DE PEDIDOS (Lectura de 3 tablas: Pedidos + Usuarios + Mesas)
@bp.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Hacemos JOIN para mostrar nombres en lugar de IDs
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

# 2. VISUALIZAR DETALLE DE UN PEDIDO (Lectura de: Detalles + Productos)
@bp.route('/<int:id>')
def ver_detalle(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Obtener cabecera
    cursor.execute("""
        SELECT p.*, u.nombre as mesero, m.numero as mesa
        FROM pedidos p
        JOIN usuarios u ON p.id_usuario = u.id_usuario
        JOIN mesas m ON p.id_mesa = m.id_mesa
        WHERE p.id_pedido = %s
    """, (id,))
    pedido = cursor.fetchone()
    
    # Obtener los productos (JOIN con productos para saber el nombre)
    cursor.execute("""
        SELECT d.*, pr.nombre 
        FROM detalles_de_ventas d
        JOIN productos pr ON d.id_producto = pr.id_producto
        WHERE d.id_pedido = %s
    """, (id,))
    detalles = cursor.fetchall()
    
    conn.close()
    
    if pedido is None:
        flash('Pedido no encontrado', 'danger')
        return redirect(url_for('pedidos.index'))
        
    return render_template('pedidos/detalle.html', pedido=pedido, detalles=detalles)


@bp.route('/nuevo', methods=['GET', 'POST'])
def nuevo_pedido():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Variable para controlar si redirigimos o mostramos el html
    pedido_creado = False

    if request.method == 'POST':
        # Datos del formulario
        id_mesa = request.form['id_mesa']
        id_usuario = request.form['id_usuario']
        
        productos_ids = request.form.getlist('productos[]')
        cantidades = request.form.getlist('cantidades[]')

        try:
            conn.start_transaction()

            # 1. Crear cabecera
            cursor.execute(
                "INSERT INTO pedidos (total, id_usuario, id_mesa, fecha) VALUES (%s, %s, %s, NOW())",
                (0, id_usuario, id_mesa)
            )
            id_nuevo_pedido = cursor.lastrowid

            total_acumulado = 0

            # 2. Insertar detalles
            for i in range(len(productos_ids)):
                pid = productos_ids[i]
                cant = int(cantidades[i])
                
                if cant > 0:
                    cursor.execute("SELECT precio_base FROM productos WHERE id_producto = %s", (pid,))
                    producto = cursor.fetchone()
                    
                    if producto: # Validación extra por seguridad
                        precio = producto['precio_base']
                        subtotal = precio * cant
                        total_acumulado += subtotal

                        cursor.execute("""
                            INSERT INTO detalles_de_ventas (id_pedido, id_producto, cantidad, precio_unitario)
                            VALUES (%s, %s, %s, %s)
                        """, (id_nuevo_pedido, pid, cant, precio))

            # Actualizar total
            cursor.execute("UPDATE pedidos SET total = %s WHERE id_pedido = %s", (total_acumulado, id_nuevo_pedido))

            # 3. Bloquear mesa
            cursor.execute("UPDATE mesas SET estado = 'ocupada' WHERE id_mesa = %s", (id_mesa,))

            conn.commit()
            flash('Pedido creado exitosamente', 'success')
            pedido_creado = True # Marcamos éxito

        except Exception as e:
            conn.rollback()
            flash(f'Error al crear el pedido: {e}', 'danger')
            # NO CERRAMOS AQUI, dejamos que el código fluya para recargar el formulario

    # Si se creó con éxito, cerramos y redirigimos
    if pedido_creado:
        cursor.close()
        conn.close()
        return redirect(url_for('home.index'))

    # --- SI LLEGAMOS AQUI ES PORQUE ES UN GET O EL POST FALLÓ ---
    # Necesitamos la conexión abierta para cargar las listas nuevamente
    
    try:
        # Cargar datos para el formulario
        cursor.execute("SELECT * FROM mesas WHERE estado = 'disponible'")
        mesas_disponibles = cursor.fetchall()

        cursor.execute("SELECT * FROM usuarios WHERE acceso = 'activo'")
        usuarios = cursor.fetchall()

        cursor.execute("SELECT * FROM productos")
        productos = cursor.fetchall()
        
        return render_template('pedidos/crear.html', mesas=mesas_disponibles, usuarios=usuarios, productos=productos)
    
    finally:
        # Aquí sí cerramos definitivamente pase lo que pase al renderizar
        cursor.close()
        conn.close()


@bp.route('/eliminar/<int:id>', methods=['POST'])
def eliminar_pedido(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        conn.start_transaction()

        # 1. Averiguar qué mesa estaba ocupando este pedido antes de borrarlo
        cursor.execute("SELECT id_mesa FROM pedidos WHERE id_pedido = %s", (id,))
        pedido = cursor.fetchone()

        if not pedido:
            flash('El pedido no existe.', 'warning')
            return redirect(url_for('pedidos.index'))

        id_mesa = pedido['id_mesa']

        # 2. Borrar el pedido
        # Gracias al ON DELETE CASCADE en tu CREATE TABLE, 
        # esto también borra los 'detalles_de_ventas' automáticamente.
        cursor.execute("DELETE FROM pedidos WHERE id_pedido = %s", (id,))

        # 3. Liberar la mesa (ponerla en 'disponible')
        # Solo lo hacemos si la mesa estaba 'ocupada' para evitar inconsistencias
        cursor.execute("UPDATE mesas SET estado = 'disponible' WHERE id_mesa = %s", (id_mesa,))

        conn.commit()
        flash('Pedido eliminado y mesa liberada correctamente.', 'success')

    except Exception as e:
        conn.rollback()
        flash(f'Error al eliminar el pedido: {e}', 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('pedidos.index'))


@bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_pedido(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        nueva_mesa_id = request.form['id_mesa']
        
        try:
            conn.start_transaction()

            # 1. Obtener la mesa actual que tiene el pedido antes de cambiarla
            cursor.execute("SELECT id_mesa FROM pedidos WHERE id_pedido = %s", (id,))
            pedido_actual = cursor.fetchone()
            
            if not pedido_actual:
                raise Exception("El pedido no existe")

            vieja_mesa_id = pedido_actual['id_mesa']

            # Solo hacemos cambios si seleccionaron una mesa diferente
            if str(vieja_mesa_id) != str(nueva_mesa_id):
                # A. Actualizar la cabecera del PEDIDO
                cursor.execute("UPDATE pedidos SET id_mesa = %s WHERE id_pedido = %s", (nueva_mesa_id, id))

                # B. Liberar la mesa VIEJA
                cursor.execute("UPDATE mesas SET estado = 'disponible' WHERE id_mesa = %s", (vieja_mesa_id,))

                # C. Ocupar la mesa NUEVA
                cursor.execute("UPDATE mesas SET estado = 'ocupada' WHERE id_mesa = %s", (nueva_mesa_id,))

                conn.commit()
                flash('Mesa actualizada correctamente.', 'success')
            else:
                flash('No se realizaron cambios (misma mesa seleccionada).', 'info')

            return redirect(url_for('pedidos.index'))

        except Exception as e:
            conn.rollback()
            flash(f'Error al editar el pedido: {e}', 'danger')
        finally:
            cursor.close()
            conn.close()

    # --- GET: Mostrar formulario ---
    
    # Buscamos el pedido para saber qué mesa tiene actualmente
    cursor.execute("""
        SELECT p.*, u.nombre as nombre_mesero 
        FROM pedidos p 
        JOIN usuarios u ON p.id_usuario = u.id_usuario 
        WHERE id_pedido = %s
    """, (id,))
    pedido = cursor.fetchone()

    if not pedido:
        flash('Pedido no encontrado', 'danger')
        return redirect(url_for('pedidos.index'))

    # Buscamos mesas disponibles + la mesa actual (para que aparezca seleccionada en la lista)
    cursor.execute("""
        SELECT * FROM mesas 
        WHERE estado = 'disponible' OR id_mesa = %s
    """, (pedido['id_mesa'],))
    mesas = cursor.fetchall()
    
    conn.close()
    return render_template('pedidos/editar.html', pedido=pedido, mesas=mesas)