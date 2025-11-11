#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para inicializar la base de datos SQLite de forma segura
"""
import os
import sys
from pathlib import Path

# Crear la carpeta 'instance' si no existe
instance_dir = Path('instance')
instance_dir.mkdir(exist_ok=True)
print(f"✓ Carpeta 'instance' lista en: {instance_dir.absolute()}")

# Ahora importar la aplicación
from app import app, db

print("\n📊 Inicializando Base de Datos...")
with app.app_context():
    try:
        # Crear todas las tablas
        db.create_all()
        print("✓ Tablas creadas exitosamente")
        
        # Verificar conexión
        from sqlalchemy import text
        result = db.session.execute(text("SELECT 1"))
        print("✓ Conexión a BD verificada")
        
        # Mostrar información
        print(f"\n✓ DATABASE_URL: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
        print(f"✓ Archivo BD: {instance_dir / 'gametech_store.db'}")
        print(f"✓ Existe: {(instance_dir / 'gametech_store.db').exists()}")
        
        print("\n✅ Base de datos inicializada correctamente")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
