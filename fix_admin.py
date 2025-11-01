import sqlite3
import os
from dotenv import load_dotenv
# Cargar variables de entorno desde .env
load_dotenv()

# Obtener la contraseña de las variables de entorno
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'G@meT3ch2023!')  # Valor por defecto solo para desarrollo

# Asegurarse de que el directorio instance existe
if not os.path.exists('instance'):
    os.makedirs('instance')

# Conectar a la base de datos
db_path = os.path.join('instance', 'gametech_store.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Actualizar el usuario admin existente
    cursor.execute('''
        UPDATE users 
        SET is_admin = 1 
        WHERE username = 'admin'
    ''')
    
    if cursor.rowcount == 0:
        # Si no existe el usuario admin, crearlo
        from werkzeug.security import generate_password_hash
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, is_admin, is_active)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', 'admin@gametechstore.com', generate_password_hash(ADMIN_PASSWORD), 1, 1))
    
    conn.commit()
    print("✅ Usuario admin actualizado/creado exitosamente")
    print("Usuario: admin")
    print("✅ El usuario admin ha sido configurado con éxito")

except sqlite3.Error as e:
    print(f"❌ Error en la base de datos: {str(e)}")
    if "no such table" in str(e):
        print("La tabla users no existe. Por favor, ejecuta la aplicación primero para crear las tablas.")

finally:
    conn.close()