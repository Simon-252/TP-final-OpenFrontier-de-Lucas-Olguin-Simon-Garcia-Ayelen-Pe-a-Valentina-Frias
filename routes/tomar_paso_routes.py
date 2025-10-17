# routes/tomar_paso_routes.py
from flask import current_app, Blueprint, jsonify, render_template
import requests, re
from bs4 import BeautifulSoup
from config.constantes import URL, IMAGE_FILENAMES
from models.db import db
from models.paso_models import Paso
from routes.users_routes import token_required
import random


# Blueprint para /paso
pasos = Blueprint("pasos", __name__, url_prefix="/paso")


@pasos.route("/api", methods=["GET"])
@token_required()
def api_paso(current_user):
    """Devuelve el último Paso en JSON (protegido)."""
    paso = Paso.query.first()
    if paso:
        return jsonify(paso.to_dict())
    return jsonify({"message": "No hay registros de paso"}), 404

# Nuevo endpoint público para el layout.html (usuarios no autenticados)
@pasos.route("/public_api", methods=["GET"])
def public_api_paso():
    """Devuelve el último Paso en JSON (público, sin token) y una imagen al azar."""
    paso = Paso.query.first()

    # Lógica para elegir una imagen al azar
    random_image = random.choice(IMAGE_FILENAMES)

    if paso:
        # Crea el diccionario de datos de la BD
        data = paso.to_dict()
        
        # Agrega el nombre de la imagen al diccionario de respuesta
        data['image_filename'] = random_image
        
        return jsonify(data), 200
    
    # Si la BD está vacía, devuelve el error 404, pero también una imagen por defecto
    return jsonify({
        "message": "No hay registros de paso",
        "estado": "desconocido", 
        "image_filename": random_image # Usa una imagen al azar aunque no haya estado
    }), 404

@pasos.route("/", methods=["GET"])
def ver_paso():
    """Vista HTML para debug/manual (opcional)."""
    paso = Paso.query.first()
    return render_template("paso/paso.html", pasos=paso.to_dict() if paso else {})


def actualizar_estado():
    """
    Scrapea la web y actualiza el estado del paso en la BD.
    Esta función puede llamarse desde el scheduler. Abre app_context internamente.
    """
    with current_app.app_context():
        try:
            resp = requests.get(URL, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            texto = soup.find(string=re.compile(r"^(Abierto|Cerrado|Habilitado)", re.IGNORECASE))
            if texto:
                string_paso = texto.strip()
            else:
                string_paso = "Estado desconocido"

            m = re.match(r"^(Abierto|Cerrado|Habilitado)\s*(.*)$", string_paso, re.IGNORECASE)
            if m:
                estado = m.group(1)
                actualizado = m.group(2).strip()
            else:
                estado, actualizado = string_paso, ""

        except Exception as e:
            estado = "Error"
            actualizado = str(e)

        paso = Paso.query.first()
        if not paso:
            # Crear el primer Paso si no existe
            paso = Paso(nombre="Cristo Redentor")

        paso.estado = estado
        paso.actualizado = actualizado
        paso.fuente = URL
        paso.timestamp = db.func.now()

        db.session.add(paso)
        db.session.commit()

        return paso.to_dict()
