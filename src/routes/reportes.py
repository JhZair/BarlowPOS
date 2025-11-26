from flask import Blueprint, render_template, request, send_file
from src.database import get_db_connection
import pandas as pd
import io

bp = Blueprint('reportes', __name__, url_prefix='/reportes')

@bp.route('/', methods=['GET', 'POST'])
def ventas():
    conn = get_db_connection()
    resultados = []
    
    # Obtenemos las fechas del formulario (si es que enviaron algo)
    fecha_inicio = request.form.get('fecha_inicio')
    fecha_fin = request.form.get('fecha_fin')
    
    # SQL Base: Total vendido por cada Mesero
    sql = """
        SELECT 
            u.nombre AS mesero, 
            COUNT(p.id_pedido) AS cantidad_pedidos, 
            SUM(p.total) AS total_vendido
        FROM pedidos p
        JOIN usuarios u ON p.id_usuario = u.id_usuario
    """
    
    params = []
    
    # Si hay fechas seleccionadas, agregamos el filtro WHERE
    if fecha_inicio and fecha_fin:
        sql += " WHERE p.fecha BETWEEN %s AND %s "
        # Agregamos horas para cubrir todo el día final (hasta las 23:59:59)
        params = [fecha_inicio + ' 00:00:00', fecha_fin + ' 23:59:59']
        
    sql += " GROUP BY u.nombre"
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params)
        resultados = cursor.fetchall()
        
        # --- LÓGICA DE EXPORTAR A EXCEL ---
        # Si presionaron el botón "Descargar Excel"
        if 'btn_exportar' in request.form:
            # 1. Convertir datos a DataFrame de Pandas
            df = pd.DataFrame(resultados)
            
            if not df.empty:
                # 2. Crear archivo Excel en memoria (RAM)
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Ventas')
                output.seek(0)
                
                cursor.close()
                conn.close()
                
                # 3. Enviar el archivo al navegador
                return send_file(output, 
                                 download_name="reporte_ventas.xlsx", 
                                 as_attachment=True,
                                 mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        
        cursor.close()
        conn.close()

    return render_template('reportes/ventas.html', resultados=resultados)