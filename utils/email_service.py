"""
Servicio de envío de correos electrónicos
"""
from flask_mail import Mail, Message
from flask import render_template, url_for
import secrets
from datetime import datetime, timedelta

mail = Mail()

def init_mail(app):
    """Inicializar Flask-Mail con la aplicación"""
    mail.init_app(app)

def generate_verification_token():
    """Generar un token único para verificación"""
    return secrets.token_urlsafe(32)

def send_verification_email(user_email, username, token):
    """
    Enviar correo de verificación al usuario
    
    Args:
        user_email: Email del usuario
        username: Nombre de usuario
        token: Token de verificación
    """
    try:
        # Crear URL de verificación
        verification_url = url_for('auth.verify_email', token=token, _external=True)
        
        # Crear mensaje
        msg = Message(
            subject='Verifica tu cuenta en GameTech Store',
            sender=('GameTech Store', 'noreply@gametechstore.com'),
            recipients=[user_email]
        )
        
        # Cuerpo del correo en HTML
        msg.html = render_template(
            'emails/verify_email.html',
            username=username,
            verification_url=verification_url
        )
        
        # Cuerpo del correo en texto plano (fallback)
        msg.body = f"""
Hola {username},

¡Bienvenido a GameTech Store!

Para completar tu registro, por favor verifica tu correo electrónico haciendo clic en el siguiente enlace:

{verification_url}

Este enlace expirará en 24 horas.

Si no creaste esta cuenta, puedes ignorar este correo.

Saludos,
El equipo de GameTech Store
        """
        
        # Enviar correo
        mail.send(msg)
        return True
        
    except Exception as e:
        print(f"Error al enviar correo de verificación: {e}")
        return False

def send_welcome_email(user_email, username):
    """
    Enviar correo de bienvenida después de verificar la cuenta
    
    Args:
        user_email: Email del usuario
        username: Nombre de usuario
    """
    try:
        msg = Message(
            subject='¡Bienvenido a GameTech Store!',
            sender=('GameTech Store', 'noreply@gametechstore.com'),
            recipients=[user_email]
        )
        
        msg.html = render_template(
            'emails/welcome.html',
            username=username
        )
        
        msg.body = f"""
Hola {username},

¡Tu cuenta ha sido verificada exitosamente!

Ya puedes disfrutar de todas las funcionalidades de GameTech Store:
- Comprar juegos y hardware gaming
- Analizar la compatibilidad de tu PC
- Solicitar facturas electrónicas
- Y mucho más...

¡Gracias por unirte a nuestra comunidad!

Saludos,
El equipo de GameTech Store
        """
        
        mail.send(msg)
        return True
        
    except Exception as e:
        print(f"Error al enviar correo de bienvenida: {e}")
        return False

def get_token_expiry():
    """Obtener fecha de expiración del token (24 horas)"""
    return datetime.now() + timedelta(hours=24)
