"""
Controlador de facturas electrónicas
Maneja la solicitud, generación y descarga de facturas
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify, current_app
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
    
    if not _user_can_invoice(order):
        return _forbidden_redirect()
        
    existing_invoice = Invoice.query.filter_by(order_id=order.id).first()
    if existing_invoice:
        return _already_invoiced_redirect(existing_invoice)

    if request.method == 'POST':
        return _handle_invoice_form(order)
        
    # GET - Mostrar formulario
    return render_template(SOLICITAR_FACTURA, order=order, user=current_user)


def _user_can_invoice(order):
    return order.user_id == current_user.id

def _forbidden_redirect():
    flash('No tienes permiso para facturar esta orden', 'danger')
    return redirect(url_for(CART_ORDENES))

def _already_invoiced_redirect(existing_invoice):
    flash('Esta orden ya tiene una factura generada', 'info')
    return redirect(url_for(VER_FACTURA, invoice_id=existing_invoice.id))

def _handle_invoice_form(order):
    nit, razon_social, error = _get_and_validate_invoice_fields()
    if error:
        flash(error, 'danger')
        return render_template(SOLICITAR_FACTURA, order=order, user=current_user)
    
    try:
        _maybe_save_user_fiscal_data(nit, razon_social)
        invoice = _build_invoice(order, nit, razon_social)
        _generate_invoice_pdf(invoice, order)
        db.session.add(invoice)
        db.session.commit()
        flash(f'¡Factura generada exitosamente! Folio: {invoice.folio}', 'success')
        return redirect(url_for(CART_ORDENES))
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error generando factura: {str(e)}')
        flash(f'Error al generar la factura: {str(e)}', 'danger')
        return render_template(SOLICITAR_FACTURA, order=order, user=current_user)

def _get_and_validate_invoice_fields():
    nit = request.form.get('nit', '').strip()
    razon_social = request.form.get('razon_social', '').strip()
    # ... obtener otros campos como antes
    if not nit or not razon_social:
        return nit, razon_social, 'NIT/CC y Razón Social son obligatorios'
    if len(nit) < 6 or len(nit) > 20:
        return nit, razon_social, 'NIT/CC inválido. Debe tener entre 6 y 20 caracteres'
    return nit, razon_social, None

def _maybe_save_user_fiscal_data(nit, razon_social):
    if request.form.get('guardar_datos'):
        # Guardar datos fiscales en el usuario
        current_user.rfc = nit
        current_user.razon_social = razon_social
        current_user.direccion_fiscal = request.form.get('direccion_fiscal', '').strip()
        current_user.codigo_postal = request.form.get('codigo_postal', '').strip()
        db.session.commit()
        current_app.logger.info('Datos fiscales guardados en usuario')

def _build_invoice(order, nit, razon_social):
    # ... construir y devolver el objeto Invoice en base a los datos y a tu lógica actual
    # Devuelve el objeto Invoice (omitir detalles por brevedad)
    pass

def _generate_invoice_pdf(invoice, order):
    # ... tu lógica actual de generación de PDF, pero sin tanto nesting
    pass

    
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
