"""
Controlador de facturas electrónicas colombianas
Maneja la solicitud, generación y envío de facturas por correo
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify, current_app
from flask_login import login_required, current_user
from flask_mail import Message
from extensions import db
from models.database_models import Invoice, Order, User
from utils.invoice_generator_colombia import InvoiceGeneratorColombia as InvoiceGenerator
import os
from datetime import datetime

CART_ORDENES = 'cart.mis_ordenes'
VER_FACTURA = 'invoice.ver_factura'
SOLICITAR_FACTURA = 'invoice/solicitar_factura.html'

invoice_bp = Blueprint('invoice', __name__)

@invoice_bp.route('/factura/solicitar/<int:order_id>', methods=['GET', 'POST'])
@login_required
def solicitar_factura(order_id):
    """Solicitar factura para una orden"""
    order = Order.query.get_or_404(order_id)
    
    # Verificar que la orden pertenece al usuario
    if order.user_id != current_user.id:
        flash('No tienes permiso para facturar esta orden', 'danger')
        return redirect(url_for(CART_ORDENES))
    
    # Verificar si ya tiene factura
    existing_invoice = Invoice.query.filter_by(order_id=order.id).first()
    if existing_invoice:
        flash('Esta orden ya tiene una factura generada', 'info')
        return redirect(url_for(VER_FACTURA, invoice_id=existing_invoice.id))
    
    if request.method == 'POST':
        # Obtener datos fiscales del formulario (Colombia)
        nit = request.form.get('nit', '').strip()
        tipo_documento = request.form.get('tipo_documento', '31')  # 13=CC, 31=NIT
        razon_social = request.form.get('razon_social', '').strip()
        direccion_fiscal = request.form.get('direccion_fiscal', '').strip()
        ciudad = request.form.get('ciudad', '').strip()
        departamento = request.form.get('departamento', '').strip()
        codigo_postal = request.form.get('codigo_postal', '').strip()
        telefono = request.form.get('telefono', '').strip()
        forma_pago = request.form.get('forma_pago', 'Tarjeta de Crédito')
        
        # Validar datos requeridos
        if not nit or not razon_social:
            flash('NIT/CC y Razón Social son obligatorios', 'danger')
            return render_template(SOLICITAR_FACTURA, order=order, user=current_user)
        
        # Validar formato de NIT (flexible)
        if len(nit) < 6 or len(nit) > 20:
            flash('NIT/CC inválido. Debe tener entre 6 y 20 caracteres', 'danger')
            return render_template(SOLICITAR_FACTURA, order=order, user=current_user)
        
        try:
            current_app.logger.info(f'Iniciando generación de factura para orden {order.id}')
            
            # Guardar datos fiscales en el usuario si lo solicita
            if request.form.get('guardar_datos'):
                current_user.rfc = nit  # Guardar NIT en campo rfc
                current_user.razon_social = razon_social
                current_user.direccion_fiscal = direccion_fiscal
                current_user.codigo_postal = codigo_postal
                db.session.commit()
                current_app.logger.info('Datos fiscales guardados en usuario')
            
            # Crear factura con datos colombianos
            current_app.logger.info('Creando objeto Invoice')
            invoice = Invoice(
                order_id=order.id,
                user_id=current_user.id,
                folio=f'FE-{order.id:06d}',
                fecha_emision=datetime.now(),
                
                # Datos del receptor (Colombia)
                nit_receptor=nit,
                tipo_documento_receptor=tipo_documento,
                razon_social_receptor=razon_social,
                direccion_fiscal_receptor=direccion_fiscal,
                ciudad=ciudad,
                departamento=departamento,
                codigo_postal_receptor=codigo_postal,
                telefono=telefono,
                email_receptor=current_user.email,
                
                # Datos del emisor
                nit_emisor='900123456-7',
                razon_social_emisor='GameTech Store SAS',
                regimen_emisor='Responsable de IVA',
                
                # Montos
                subtotal=order.total / 1.19,  # IVA 19% Colombia
                iva=order.total - (order.total / 1.19),
                total=order.total,
                
                # Otros datos
                forma_pago=forma_pago,
                moneda='COP',
                status='valid'
            )
            
            # Generar CUFE (simplificado)
            import uuid
            invoice.cufe = str(uuid.uuid4())
            current_app.logger.info(f'CUFE generado: {invoice.cufe[:20]}...')
            
            db.session.add(invoice)
            
            # NO hacer flush aquí - esperar a que todo esté listo
            current_app.logger.info('Factura creada en memoria, preparando PDF...')
            
            # Generar PDF antes de commit
            try:
                # Usar un ID temporal para el nombre del archivo
                temp_id = f"{order.id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                pdf_filename = f'factura_{invoice.folio}_{temp_id}.pdf'
                pdf_dir = os.path.join('static', 'invoices', 'pdf')
                os.makedirs(pdf_dir, exist_ok=True)
                pdf_path = os.path.join(pdf_dir, pdf_filename)
                full_pdf_path = os.path.join(os.getcwd(), pdf_path)
                
                current_app.logger.info(f'Generando PDF en: {full_pdf_path}')
                InvoiceGenerator.generate_pdf(invoice, order, full_pdf_path)
                invoice.pdf_path = pdf_path
                
                current_app.logger.info(f'PDF generado exitosamente: {pdf_path}')
            except Exception as pdf_error:
                current_app.logger.error(f'Error generando PDF: {str(pdf_error)}')
                import traceback
                current_app.logger.error(traceback.format_exc())
                # Si falla el PDF, no guardar la factura
                raise Exception(f'Error al generar PDF: {str(pdf_error)}')
            
            # Solo hacer commit si todo salió bien
            db.session.commit()
            current_app.logger.info(f'Factura guardada exitosamente con ID: {invoice.id}')
            
            flash(f'¡Factura generada exitosamente! Folio: {invoice.folio}', 'success')
            return redirect(url_for(CART_ORDENES))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error generando factura: {str(e)}')
            current_app.logger.error(f'Traceback: {e.__class__.__name__}')
            import traceback
            current_app.logger.error(traceback.format_exc())
            flash(f'Error al generar la factura: {str(e)}', 'danger')
            return render_template(SOLICITAR_FACTURA, order=order, user=current_user)
    
    # GET - Mostrar formulario
    return render_template(SOLICITAR_FACTURA, order=order, user=current_user)

@invoice_bp.route('/factura/<int:invoice_id>')
@login_required
def ver_factura(invoice_id):
    """Ver detalles de una factura"""
    invoice = Invoice.query.get_or_404(invoice_id)
    
    # Verificar que la factura pertenece al usuario
    if invoice.user_id != current_user.id and not current_user.is_admin:
        flash('No tienes permiso para ver esta factura', 'danger')
        return redirect(url_for(CART_ORDENES))
    
    return render_template('invoice/ver_factura.html', invoice=invoice)

@invoice_bp.route('/factura/descargar/<int:invoice_id>')
@login_required
def descargar_factura(invoice_id):
    """Descargar PDF de factura"""
    invoice = Invoice.query.get_or_404(invoice_id)
    
    # Verificar permisos
    if invoice.user_id != current_user.id and not current_user.is_admin:
        flash('No tienes permiso para descargar esta factura', 'danger')
        return redirect(url_for(CART_ORDENES))
    
    # Verificar que existe el PDF
    if not invoice.pdf_path or not os.path.exists(invoice.pdf_path):
        flash('El PDF de la factura no está disponible', 'danger')
        return redirect(url_for(VER_FACTURA, invoice_id=invoice_id))
    
    return send_file(
        invoice.pdf_path,
        as_attachment=True,
        download_name=f'Factura_{invoice.folio}.pdf',
        mimetype='application/pdf'
    )

@invoice_bp.route('/mis-facturas')
@login_required
def mis_facturas():
    """Ver todas las facturas del usuario"""
    invoices = Invoice.query.filter_by(user_id=current_user.id).order_by(Invoice.created_at.desc()).all()
    return render_template('invoice/mis_facturas.html', invoices=invoices)

@invoice_bp.route('/factura/cancelar/<int:invoice_id>', methods=['POST'])
@login_required
def cancelar_factura(invoice_id):
    """Cancelar una factura (solo admin)"""
    if not current_user.is_admin:
        return jsonify({'error': 'No autorizado'}), 403
    
    invoice = Invoice.query.get_or_404(invoice_id)
    
    if invoice.status == 'cancelled':
        return jsonify({'error': 'La factura ya está cancelada'}), 400
    
    invoice.status = 'cancelled'
    invoice.fecha_cancelacion = datetime.now()
    db.session.commit()
    
    flash('Factura cancelada exitosamente', 'success')
    return redirect(url_for(VER_FACTURA, invoice_id=invoice_id))

# Funciones auxiliares
def generate_simple_seal(invoice):
    """Generar sello digital simplificado (para demostración)"""
    import hashlib
    
    # En producción, esto se haría con certificados digitales del SAT
    data = f"{invoice.uuid}{invoice.rfc_emisor}{invoice.rfc_receptor}{invoice.total}{invoice.fecha_emision}"
    return hashlib.sha256(data.encode()).hexdigest()

def generate_cadena_original(invoice):
    """Generar cadena original del comprobante"""
    # Formato simplificado
    return f"||{invoice.uuid}|{invoice.fecha_timbrado}|{invoice.rfc_emisor}|{invoice.rfc_receptor}|{invoice.total}||"
