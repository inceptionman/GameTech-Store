"""
Controlador de facturas electrónicas
Maneja la solicitud, generación y descarga de facturas
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_login import login_required, current_user
from database import db
from models.database_models import Invoice, Order, User
from utils.invoice_generator import InvoiceGenerator
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
    if hasattr(order, 'invoice') and order.invoice:
        flash('Esta orden ya tiene una factura generada', 'info')
        return redirect(url_for(VER_FACTURA, invoice_id=order.invoice.id))
    
    if request.method == 'POST':
        # Obtener datos fiscales del formulario
        rfc = request.form.get('rfc', '').strip().upper()
        razon_social = request.form.get('razon_social', '').strip()
        direccion_fiscal = request.form.get('direccion_fiscal', '').strip()
        codigo_postal = request.form.get('codigo_postal', '').strip()
        regimen_fiscal = request.form.get('regimen_fiscal', '').strip()
        uso_cfdi = request.form.get('uso_cfdi', 'G03')
        forma_pago = request.form.get('forma_pago', '03')
        
        # Validar datos requeridos
        if not rfc or not razon_social:
            flash('RFC y Razón Social son obligatorios', 'danger')
            return render_template(SOLICITAR_FACTURA, order=order, user=current_user)
        
        # Validar formato de RFC (simplificado)
        if len(rfc) not in [12, 13]:
            flash('RFC inválido. Debe tener 12 o 13 caracteres', 'danger')
            return render_template(SOLICITAR_FACTURA, order=order, user=current_user)
        
        try:
            # Guardar datos fiscales en el usuario si lo solicita
            if request.form.get('guardar_datos'):
                current_user.rfc = rfc
                current_user.razon_social = razon_social
                current_user.direccion_fiscal = direccion_fiscal
                current_user.codigo_postal = codigo_postal
                current_user.regimen_fiscal = regimen_fiscal
            
            # Crear factura
            user_fiscal_data = {
                'rfc': rfc,
                'razon_social': razon_social,
                'direccion_fiscal': direccion_fiscal,
                'codigo_postal': codigo_postal,
                'regimen_fiscal': regimen_fiscal,
                'uso_cfdi': uso_cfdi,
                'forma_pago': forma_pago
            }
            
            invoice = Invoice.create_from_order(order, user_fiscal_data)
            
            # Generar sello digital simplificado
            invoice.sello_digital = generate_simple_seal(invoice)
            invoice.cadena_original = generate_cadena_original(invoice)
            
            db.session.add(invoice)
            db.session.flush()  # Para obtener el ID
            
            # Generar PDF
            pdf_filename = f'factura_{invoice.folio}_{invoice.uuid[:8]}.pdf'
            pdf_path = os.path.join('static', 'invoices', 'pdf', pdf_filename)
            full_pdf_path = os.path.join(os.getcwd(), pdf_path)
            
            InvoiceGenerator.generate_pdf(invoice, order, full_pdf_path)
            
            invoice.pdf_path = pdf_path
            
            db.session.commit()
            
            flash(f'¡Factura generada exitosamente! Folio: {invoice.folio}', 'success')
            return redirect(url_for(VER_FACTURA, invoice_id=invoice.id))
            
        except Exception as e:
            db.session.rollback()
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
