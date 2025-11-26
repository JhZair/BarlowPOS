from flask import Flask
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'clave_secreta_desarrollo'

    # --- REGISTRO DE RUTAS ---
    from .routes import home
    from .routes import usuarios
    from .routes import productos
    from .routes import reportes
    from .routes import productos

    app.register_blueprint(home.bp)
    app.register_blueprint(usuarios.bp)
    app.register_blueprint(productos.bp)

    @app.route('/prueba-db')
    def prueba_db():
        from src.database import get_db_connection
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DATABASE();")
            nombre_db = cursor.fetchone()
            conn.close()
            return f"<h1>¡Conexión Exitosa!</h1> Estás conectado a la base de datos: <b>{nombre_db[0]}</b>"
        else:
            return "<h1>Error de Conexión</h1> Revisa la terminal para ver el error."

    return app