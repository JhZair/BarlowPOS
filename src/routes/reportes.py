from flask import Blueprint, render_template, request, send_file
from src.database import get_db_connection
import pandas as pd
import io
from datetime import datetime, timedelta

bp = Blueprint('reportes', __name__, url_prefix='/reportes')

@bp.route('/', methods=['GET', 'POST'])
def ventas():
    conn = get_db_connection()
    if not conn:
        return "Error de conexión a BD"

    cursor = conn.cursor(dictionary=True)

    hoy = datetime.now()
    inicio_defecto = hoy.replace(day=1).strftime('%Y-%m-%d')
    fin_defecto = hoy.strftime('%Y-%m-%d')

    fecha_inicio = request.form.get('fecha_inicio', inicio_defecto)
    fecha_fin = request.form.get('fecha_fin', fin_defecto)

    params = [fecha_inicio + ' 00:00:00', fecha_fin + ' 23:59:59']
    where_clause = " WHERE p.fecha BETWEEN %s AND %s "

    sql_kpi = f"""
        SELECT 
            COALESCE(SUM(p.total), 0) as venta_total,
            COUNT(p.id_pedido) as total_pedidos,
            COALESCE(AVG(p.total), 0) as ticket_promedio
        FROM pedidos p
        {where_clause}
    """
    cursor.execute(sql_kpi, params)
    kpis = cursor.fetchone()

    sql_mozos = f"""
        SELECT u.nombre AS mesero, COUNT(p.id_pedido) AS cantidad, SUM(p.total) AS total
        FROM pedidos p
        JOIN usuarios u ON p.id_usuario = u.id_usuario
        {where_clause}
        GROUP BY u.nombre ORDER BY total DESC
    """
    cursor.execute(sql_mozos, params)
    data_mozos = cursor.fetchall()

    sql_productos = f"""
        SELECT prod.nombre, c.nombre as categoria, SUM(dv.cantidad) as cantidad_vendida, SUM(dv.cantidad * dv.precio_unitario) as total_generado
        FROM detalles_de_ventas dv
        JOIN pedidos p ON dv.id_pedido = p.id_pedido
        JOIN productos prod ON dv.id_producto = prod.id_producto
        JOIN clasificaciones c ON prod.id_clasificaciones = c.id_clasificacion
        {where_clause}
        GROUP BY prod.nombre, c.nombre
        ORDER BY cantidad_vendida DESC
        LIMIT 10
    """
    cursor.execute(sql_productos, params)
    data_productos = cursor.fetchall()

    sql_pagos = f"""
        SELECT pg.tipo_pago, SUM(pg.monto_entregado - COALESCE(pg.vuelto, 0)) as neto_recibido
        FROM pagos pg
        JOIN pedidos p ON pg.id_pedido = p.id_pedido
        {where_clause}
        GROUP BY pg.tipo_pago
    """
    cursor.execute(sql_pagos, params)
    data_pagos = cursor.fetchall()

    if 'btn_exportar' in request.form:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            
            df_kpi = pd.DataFrame([kpis])
            df_kpi.to_excel(writer, sheet_name='Resumen KPIs', index=False)

            if data_productos:
                pd.DataFrame(data_productos).to_excel(writer, sheet_name='Top Productos', index=False)
            
            if data_mozos:
                pd.DataFrame(data_mozos).to_excel(writer, sheet_name='Rendimiento Mozos', index=False)
            
            if data_pagos:
                pd.DataFrame(data_pagos).to_excel(writer, sheet_name='Métodos de Pago', index=False)

            sql_bruto = f"""
                SELECT p.id_pedido, p.fecha, u.nombre as usuario, m.numero as mesa, p.total
                FROM pedidos p
                JOIN usuarios u ON p.id_usuario = u.id_usuario
                JOIN mesas m ON p.id_mesa = m.id_mesa
                {where_clause}
                ORDER BY p.fecha DESC
            """
            cursor.execute(sql_bruto, params)
            data_bruto = cursor.fetchall()
            if data_bruto:
                pd.DataFrame(data_bruto).to_excel(writer, sheet_name='Detalle Transacciones', index=False)

        output.seek(0)
        cursor.close()
        conn.close()
        
        nombre_archivo = f"Reporte_Ventas_{fecha_inicio}_al_{fecha_fin}.xlsx"
        return send_file(output, download_name=nombre_archivo, as_attachment=True, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    cursor.close()
    conn.close()

    return render_template('reportes/ventas.html', 
                           kpis=kpis, 
                           mozos=data_mozos, 
                           productos=data_productos, 
                           pagos=data_pagos,
                           f_inicio=fecha_inicio, 
                           f_fin=fecha_fin)