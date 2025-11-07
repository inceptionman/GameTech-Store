"""
Script para ejecutar la migración de base de datos
Detecta automáticamente si es SQLite o PostgreSQL
"""
import sys
import os
from dotenv import load_dotenv

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Cargar variables de entorno
load_dotenv()

if __name__ == '__main__':
    # Detectar tipo de base de datos
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///instance/gametech_store.db')
    
    if database_url.startswith('postgresql') or database_url.startswith('postgres'):
        print("🔍 Base de datos detectada: PostgreSQL (Neon Tech)")
        from migrations.migrate_neontech import migrate
    else:
        print("🔍 Base de datos detectada: SQLite (Local)")
        from migrations.add_hardware_analysis_tables import migrate
    
    try:
        migrate()
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        sys.exit(1)
