"""
Sistema de migraciones automáticas
Se ejecuta al iniciar la aplicación
"""
from flask import current_app
from database import db
from sqlalchemy import text, inspect
import os

def check_column_exists(table_name, column_name):
    """Verificar si una columna existe en una tabla"""
    try:
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        return column_name in columns
    except Exception:
        return False

def run_auto_migrations():
    """Ejecutar migraciones automáticas al iniciar la app"""
    try:
        current_app.logger.info("🔄 Verificando migraciones necesarias...")
        
        # Verificar si la tabla invoices existe
        inspector = inspect(db.engine)
        if 'invoices' not in inspector.get_table_names():
            current_app.logger.info("⏭️  Tabla invoices no existe aún, saltando migraciones")
            return
        
        migrations_needed = []
        
        # Lista de columnas colombianas a agregar
        colombia_columns = {
            'nit_receptor': 'VARCHAR(20)',
            'tipo_documento_receptor': "VARCHAR(10) DEFAULT '31'",
            'ciudad': 'VARCHAR(100)',
            'departamento': 'VARCHAR(100)',
            'telefono': 'VARCHAR(20)',
            'email_receptor': 'VARCHAR(200)',
            'nit_emisor': "VARCHAR(20) DEFAULT '900123456-7'",
            'regimen_emisor': "VARCHAR(50) DEFAULT 'Responsable de IVA'",
            'cufe': 'TEXT',
            'qr_code': 'TEXT',
            'fecha_validacion_dian': 'TIMESTAMP'
        }
        
        # Verificar qué columnas faltan
        for column_name, column_type in colombia_columns.items():
            if not check_column_exists('invoices', column_name):
                migrations_needed.append((column_name, column_type))
        
        if not migrations_needed:
            current_app.logger.info("✅ Todas las migraciones ya están aplicadas")
            return
        
        current_app.logger.info(f"📦 Aplicando {len(migrations_needed)} migraciones...")
        
        # Aplicar migraciones
        for column_name, column_type in migrations_needed:
            try:
                sql = f"ALTER TABLE invoices ADD COLUMN IF NOT EXISTS {column_name} {column_type}"
                db.session.execute(text(sql))
                current_app.logger.info(f"  ✅ Agregada columna: {column_name}")
            except Exception as e:
                error_msg = str(e).lower()
                if 'already exists' in error_msg or 'duplicate column' in error_msg:
                    current_app.logger.info(f"  ⏭️  Columna {column_name} ya existe")
                else:
                    current_app.logger.error(f"  ❌ Error agregando {column_name}: {str(e)}")
        
        # Migrar datos existentes
        try:
            # Copiar RFC a NIT si existe
            if check_column_exists('invoices', 'rfc_receptor') and check_column_exists('invoices', 'nit_receptor'):
                db.session.execute(text("""
                    UPDATE invoices 
                    SET nit_receptor = rfc_receptor 
                    WHERE nit_receptor IS NULL AND rfc_receptor IS NOT NULL
                """))
                current_app.logger.info("  ✅ Datos de RFC copiados a NIT")
            
            # Copiar email de usuarios
            db.session.execute(text("""
                UPDATE invoices 
                SET email_receptor = (
                    SELECT email FROM users WHERE users.id = invoices.user_id
                )
                WHERE email_receptor IS NULL
            """))
            current_app.logger.info("  ✅ Emails de usuarios actualizados")
            
            # Actualizar razón social del emisor
            db.session.execute(text("""
                UPDATE invoices 
                SET razon_social_emisor = 'GameTech Store SAS'
                WHERE razon_social_emisor = 'GameTech Store SA de CV' 
                   OR razon_social_emisor = 'GameTech Store SA de CV'
            """))
            current_app.logger.info("  ✅ Razón social actualizada a Colombia")
            
            # Actualizar fecha_validacion_dian
            if check_column_exists('invoices', 'fecha_timbrado'):
                db.session.execute(text("""
                    UPDATE invoices 
                    SET fecha_validacion_dian = fecha_timbrado
                    WHERE fecha_validacion_dian IS NULL AND fecha_timbrado IS NOT NULL
                """))
                current_app.logger.info("  ✅ Fechas de validación actualizadas")
            
        except Exception as e:
            current_app.logger.warning(f"  ⚠️  Error migrando datos: {str(e)}")
        
        # Commit de todas las migraciones
        db.session.commit()
        current_app.logger.info("✅ Migraciones aplicadas exitosamente!")
        
        # Mostrar resumen
        try:
            result = db.session.execute(text("SELECT COUNT(*) FROM invoices"))
            total = result.scalar()
            current_app.logger.info(f"📊 Total de facturas en BD: {total}")
        except Exception:
            pass
            
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"❌ Error en migraciones automáticas: {str(e)}")
        # No lanzar excepción para no impedir que la app inicie

def init_auto_migrations(app):
    """Inicializar sistema de migraciones automáticas"""
    with app.app_context():
        run_auto_migrations()
