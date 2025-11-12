"""
Controlador de diagnóstico temporal
Para verificar el estado del sistema
"""
from flask import Blueprint, render_template_string, jsonify
from flask_login import login_required, current_user
from database import db
from models.database_models import Order, User, Invoice
from sqlalchemy import inspect

diagnostico_bp = Blueprint('diagnostico', __name__)

@diagnostico_bp.route('/diagnostico')
@login_required
def diagnostico():
    """Página de diagnóstico del sistema"""
    
    # Verificar tablas
    inspector = inspect(db.engine)
    tablas = inspector.get_table_names()
    
    # Contar registros
    try:
        total_users = User.query.count()
    except:
        total_users = "Error"
    
    try:
        total_orders = Order.query.count()
    except:
        total_orders = "Error"
    
    try:
        total_invoices = Invoice.query.count()
    except:
        total_invoices = "Error"
    
    # Órdenes del usuario actual
    try:
        user_orders = Order.query.filter_by(user_id=current_user.id).count()
    except:
        user_orders = "Error"
    
    # Verificar columnas de invoices
    try:
        invoice_columns = [col['name'] for col in inspector.get_columns('invoices')]
    except:
        invoice_columns = ["Error obteniendo columnas"]
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Diagnóstico del Sistema</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.4.0/css/all.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <h1>🔍 Diagnóstico del Sistema</h1>
            <hr>
            
            <h3>Test de Iconos</h3>
            <div class="mb-4">
                <i class="fas fa-shopping-cart fa-3x text-primary"></i>
                <i class="fas fa-search fa-3x text-success ms-3"></i>
                <i class="fas fa-user fa-3x text-info ms-3"></i>
                <i class="fas fa-heart fa-3x text-danger ms-3"></i>
                <p class="mt-2">Si ves los iconos arriba, Font Awesome está funcionando ✅</p>
            </div>
            
            <h3>Base de Datos</h3>
            <table class="table table-bordered">
                <tr>
                    <th>Tablas en BD</th>
                    <td>{len(tablas)}</td>
                </tr>
                <tr>
                    <th>Lista de Tablas</th>
                    <td>{', '.join(tablas)}</td>
                </tr>
                <tr>
                    <th>Total Usuarios</th>
                    <td>{total_users}</td>
                </tr>
                <tr>
                    <th>Total Órdenes</th>
                    <td>{total_orders}</td>
                </tr>
                <tr>
                    <th>Total Facturas</th>
                    <td>{total_invoices}</td>
                </tr>
                <tr>
                    <th>Órdenes del Usuario Actual</th>
                    <td>{user_orders}</td>
                </tr>
            </table>
            
            <h3>Columnas de Invoices</h3>
            <div class="alert alert-info">
                <strong>Columnas Colombianas:</strong>
                <ul>
                    <li>nit_receptor: {'✅' if 'nit_receptor' in invoice_columns else '❌'}</li>
                    <li>tipo_documento_receptor: {'✅' if 'tipo_documento_receptor' in invoice_columns else '❌'}</li>
                    <li>ciudad: {'✅' if 'ciudad' in invoice_columns else '❌'}</li>
                    <li>departamento: {'✅' if 'departamento' in invoice_columns else '❌'}</li>
                    <li>email_receptor: {'✅' if 'email_receptor' in invoice_columns else '❌'}</li>
                    <li>cufe: {'✅' if 'cufe' in invoice_columns else '❌'}</li>
                </ul>
            </div>
            
            <h3>Usuario Actual</h3>
            <table class="table table-bordered">
                <tr>
                    <th>Username</th>
                    <td>{current_user.username}</td>
                </tr>
                <tr>
                    <th>Email</th>
                    <td>{current_user.email}</td>
                </tr>
                <tr>
                    <th>ID</th>
                    <td>{current_user.id}</td>
                </tr>
            </table>
            
            <h3>Acciones</h3>
            <a href="/mis-ordenes" class="btn btn-primary">
                <i class="fas fa-shopping-bag"></i> Ir a Mis Órdenes
            </a>
            <a href="/" class="btn btn-secondary">
                <i class="fas fa-home"></i> Volver al Inicio
            </a>
        </div>
    </body>
    </html>
    """
    
    return render_template_string(html)

@diagnostico_bp.route('/diagnostico/json')
@login_required
def diagnostico_json():
    """Diagnóstico en formato JSON"""
    
    inspector = inspect(db.engine)
    
    try:
        invoice_columns = [col['name'] for col in inspector.get_columns('invoices')]
    except:
        invoice_columns = []
    
    return jsonify({
        'tablas': inspector.get_table_names(),
        'total_users': User.query.count(),
        'total_orders': Order.query.count(),
        'user_orders': Order.query.filter_by(user_id=current_user.id).count(),
        'invoice_columns': invoice_columns,
        'columnas_colombia': {
            'nit_receptor': 'nit_receptor' in invoice_columns,
            'tipo_documento_receptor': 'tipo_documento_receptor' in invoice_columns,
            'ciudad': 'ciudad' in invoice_columns,
            'departamento': 'departamento' in invoice_columns,
            'email_receptor': 'email_receptor' in invoice_columns,
            'cufe': 'cufe' in invoice_columns
        }
    })
