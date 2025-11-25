from flask import Blueprint, render_template

# Creamos un "Blueprint" (un grupo de rutas)
bp = Blueprint('home', __name__)

@bp.route('/')
def index():
    return render_template('index.html')