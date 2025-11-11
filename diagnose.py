#!/usr/bin/env python
"""
Diagnosticar problemas con la aplicación
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("DIAGNÓSTICO DE LA APLICACIÓN GAMETECH STORE")
print("=" * 60)

# 1. Verificar DATABASE_URL
print("\n1️⃣  DATABASE_URL:")
db_url = os.environ.get('DATABASE_URL')
if db_url:
    # Ocultar credenciales
    if 'postgresql' in db_url:
        print(f"   ✓ PostgreSQL configurado (URL ocultada por seguridad)")
    elif 'sqlite' in db_url:
        print(f"   ✓ SQLite: {db_url}")
    else:
        print(f"   ? Desconocido: {db_url[:50]}...")
else:
    print("   ✗ No configurado, usando SQLite por defecto")

# 2. Verificar que la carpeta instance existe
print("\n2️⃣  Carpeta 'instance':")
if os.path.exists('instance'):
    print("   ✓ Existe")
    if os.path.exists('instance/gametech_store.db'):
        print("   ✓ Base de datos SQLite existe")
    else:
        print("   ⚠ Base de datos SQLite no existe (se creará)")
else:
    print("   ✗ No existe, creando...")
    os.makedirs('instance', exist_ok=True)
    print("   ✓ Creada")

# 3. Intentar importar la aplicación
print("\n3️⃣  Importación de la aplicación:")
try:
    from app import app
    print("   ✓ app.py importado correctamente")
except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)

# 4. Verificar controladores
print("\n4️⃣  Controladores:")
controllers = [
    'store',
    'hardware',
    'auth',
    'cart',
    'admin',
    'analyzer',
    'invoice',
    'wishlist'
]

for controller in controllers:
    try:
        if controller == 'analyzer':
            from controllers.hardware_analyzer import analyzer_bp
        else:
            exec(f"from controllers.{controller} import {controller}_bp")
        print(f"   ✓ {controller}")
    except Exception as e:
        print(f"   ✗ {controller}: {e}")

# 5. Inicializar base de datos
print("\n5️⃣  Inicialización de BD:")
try:
    with app.app_context():
        from database import db
        db.create_all()
        print("   ✓ Tablas creadas/verificadas")
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

# 6. Verificar hardware disponible
print("\n6️⃣  Hardware en BD:")
try:
    with app.app_context():
        from models.database_models import Hardware
        cpus = Hardware.get_hardware_by_tipo('CPU')
        gpus = Hardware.get_hardware_by_tipo('GPU')
        rams = Hardware.get_hardware_by_tipo('RAM')
        
        print(f"   CPUs: {len(cpus)}")
        print(f"   GPUs: {len(gpus)}")
        print(f"   RAMs: {len(rams)}")
        
        if len(cpus) == 0 or len(gpus) == 0 or len(rams) == 0:
            print("   ⚠ Falta hardware para probar el analizador")
except Exception as e:
    print(f"   ✗ Error: {e}")

# 7. Probar analizador
print("\n7️⃣  Prueba del Analizador:")
try:
    with app.app_context():
        from models.database_models import Hardware
        cpus = Hardware.get_hardware_by_tipo('CPU')
        gpus = Hardware.get_hardware_by_tipo('GPU')
        rams = Hardware.get_hardware_by_tipo('RAM')
        
        if cpus and gpus and rams:
            from controllers.hardware_analyzer import (
                calculate_system_score,
                analyze_game_compatibility,
                generate_recommendations
            )
            from utils.bottleneck_detector import BottleneckDetector
            
            cpu, gpu, ram = cpus[0], gpus[0], rams[0]
            
            score = calculate_system_score(cpu, gpu, ram)
            print(f"   ✓ Puntuación calculada: {score['total']}")
            
            bottlenecks = BottleneckDetector.detect(cpu, gpu, ram)
            print(f"   ✓ Cuello de botella analizado: {bottlenecks['type']}")
            
            games = analyze_game_compatibility(cpu, gpu, ram)
            total = sum(len(v) for v in games.values())
            print(f"   ✓ Juegos analizados: {total}")
            
            recs = generate_recommendations(bottlenecks, score)
            print(f"   ✓ Recomendaciones generadas: {len(recs)}")
        else:
            print("   ⚠ No hay hardware suficiente para probar")
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("✅ DIAGNÓSTICO COMPLETADO")
print("=" * 60)
