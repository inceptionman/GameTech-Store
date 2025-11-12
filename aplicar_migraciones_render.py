"""
Script para aplicar migraciones en Render
Ejecutar desde Render Shell: python aplicar_migraciones_render.py
"""
from app import app, db
from sqlalchemy import text, inspect

def aplicar_migraciones():
    """Aplicar migraciones de facturas a Colombia"""
    with app.app_context():
        print("🇨🇴 Aplicando migraciones para facturas colombianas...")
        print()
        
        try:
            inspector = inspect(db.engine)
            
            # Verificar si la tabla invoices existe
            if 'invoices' not in inspector.get_table_names():
                print("⚠️  Tabla invoices no existe. Creando tablas...")
                db.create_all()
                print("✅ Tablas creadas")
                return
            
            # Obtener columnas existentes
            existing_columns = [col['name'] for col in inspector.get_columns('invoices')]
            print(f"📊 Columnas existentes: {len(existing_columns)}")
            
            # Lista de columnas a agregar
            migrations = [
                ("nit_receptor", "VARCHAR(20)"),
                ("tipo_documento_receptor", "VARCHAR(10) DEFAULT '31'"),
                ("ciudad", "VARCHAR(100)"),
                ("departamento", "VARCHAR(100)"),
                ("telefono", "VARCHAR(20)"),
                ("email_receptor", "VARCHAR(200)"),
                ("nit_emisor", "VARCHAR(20) DEFAULT '900123456-7'"),
                ("razon_social_emisor", "VARCHAR(200) DEFAULT 'GameTech Store SAS'"),
                ("regimen_emisor", "VARCHAR(50) DEFAULT 'Responsable de IVA'"),
                ("cufe", "TEXT"),
                ("qr_code", "TEXT"),
                ("fecha_validacion_dian", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
            ]
            
            print()
            print("🔧 Aplicando migraciones...")
            print()
            
            # Aplicar migraciones
            columnas_agregadas = 0
            for column_name, column_type in migrations:
                if column_name not in existing_columns:
                    try:
                        sql = f"ALTER TABLE invoices ADD COLUMN {column_name} {column_type}"
                        db.session.execute(text(sql))
                        db.session.commit()
                        print(f"  ✅ Agregada columna: {column_name}")
                        columnas_agregadas += 1
                    except Exception as e:
                        db.session.rollback()
                        print(f"  ❌ Error agregando {column_name}: {str(e)}")
                else:
                    print(f"  ⏭️  Columna {column_name} ya existe")
            
            print()
            print("📦 Migrando datos existentes...")
            print()
            
            # Migrar datos existentes
            try:
                # Copiar RFC a NIT si existe
                if 'rfc_receptor' in existing_columns and 'nit_receptor' in [col['name'] for col in inspector.get_columns('invoices')]:
                    db.session.execute(text("""
                        UPDATE invoices 
                        SET nit_receptor = rfc_receptor 
                        WHERE nit_receptor IS NULL AND rfc_receptor IS NOT NULL
                    """))
                    db.session.commit()
                    print("  ✅ Datos de RFC copiados a NIT")
            except Exception as e:
                db.session.rollback()
                print(f"  ⚠️  Error copiando RFC: {str(e)}")
            
            # Copiar email de usuarios
            try:
                db.session.execute(text("""
                    UPDATE invoices 
                    SET email_receptor = (
                        SELECT email FROM users WHERE users.id = invoices.user_id
                    )
                    WHERE email_receptor IS NULL
                """))
                db.session.commit()
                print("  ✅ Emails de usuarios actualizados")
            except Exception as e:
                db.session.rollback()
                print(f"  ⚠️  Error actualizando emails: {str(e)}")
            
            # Actualizar razón social del emisor
            try:
                if 'razon_social_emisor' in [col['name'] for col in inspector.get_columns('invoices')]:
                    db.session.execute(text("""
                        UPDATE invoices 
                        SET razon_social_emisor = 'GameTech Store SAS'
                        WHERE razon_social_emisor IS NULL OR razon_social_emisor LIKE '%SA de CV%'
                    """))
                    db.session.commit()
                    print("  ✅ Razón social actualizada a Colombia")
            except Exception as e:
                db.session.rollback()
                print(f"  ⚠️  Error actualizando razón social: {str(e)}")
            
            print()
            print("=" * 60)
            print("✅ MIGRACIONES COMPLETADAS EXITOSAMENTE!")
            print("=" * 60)
            print()
            print(f"📊 Columnas agregadas: {columnas_agregadas}")
            
            # Mostrar resumen
            result = db.session.execute(text("SELECT COUNT(*) FROM invoices"))
            total = result.scalar()
            print(f"📊 Total de facturas en BD: {total}")
            
        except Exception as e:
            db.session.rollback()
            print()
            print("=" * 60)
            print("❌ ERROR EN MIGRACIONES")
            print("=" * 60)
            print(f"Error: {str(e)}")
            import traceback
            print(traceback.format_exc())

if __name__ == '__main__':
    print("=" * 60)
    print("APLICAR MIGRACIONES EN RENDER")
    print("=" * 60)
    print()
    aplicar_migraciones()
