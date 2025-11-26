from flask import Blueprint, render_template
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