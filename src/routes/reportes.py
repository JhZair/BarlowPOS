from flask import Blueprint, render_template, request, send_file
from src.database import get_db_connection
import pandas as pd
import io

bp = Blueprint('reportes', __name__, url_prefix='/reportes')

@bp.route('/', methods=['GET', 'POST'])
def ventas():
    conn = get_db_connection()
    resultados = []
    
    # Filtros de fecha (por defecto vacíos)
    fecha_inicio = request.form.get('fecha_inicio')
    fecha_fin = request.form.get('fecha_fin')
    
    sql = """
        SELECT 
            u.nombre as mesero,
            COUNT(p.id_pedido) as cantidad_pedidos,
            SUM(p.total) as total_vendido
        FROM pedidos p
        JOIN usuarios u ON p.id_usuario = u.id_usuario
    """
    
    # Lógica de filtro (WHERE dinámico)
    params = []
    if fecha_inicio and fecha_fin:
        sql += " WHERE p.fecha BETWEEN %s AND %s "
        params = [fecha_inicio, fecha_fin]
        
    sql += " GROUP BY u.nombre"
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params)
        resultados = cursor.fetchall()
        
        # --- EXPORTACIÓN A EXCEL ---
        if 'exportar_excel' in request.form:
            # Convertimos la lista de diccionarios a DataFrame de Pandas
            df = pd.DataFrame(resultados)
            if not df.empty:
                output = io.BytesIO()
                # Escribir el Excel en memoria
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Ventas')
                output.seek(0)
                
                return send_file(output, 
                                 download_name="reporte_ventas.xlsx", 
                                 as_attachment=True)
        
        cursor.close()
        conn.close()

    return render_template('reportes/ventas.html', resultados=resultados)