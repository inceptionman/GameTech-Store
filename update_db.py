"""
Script para actualizar la base de datos con los campos de recuperación de contraseña
"""
from app import app
from database import db
from models.database_models import User

def update_database():
    """Agregar campos de recuperación de contraseña"""
    with app.app_context():
        # Crear las tablas si no existen
        db.create_all()
        
        # Verificar si las columnas existen
        inspector = db.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('users')]
        
        if 'reset_token' not in columns:
            with db.engine.connect() as conn:
                # Agregar las nuevas columnas
                conn.execute(db.text('''
                    ALTER TABLE users 
                    ADD COLUMN reset_token VARCHAR(100) UNIQUE,
                    ADD COLUMN reset_token_expiry TIMESTAMP WITH TIME ZONE
                '''))
                
                # Commit the transaction
                conn.commit()
            
            print("Base de datos actualizada exitosamente")
        else:
            print("La base de datos ya está actualizada")

if __name__ == '__main__':
    update_database()