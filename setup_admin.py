"""
Script para configurar la contraseña del administrador de forma segura
"""
import bcrypt
from getpass import getpass
import os
from dotenv import load_dotenv

def setup_admin_password():
    """Configura la contraseña del administrador de forma segura"""
    print("\n=== Configuración de Contraseña de Administrador ===")
    
    while True:
        password = getpass("Ingresa la nueva contraseña de administrador: ")
        confirm = getpass("Confirma la contraseña: ")
        
        if password != confirm:
            print("Las contraseñas no coinciden. Intenta de nuevo.\n")
            continue
            
        if len(password) < 8:
            print("La contraseña debe tener al menos 8 caracteres. Intenta de nuevo.\n")
            continue
            
        if not any(c.isupper() for c in password):
            print("La contraseña debe contener al menos una mayúscula. Intenta de nuevo.\n")
            continue
            
        if not any(c.islower() for c in password):
            print("La contraseña debe contener al menos una minúscula. Intenta de nuevo.\n")
            continue
            
        if not any(c.isdigit() for c in password):
            print("La contraseña debe contener al menos un número. Intenta de nuevo.\n")
            continue
        
        break
    
    # Generar el hash de la contraseña
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    # Cargar el archivo .env existente
    load_dotenv()
    env_content = ""
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            env_content = f.read()
    
    # Eliminar configuraciones antiguas de admin si existen
    env_lines = env_content.split('\n')
    env_lines = [line for line in env_lines if not line.startswith(('ADMIN_PASSWORD_HASH=', 'ADMIN_USERNAME='))]
    
    # Añadir las nuevas configuraciones
    env_lines.append('\n# Credenciales de administrador')
    env_lines.append('ADMIN_USERNAME=admin')
    env_lines.append(f'ADMIN_PASSWORD_HASH={password_hash.decode("utf-8")}')
    
    # Guardar el archivo .env actualizado
    with open('.env', 'w') as f:
        f.write('\n'.join(env_lines))
    
    print("\n✅ Contraseña de administrador configurada exitosamente!")
    print("La contraseña ha sido hasheada y almacenada de forma segura en el archivo .env")

if __name__ == '__main__':
    setup_admin_password()