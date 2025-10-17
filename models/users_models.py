import uuid # Importa la librería uuid para generar identificadores únicos
from models.db import db

class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(90), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="user")  # 'user' o 'admin'
    phone = db.Column(db.String(20), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'phone': self.phone
        } #método para convertir el objeto en un diccionario, útil para serializar a JSON, serializar significa convertir 
            #un objeto en un formato que se pueda almacenar o transmitir
