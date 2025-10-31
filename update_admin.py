"""
Script para actualizar los permisos del usuario admin
"""
from flask import Flask
from extensions import db
from models.database_models import User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/gametech_store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Asegurarnos de que el directorio instance existe
import os
if not os.path.exists('instance'):
    os.makedirs('instance')

db.init_app(app)

with app.app_context():
    try:
        # Buscar el usuario admin
        admin = User.query.filter_by(username='admin').first()
        if admin:
            admin.is_admin = True
            db.session.commit()
            print("✅ Usuario admin actualizado con éxito - permisos de administrador concedidos")
        else:
            # Crear el usuario admin si no existe
            from werkzeug.security import generate_password_hash
            admin = User(
                username='admin',
                email='admin@gametechstore.com',
                password_hash=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Usuario admin creado con éxito con permisos de administrador")
            print("Usuario: admin")
            print("Contraseña: admin123")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        # Si hay tablas que no existen, crearlas
        db.create_all()
        print("✅ Base de datos inicializada. Por favor, ejecuta el script nuevamente.")