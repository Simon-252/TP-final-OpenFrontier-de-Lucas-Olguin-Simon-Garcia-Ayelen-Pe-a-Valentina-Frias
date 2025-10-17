from flask import Flask, render_template
from config.config import DATABASE_CONNECTION_URI, SECRET_KEY, WEATHER_API_KEY
from models.db import db
from routes.about import about
from routes.tomar_paso_routes import pasos, actualizar_estado
from routes.users_routes import auth_bp
from routes.clima_routes import clima_bp
from flask_migrate import Migrate
from flask_apscheduler import APScheduler

# ---------------------------------------------------
# Inicialización de Flask
# ---------------------------------------------------
app = Flask(__name__)
app.secret_key = "clave_secreta"  # necesaria para usar flash

# ---------------------------------------------------
# Configuración
# ---------------------------------------------------
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_CONNECTION_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = SECRET_KEY
app.config["WEATHER_API_KEY"] = WEATHER_API_KEY

db.init_app(app)
migrate = Migrate(app, db)

scheduler = APScheduler()

# ---------------------------------------------------
# Registro de Blueprints
# ---------------------------------------------------
app.register_blueprint(clima_bp)
app.register_blueprint(pasos)
app.register_blueprint(about)
app.register_blueprint(auth_bp)

# ---------------------------------------------------
# Rutas
# ---------------------------------------------------
@app.route("/")  # Ruta principal
def index():
    return render_template("layout.html")

# ---------------------------------------------------
# Jobs automáticos
# ---------------------------------------------------
def job_actualizar_estado():
    """Ejecuta la actualización del paso dentro del contexto de la app"""
    with app.app_context():
        actualizar_estado()

def job_actualizar_clima():
    """Ejecuta la actualización del clima dentro del contexto de la app"""
    from routes.clima_routes import actualizar_automatico
    with app.app_context():
        actualizar_automatico()

# ---------------------------------------------------
# Main
# ---------------------------------------------------
with app.app_context():
    #db.drop_all()   # Solo si necesitas recrear la base de datos
    #db.create_all()
    actualizar_estado()  # Ejecutamos la función una vez al iniciar

if __name__ == "__main__":
    scheduler.init_app(app)

    # Programa la tarea: ejecutar la función cada 30 minutos
    scheduler.add_job(
        id="actualizar_estado_paso",
        func=job_actualizar_estado,
        trigger="interval",
        minutes=30
    )

    # Programa la tarea: ejecutar la función cada 10 minutos (clima)
    scheduler.add_job(
        id="actualizar_clima",
        func=job_actualizar_clima,
        trigger="interval",
        minutes=10
    )

    scheduler.start()
    app.run(debug=True, use_reloader=False)