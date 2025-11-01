
"""
Controlador de autenticación
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from extensions import db, mail
from models.database_models import User
import re
import secrets
from datetime import datetime, timedelta, timezone

AUTH_REGISTRO = 'auth/registro.html'
RESET_PASSWORD = 'auth/reset_password.html'
AUTH_LOGIN = 'auth.login'

# Patrones de validación de contraseña
PATTERN_LOWERCASE = r'[a-z]'
PATTERN_UPPERCASE = r'[A-Z]'
PATTERN_DIGIT = r'\d'
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    """Página de registro de usuarios"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        error = validar_datos_registro(username, email, password, confirm_password)
        if error:
            flash(error, 'danger')
            return render_template(AUTH_REGISTRO)

        # Verificar si usuario o email ya existen
        if User.query.filter_by(username=username).first():
            flash('El nombre de usuario ya está en uso.', 'danger')
            return render_template(AUTH_REGISTRO)

        if User.query.filter_by(email=email).first():
            flash('El email ya está registrado.', 'danger')
            return render_template(AUTH_REGISTRO)

        # Crear nuevo usuario con contraseña cifrada
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('¡Registro exitoso! Ahora puedes iniciar sesión', 'success')
        return redirect(url_for(AUTH_LOGIN))
    
    return render_template(AUTH_REGISTRO)

def validar_datos_registro(username, email, password, confirm_password):
    """Valida los datos del formulario de registro y devuelve un mensaje de error o None."""
    if not username or not email or not password:
        return 'Todos los campos son obligatorios'

    if password != confirm_password:
        return 'Las contraseñas no coinciden'

    if len(password) < 8:
        return 'La contraseña debe tener al menos 8 caracteres'

    if not re.search(PATTERN_UPPERCASE, password):
        return 'La contraseña debe contener al menos una letra mayúscula'

    if not re.search(PATTERN_LOWERCASE, password):
        return 'La contraseña debe contener al menos una letra minúscula'

    if not re.search(PATTERN_DIGIT, password):
        return 'La contraseña debe contener al menos un número'

    return None
        

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de inicio de sesión"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        if not username or not password:
            flash('Por favor ingresa usuario y contraseña', 'danger')
            return render_template('auth/login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            # Login exitoso
            login_user(user, remember=remember)
            flash(f'¡Bienvenido {user.username}!', 'success')
            
            # Redirigir a la página solicitada o al inicio
            next_page = request.args.get('next')
            return redirect(url_for(next_page)) if next_page else redirect(url_for('index'))
        else:
            # Login fallido
            flash('Usuario o contraseña incorrectos', 'danger')
            # Aquí podrías implementar un contador de intentos fallidos
            # Para simplicidad, solo mostramos el mensaje
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Cerrar sesión"""
    logout_user()
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('index'))

@auth_bp.route('/perfil')
@login_required
def perfil():
    """Página de perfil del usuario"""
    return render_template('auth/perfil.html', user=current_user)

@auth_bp.route('/perfil/editar', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    """Editar perfil del usuario"""
    if request.method == 'POST':
        email = request.form.get('email')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        
        # Actualizar email
        if email and email != current_user.email:
            if User.query.filter_by(email=email).first():
                flash('El email ya está en uso', 'danger')
            else:
                current_user.email = email
                flash('Email actualizado correctamente', 'success')
        
        # Cambiar contraseña
        if current_password and new_password:
            if current_user.check_password(current_password):
                if len(new_password) >= 8 and re.search(PATTERN_UPPERCASE, new_password) and re.search(PATTERN_LOWERCASE, new_password) and re.search(PATTERN_DIGIT, new_password):
                    current_user.set_password(new_password)
                    flash('Contraseña actualizada correctamente', 'success')
                else:
                    flash('La nueva contraseña debe tener al menos 8 caracteres, con mayúscula, minúscula y número', 'danger')
            else:
                flash('Contraseña actual incorrecta', 'danger')
        
        db.session.commit()
        return redirect(url_for('auth.perfil'))
    
    return render_template('auth/editar_perfil.html', user=current_user)

@auth_bp.route('/recuperar-password', methods=['GET', 'POST'])
def recuperar_password():
    """Página para solicitar recuperación de contraseña"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Generar token único
            token = secrets.token_urlsafe(32)
            user.reset_token = token
            # Usar timezone aware datetime
            user.reset_token_expiry = datetime.now(timezone.utc) + timedelta(hours=1)
            db.session.commit()
            
            # Enviar email
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            msg = Message('Recuperación de Contraseña',
                        recipients=[user.email])
            msg.body = f'''Para restablecer tu contraseña, visita el siguiente enlace:

{reset_url}

Si no solicitaste un restablecimiento de contraseña, puedes ignorar este mensaje.

El enlace expirará en 1 hora.
'''
            mail.send(msg)
            
            flash('Se ha enviado un email con las instrucciones para recuperar tu contraseña', 'info')
            return redirect(url_for(AUTH_LOGIN))
        
        flash('Si el email existe en nuestra base de datos, recibirás las instrucciones para recuperar tu contraseña', 'info')
        return redirect(url_for(AUTH_LOGIN))
    
    return render_template('auth/recuperar_password.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Página para establecer nueva contraseña"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # Intentar recuperar el usuario con reintentos
    user = None
    for _ in range(3):  # Intentar hasta 3 veces
        try:
            user = User.query.filter_by(reset_token=token).first()
            if user:
                break
        except Exception:
            db.session.rollback()  # Rollback en caso de error
            continue
    
    if user is None:
        flash('Error al conectar con la base de datos o token inválido. Por favor, solicita un nuevo enlace.', 'danger')
        return redirect(url_for(AUTH_LOGIN))
    
    if user.reset_token_expiry < datetime.now(timezone.utc):
        flash('El enlace de recuperación ha expirado. Por favor, solicita uno nuevo.', 'danger')
        return redirect(url_for(AUTH_LOGIN))

    if request.method == 'POST':
        try:
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            
            # Lista para almacenar todos los errores encontrados
            errors = []
            
            # Validar que las contraseñas coincidan
            if password != confirm_password:
                errors.append('Las contraseñas no coinciden')
                
            # Validar longitud mínima
            if len(password) < 8:
                errors.append('La contraseña debe tener al menos 8 caracteres')
                
            # Validar mayúscula
            if not re.search(PATTERN_UPPERCASE, password):
                errors.append('La contraseña debe contener al menos una letra mayúscula')
                
            # Validar minúscula
            if not re.search(PATTERN_LOWERCASE, password):
                errors.append('La contraseña debe contener al menos una letra minúscula')
                
            # Validar número
            if not re.search(PATTERN_DIGIT, password):
                errors.append('La contraseña debe contener al menos un número')
            
            # Si hay errores, mostrarlos todos juntos
            if errors:
                for error in errors:
                    flash(error, 'danger')
                return render_template(RESET_PASSWORD)
            
            # Si pasa todas las validaciones, actualizar la contraseña
            user.set_password(password)
            user.reset_token = None
            user.reset_token_expiry = None
            db.session.commit()
            
            flash('Tu contraseña ha sido actualizada correctamente. Ahora puedes iniciar sesión', 'success')
            return redirect(url_for(AUTH_LOGIN))
            
        except Exception:
            db.session.rollback()
            flash('Ocurrió un error al actualizar la contraseña. Por favor, intenta nuevamente.', 'danger')
            return render_template(RESET_PASSWORD)

    # Si es método GET o hubo error en el POST
    return render_template(RESET_PASSWORD)
