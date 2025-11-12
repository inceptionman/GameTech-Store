"""
Endpoint temporal para ejecutar migraciones
ELIMINAR DESPUÉS DE USAR
"""
from flask import Blueprint, jsonify
from extensions import db
from sqlalchemy import text, inspect
import os

migrate_bp = Blueprint('migrate', __name__)

# Clave secreta para proteger el endpoint
SECRET_KEY = os.environ.get('MIGRATION_SECRET', 'temp-migration-key-2024')

@migrate_bp.route('/limpiar-facturas-parciales/<secret>')
def limpiar_facturas_parciales(secret):
    """Eliminar facturas sin PDF (parciales)"""
    
    # Verificar clave secreta
    if secret != SECRET_KEY:
        return jsonify({'error': 'No autorizado'}), 403
    
    try:
        from models.database_models import Invoice
        
        # Buscar facturas sin PDF
        facturas_parciales = Invoice.query.filter(
            (Invoice.pdf_path == None) | (Invoice.pdf_path == '')
        ).all()
        
        if not facturas_parciales:
            return jsonify({
                'status': 'success',
                'message': 'No hay facturas parciales',
                'eliminadas': 0
            })
        
        # Eliminar facturas parciales
        ids_eliminados = []
        for factura in facturas_parciales:
            ids_eliminados.append({
                'id': factura.id,
                'order_id': factura.order_id,
                'folio': factura.folio
            })
            db.session.delete(factura)
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Facturas parciales eliminadas',
            'eliminadas': len(ids_eliminados),
            'facturas': ids_eliminados
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@migrate_bp.route('/ejecutar-migraciones/<secret>')
def ejecutar_migraciones(secret):
    """Ejecutar migraciones de base de datos"""
    
    # Verificar clave secreta
    if secret != SECRET_KEY:
        return jsonify({'error': 'No autorizado'}), 403
    
    resultados = []
    
    try:
        inspector = inspect(db.engine)
        
        # Verificar si la tabla invoices existe
        if 'invoices' not in inspector.get_table_names():
            db.create_all()
            return jsonify({
                'status': 'success',
                'message': 'Tablas creadas',
                'resultados': ['Tabla invoices creada']
            })
        
        # Obtener columnas existentes
        existing_columns = [col['name'] for col in inspector.get_columns('invoices')]
        resultados.append(f"Columnas existentes: {len(existing_columns)}")
        
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
        
        # Aplicar migraciones
        columnas_agregadas = 0
        for column_name, column_type in migrations:
            if column_name not in existing_columns:
                try:
                    sql = f"ALTER TABLE invoices ADD COLUMN {column_name} {column_type}"
                    db.session.execute(text(sql))
                    db.session.commit()
                    resultados.append(f"✅ Agregada: {column_name}")
                    columnas_agregadas += 1
                except Exception as e:
                    db.session.rollback()
                    resultados.append(f"❌ Error en {column_name}: {str(e)}")
            else:
                resultados.append(f"⏭️ Ya existe: {column_name}")
        
        # Migrar datos existentes
        try:
            # Copiar RFC a NIT si existe
            if 'rfc_receptor' in existing_columns:
                db.session.execute(text("""
                    UPDATE invoices 
                    SET nit_receptor = rfc_receptor 
                    WHERE nit_receptor IS NULL AND rfc_receptor IS NOT NULL
                """))
                db.session.commit()
                resultados.append("✅ RFC copiado a NIT")
        except Exception as e:
            db.session.rollback()
            resultados.append(f"⚠️ Error copiando RFC: {str(e)}")
        
        # Copiar emails
        try:
            db.session.execute(text("""
                UPDATE invoices 
                SET email_receptor = (
                    SELECT email FROM users WHERE users.id = invoices.user_id
                )
                WHERE email_receptor IS NULL
            """))
            db.session.commit()
            resultados.append("✅ Emails actualizados")
        except Exception as e:
            db.session.rollback()
            resultados.append(f"⚠️ Error actualizando emails: {str(e)}")
        
        # Contar facturas
        result = db.session.execute(text("SELECT COUNT(*) FROM invoices"))
        total = result.scalar()
        
        return jsonify({
            'status': 'success',
            'message': 'Migraciones completadas',
            'columnas_agregadas': columnas_agregadas,
            'total_facturas': total,
            'resultados': resultados
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e),
            'resultados': resultados
        }), 500
