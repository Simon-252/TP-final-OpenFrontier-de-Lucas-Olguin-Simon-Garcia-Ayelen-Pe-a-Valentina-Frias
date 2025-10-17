from flask import Blueprint, request, jsonify, render_template 
from models.users_models import User
from models.db import db
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from flask import current_app as app #importa la instancia de Flask, para acceder a la configuración de la app
from functools import wraps #sirve para decorar funciones
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

def token_required(role=None): #decorador para proteger rutas, si se pasa role, solo usuarios con ese rol pueden acceder
    def decorator(f): #funcion que recibe la funcion a decorar
        @wraps(f) #preserva el nombre y docstring de la funcion original, docstring es la descripcion de la funcion
        def decorated(*args, **kwargs): #funcion que se ejecuta en lugar de la original, args y kwargs son los argumentos posicionales
            token = request.headers.get('Authorization')
            if not token: #sino hay token, devuelve error 401
                return jsonify({'message': 'Token is missing'}), 401
            try: #si hay token, lo decodifica y busca el usuario
                token = token.split()[1]  # Bearer <token>
                data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"]) #decodifica el token con la clave secreta y el algoritmo HS256, el algoritmo es el metodo de cifrado
                current_user = User.query.get(data['id']) #busca el usuario por id
                if not current_user: #sino encuentra el usuario, devuelve error 404
                    return jsonify({'message': 'User not found'}), 404
                if role and current_user.role != role: #si se pasa rol y el usuario no tiene ese rol, devuelve error 403
                    return jsonify({'message': 'Unauthorized'}), 403
            except Exception as e: #si hay error al decodificar el token, devuelve error 401
                return jsonify({'message': 'Token is invalid', 'error': str(e)}), 401 #muestra el error para debug
            return f(current_user, *args, **kwargs) #si todo va bien, ejecuta la funcion original pasando el usuario actual como primer argumento
        return decorated
    return decorator #retorna el decorador principal, porque hay dos niveles de decoradores

@auth_bp.route("/register", methods=["POST"]) #ruta para registrar usuarios
def register(): #funcion que registra usuarios
    data = request.get_json()
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists'}), 400
    hashed_pw = generate_password_hash(data['password'])
    new_user = User(
        username=data['username'],
        email=data['email'],
        password=hashed_pw,
        role=data.get('role', 'user')
    )
    db.session.add(new_user)
    db.session.commit()

    # Después de crear el usuario, generamos el token para devolverlo (opcional, pero útil)
    token = jwt.encode({
        'id': str(new_user.id),  # Usamos str(new_user.id) para asegurarnos de que sea JSON serializable
        'exp': datetime.utcnow() + timedelta(hours=1)
    }, app.config['SECRET_KEY'], algorithm="HS256")

    # 🔹 CAMBIO 1: Devolver el token y la URL de redirección al layout (/)
    return jsonify({
        'message': 'User created successfully',
        'token': token,
        # La ruta 'index' está definida en app.py como la que sirve layout.html
        'redirect_url': '/' 
    }), 201


@auth_bp.route("/register", methods=["GET"]) #ruta para mostrar el formulario de registro
def register_page():
    return render_template("register.html")


@auth_bp.route("/login", methods=["POST"]) #ruta para loguear usuarios
def login(): #funcion que loguea usuarios
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401

    token = jwt.encode({
        'id': str(user.id), # Asegúrate de que el ID sea string si es necesario
        'exp': datetime.utcnow() + timedelta(hours=1),
        'role': user.role,        
        'username': user.username 
    }, app.config['SECRET_KEY'], algorithm="HS256")

    # 🔑 LÓGICA DE REDIRECCIÓN CONDICIONAL 🔑
    if user.role == 'admin':
        # Redirige al administrador a su panel (Lista de Usuarios)
        final_redirect_url = '/dashboard' 
    else:
        # Redirige al usuario normal al layout principal
        final_redirect_url = '/' 

    return jsonify({
        'token': token,
        'role': user.role,
        'username': user.username,
        'redirect_url': final_redirect_url # Usamos la URL decidida
    })

@auth_bp.route("/login", methods=["GET"]) # Ruta para MOSTRAR el formulario de login
def login_page():
    # Asume que tienes un archivo login.html en la carpeta 'templates'
    return render_template("login.html")

@auth_bp.route("/dashboard", methods=["GET"]) #ruta para mostrar el dashboard
def dashboard_page():
    return render_template("dashboard_lista_de_usuario.html")

@auth_bp.route("/panel_clima_y_pasos", methods=["GET"]) #ruta para mostrar el panel de clima y pasos
def panel_clima_y_pasos():
    return render_template("panel_clima_y_pasos.html")

@auth_bp.route("/api/dashboard", methods=["GET"]) #ruta para mostrar el dashboard (API)
@token_required()
def dashboard_api(current_user): #funcion que muestra el dashboard, recibe el usuario actual como argumento
    return jsonify({
        'username': current_user.username,
        'role': current_user.role
    })

@auth_bp.route("/api/users", methods=["GET"]) #ruta para listar usuarios (solo admins)
@token_required(role="admin")  # Solo admins
def list_users(current_user): #funcion que lista los usuarios, recibe el usuario actual como argumento
    users = User.query.all() #busca todos los usuarios
    users_data = [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "role": u.role
        } for u in users
    ] #lista por comprensión que crea una lista de diccionarios con los datos de los usuarios
    return jsonify(users_data) #devuelve la lista de usuarios en formato JSON

# En routes/users_routes.py
@auth_bp.route("/api/users/<user_id>", methods=["PATCH"])
@token_required(role="admin")
def update_user_role(current_user, user_id):
    # 1. Buscar al usuario a editar
    user_to_update = User.query.get(user_id)
    
    if not user_to_update:
        return jsonify({"message": "User not found"}), 404
        
    # 2. Evitar que un admin se auto-despoje de su rol (opcional, pero buena práctica)
    if user_to_update.id == current_user.id and request.get_json().get('role') != 'admin':
        return jsonify({"message": "Admin cannot downgrade their own role via API"}), 403

    # 3. Obtener el nuevo rol del JSON
    data = request.get_json()
    new_role = data.get('role')
    
    if not new_role or new_role not in ['user', 'admin']:
        return jsonify({"message": "Invalid role provided"}), 400

    # 4. Actualizar y guardar
    user_to_update.role = new_role
    db.session.commit()
    
    return jsonify({"message": f"User {user_id} role updated to {new_role}"}), 200

# En routes/users_routes.py
@auth_bp.route("/api/users/<user_id>", methods=["DELETE"])
@token_required(role="admin")
def delete_user(current_user, user_id):
    # 1. Buscar al usuario a eliminar
    user_to_delete = User.query.get(user_id)
    
    if not user_to_delete:
        return jsonify({"message": "User not found"}), 404
        
    # 2. Prevenir la auto-eliminación
    if user_to_delete.id == current_user.id:
        return jsonify({"message": "Admin cannot delete their own account via this panel"}), 403

    # 3. Eliminar y guardar
    db.session.delete(user_to_delete)
    db.session.commit()
    
    return jsonify({"message": f"User {user_id} deleted successfully"}), 200