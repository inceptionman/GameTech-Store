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

        if not _table_exists('invoices'):
            current_app.logger.info("⏭️  Tabla invoices no existe aún, saltando migraciones")
            return

        migrations_needed = _get_pending_migrations()
        if not migrations_needed:
            current_app.logger.info("✅ Todas las migraciones ya están aplicadas")
            return

        _apply_pending_migrations(migrations_needed)
        _migrate_existing_data()
        _show_migration_summary()

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"❌ Error en migraciones automáticas: {str(e)}")
        # No lanzar excepción para no impedir que la app inicie

def _table_exists(table_name):
    inspector = inspect(db.engine)
    return table_name in inspector.get_table_names()

def _get_pending_migrations():
    colombia_columns = {
        'nit_receptor': 'VARCHAR(30)',
        'tipo_documento_receptor': 'VARCHAR(4)',
        'razon_social_receptor': 'VARCHAR(128)',
        'ciudad': 'VARCHAR(128)',
        'departamento': 'VARCHAR(128)',
        'codigo_postal': 'VARCHAR(16)',
        'telefono': 'VARCHAR(64)',
        'email_receptor': 'VARCHAR(128)',
        'qr_code': 'TEXT',
        'fecha_validacion_dian': 'TIMESTAMP'
    }
    return [
        (col, typ)
        for col, typ in colombia_columns.items()
        if not check_column_exists('invoices', col)
    ]

def _apply_pending_migrations(migrations_needed):
    current_app.logger.info(f"📦 Aplicando {len(migrations_needed)} migraciones...")
    for column_name, column_type in migrations_needed:
        try:
            sql = f"ALTER TABLE invoices ADD COLUMN IF NOT EXISTS {column_name} {column_type}"
            db.session.execute(text(sql))
            current_app.logger.info(f"  ✅ Agregada columna: {column_name}")
        except Exception as e:
            _handle_migration_error(column_name, e)
    db.session.commit()
    current_app.logger.info("✅ Migraciones aplicadas exitosamente!")

def _handle_migration_error(column_name, error):
    msg = str(error).lower()
    if 'already exists' in msg or 'duplicate column' in msg:
        current_app.logger.info(f"  ⏭️  Columna {column_name} ya existe")
    else:
        current_app.logger.error(f"  ❌ Error agregando {column_name}: {str(error)}")

def _migrate_existing_data():
    try:
        if check_column_exists('invoices', 'rfc_receptor') and check_column_exists('invoices', 'nit_receptor'):
            db.session.execute(text("""
                UPDATE invoices 
                SET nit_receptor = rfc_receptor 
                WHERE nit_receptor IS NULL AND rfc_receptor IS NOT NULL
            """))
            current_app.logger.info("  ✅ Datos de RFC copiados a NIT")

        db.session.execute(text("""
            UPDATE invoices 
            SET email_receptor = (
                SELECT email FROM users WHERE users.id = invoices.user_id
            )
            WHERE email_receptor IS NULL
        """))
        current_app.logger.info("  ✅ Emails de usuarios actualizados")

        db.session.execute(text("""
            UPDATE invoices 
            SET razon_social_emisor = 'GameTech Store SAS'
            WHERE razon_social_emisor = 'GameTech Store SA de CV'
        """))
        current_app.logger.info("  ✅ Razón social actualizada a Colombia")

        if check_column_exists('invoices', 'fecha_timbrado'):
            db.session.execute(text("""
                UPDATE invoices 
                SET fecha_validacion_dian = fecha_timbrado
                WHERE fecha_validacion_dian IS NULL AND fecha_timbrado IS NOT NULL
            """))
            current_app.logger.info("  ✅ Fechas de validación actualizadas")
        db.session.commit()
    except Exception as e:
        current_app.logger.warning(f"  ⚠️  Error migrando datos: {str(e)}")

def _show_migration_summary():
    try:
        result = db.session.execute(text("SELECT COUNT(*) FROM invoices"))
        total = result.scalar()
        current_app.logger.info(f"📊 Total de facturas en BD: {total}")
    except Exception:
        pass

def init_auto_migrations(app):
    """Inicializar sistema de migraciones automáticas"""
    with app.app_context():
        run_auto_migrations()
