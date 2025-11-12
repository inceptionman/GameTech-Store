"""
Ejecutar migraciones localmente y luego aplicar a producción
"""
from app import app, db
from sqlalchemy import text, inspect

def migrate_invoices_local():
    """Migrar tabla de facturas a formato colombiano - LOCAL"""
    
    with app.app_context():
        print("🇨🇴 Iniciando migración a sistema colombiano (LOCAL)...")
        
        try:
            inspector = inspect(db.engine)
            
            # Verificar si la tabla invoices existe
            if 'invoices' not in inspector.get_table_names():
                print("⚠️  Tabla invoices no existe. Creando tablas...")
                db.create_all()
                print("✅ Tablas creadas")
                return
            
            # Lista de columnas a agregar
            migrations = [
                ("nit_receptor", "VARCHAR(20)"),
                ("tipo_documento_receptor", "VARCHAR(10) DEFAULT '31'"),
                ("ciudad", "VARCHAR(100)"),
                ("departamento", "VARCHAR(100)"),
                ("telefono", "VARCHAR(20)"),
                ("email_receptor", "VARCHAR(200)"),
                ("nit_emisor", "VARCHAR(20) DEFAULT '900123456-7'"),
                ("regimen_emisor", "VARCHAR(50) DEFAULT 'Responsable de IVA'"),
                ("cufe", "TEXT"),
                ("qr_code", "TEXT"),
                ("fecha_validacion_dian", "TIMESTAMP"),
            ]
            
            # Obtener columnas existentes
            existing_columns = [col['name'] for col in inspector.get_columns('invoices')]
            
            # Aplicar migraciones
            for column_name, column_type in migrations:
                if column_name not in existing_columns:
                    try:
                        sql = f"ALTER TABLE invoices ADD COLUMN {column_name} {column_type}"
                        db.session.execute(text(sql))
                        db.session.commit()
                        print(f"  ✅ Agregada columna: {column_name}")
                    except Exception as e:
                        db.session.rollback()
                        print(f"  ❌ Error agregando {column_name}: {str(e)}")
                else:
                    print(f"  ⏭️  Columna {column_name} ya existe")
            
            # Migrar datos existentes
            print("\n📦 Migrando datos existentes...")
            
            # Copiar RFC a NIT
            try:
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
                db.session.execute(text("""
                    UPDATE invoices 
                    SET razon_social_emisor = 'GameTech Store SAS'
                    WHERE razon_social_emisor LIKE '%SA de CV%'
                """))
                db.session.commit()
                print("  ✅ Razón social actualizada a Colombia")
            except Exception as e:
                db.session.rollback()
                print(f"  ⚠️  Error actualizando razón social: {str(e)}")
            
            print("\n✅ Migración completada exitosamente!")
            
            # Mostrar resumen
            result = db.session.execute(text("SELECT COUNT(*) FROM invoices"))
            total = result.scalar()
            print(f"📊 Total de facturas en BD: {total}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error en migración: {str(e)}")
            raise

if __name__ == '__main__':
    print("=" * 60)
    print("MIGRACIÓN DE FACTURAS A FORMATO COLOMBIANO")
    print("=" * 60)
    print()
    
    respuesta = input("¿Ejecutar migración en base de datos LOCAL? (s/n): ")
    
    if respuesta.lower() == 's':
        migrate_invoices_local()
        print()
        print("=" * 60)
        print("MIGRACIÓN COMPLETADA")
        print("=" * 60)
        print()
        print("Ahora puedes:")
        print("1. Verificar los cambios localmente")
        print("2. Si todo está bien, hacer commit y push")
        print("3. Render aplicará los cambios automáticamente")
    else:
        print("Migración cancelada")
