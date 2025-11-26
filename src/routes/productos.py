from flask import Blueprint, render_template, request, redirect, url_for
from src.database import get_db_connection

bp = Blueprint('productos', __name__, url_prefix='/productos')

@bp.route('/')
def lista():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        sql = """
            SELECT p.id_producto, p.nombre, p.precio_base, p.tipo_producto, 
                   c.nombre AS nombre_clasificacion
            FROM productos p
            JOIN clasificaciones c ON p.id_clasificaciones = c.id_clasificacion
            ORDER BY p.nombre ASC
        """
        
        cursor.execute(sql)
        productos = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return render_template('productos/lista.html', productos=productos)
    else:
        return "Error de conexión a la Base de Datos"

@bp.route('/crear')
def crear():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM clasificaciones")
        categorias = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('productos/crear.html', categorias=categorias)
    return "Error de BD"

@bp.route('/guardar', methods=['POST'])
def guardar():
    nombre = request.form['nombre']
    precio = request.form['precio']
    id_clasif = request.form['categoria']
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        # Calculamos ID manual (porque no usaste AUTO_INCREMENT en tu SQL original)
        cursor.execute("SELECT COALESCE(MAX(id_producto), 0) + 1 FROM productos")
        nuevo_id = cursor.fetchone()[0]
        
        sql = "INSERT INTO productos (id_producto, nombre, precio_base, id_clasificaciones) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (nuevo_id, nombre, precio, id_clasif))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('productos.lista'))
    return "Error al guardar"

@bp.route('/editar/<int:id>')
def editar(id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        # 1. Buscar el producto específico
        cursor.execute("SELECT * FROM productos WHERE id_producto = %s", (id,))
        producto = cursor.fetchone()
        
        # 2. Cargar categorías para el combo box
        cursor.execute("SELECT id_clasificacion, nombre FROM clasificaciones")
        categorias = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        if producto:
            return render_template('productos/editar.html', producto=producto, categorias=categorias)
        else:
            return "Producto no encontrado"
    return "Error de conexión"

# --- RUTA: Procesar la ACTUALIZACIÓN (POST) ---
@bp.route('/actualizar', methods=['POST'])
def actualizar():
    # Recibimos el ID oculto y los datos nuevos
    id_producto = request.form['id_producto']
    nombre = request.form['nombre']
    precio = request.form['precio']
    tipo = request.form['tipo']
    id_clasificacion = request.form['categoria']
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        sql = """
            UPDATE productos 
            SET nombre = %s, precio_base = %s, tipo_producto = %s, id_clasificaciones = %s
            WHERE id_producto = %s
        """
        values = (nombre, precio, tipo, id_clasificacion, id_producto)
        
        try:
            cursor.execute(sql, values)
            conn.commit()
        except Exception as e:
            print(f"Error al actualizar: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
            
        return redirect(url_for('productos.lista'))
    return "Error de conexión"

# --- RUTA: ELIMINAR ---
@bp.route('/eliminar/<int:id>')
def eliminar(id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # Intento de borrado
            cursor.execute("DELETE FROM productos WHERE id_producto = %s", (id,))
            conn.commit()
        except Exception as e:
            print(f"No se puede eliminar (probablemente tiene ventas asociadas): {e}")
        finally:
            cursor.close()
            conn.close()
            
        return redirect(url_for('productos.lista'))
    return "Error de conexión"