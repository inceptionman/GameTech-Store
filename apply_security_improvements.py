"""
Script para aplicar mejoras de seguridad críticas
Ejecutar: python apply_security_improvements.py
"""
import os
import sys

def check_and_install_packages():
    """Verificar e instalar paquetes necesarios"""
    packages = [
        'Flask-Limiter',
        'sentry-sdk[flask]'
    ]
    
    print("📦 Instalando paquetes de seguridad...")
    for package in packages:
        os.system(f'pip install {package}')
    print("✅ Paquetes instalados\n")

def update_requirements():
    """Actualizar requirements.txt con nuevas dependencias"""
    print("📝 Actualizando requirements.txt...")
    
    new_packages = """
# Seguridad y Rate Limiting
Flask-Limiter==3.8.0

# Monitoreo y Error Tracking
sentry-sdk==2.19.2
"""
    
    with open('requirements.txt', 'a', encoding='utf-8') as f:
        f.write(new_packages)
    
    print("✅ requirements.txt actualizado\n")

def create_limiter_config():
    """Crear configuración de rate limiting"""
    print("🔒 Creando configuración de Rate Limiting...")
    
    limiter_code = """\"\"\"
Configuración de Rate Limiting
\"\"\"
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

def init_limiter(app):
    \"\"\"Inicializar rate limiter\"\"\"
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"
    )
    return limiter

# Decoradores personalizados
def rate_limit_login():
    return "5 per minute"

def rate_limit_register():
    return "3 per hour"

def rate_limit_api():
    return "100 per hour"
"""
    
    with open('utils/rate_limiter.py', 'w', encoding='utf-8') as f:
        f.write(limiter_code)
    
    print("✅ Rate limiter configurado en utils/rate_limiter.py\n")

def create_sentry_config():
    """Crear configuración de Sentry"""
    print("📊 Creando configuración de Sentry...")
    
    sentry_code = """\"\"\"
Configuración de Sentry para monitoreo de errores
\"\"\"
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
import os

def init_sentry(app):
    \"\"\"Inicializar Sentry\"\"\"
    sentry_dsn = os.environ.get('SENTRY_DSN')
    
    if sentry_dsn and app.config.get('FLASK_ENV') == 'production':
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[FlaskIntegration()],
            traces_sample_rate=1.0,
            environment=app.config.get('FLASK_ENV', 'development'),
            release=os.environ.get('APP_VERSION', '1.0.0')
        )
        app.logger.info('Sentry inicializado correctamente')
    else:
        app.logger.info('Sentry no configurado (modo desarrollo)')
"""
    
    with open('utils/sentry_config.py', 'w', encoding='utf-8') as f:
        f.write(sentry_code)
    
    print("✅ Sentry configurado en utils/sentry_config.py\n")

def create_security_headers():
    """Crear middleware para headers de seguridad"""
    print("🛡️ Creando headers de seguridad...")
    
    security_code = """\"\"\"
Middleware para headers de seguridad
\"\"\"
from flask import make_response

def add_security_headers(app):
    \"\"\"Agregar headers de seguridad a todas las respuestas\"\"\"
    
    @app.after_request
    def set_security_headers(response):
        # Prevenir clickjacking
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        
        # Prevenir MIME type sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # XSS Protection
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Content Security Policy
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net; "
            "img-src 'self' data: https:; "
        )
        
        # HSTS (solo en producción)
        if app.config.get('FLASK_ENV') == 'production':
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response
    
    app.logger.info('Headers de seguridad configurados')
"""
    
    with open('utils/security_headers.py', 'w', encoding='utf-8') as f:
        f.write(security_code)
    
    print("✅ Headers de seguridad configurados en utils/security_headers.py\n")

def create_env_example_update():
    """Actualizar .env.example con nuevas variables"""
    print("📄 Actualizando .env.example...")
    
    new_vars = """
# Monitoreo y Seguridad
SENTRY_DSN=tu_sentry_dsn_aqui
APP_VERSION=1.0.0

# Rate Limiting (opcional, por defecto usa memoria)
RATELIMIT_STORAGE_URL=redis://localhost:6379
"""
    
    with open('.env.example', 'a', encoding='utf-8') as f:
        f.write(new_vars)
    
    print("✅ .env.example actualizado\n")

def create_integration_guide():
    """Crear guía de integración"""
    print("📚 Creando guía de integración...")
    
    guide = """# 🔒 Guía de Integración de Mejoras de Seguridad

## Cambios Aplicados

1. ✅ Rate Limiting configurado
2. ✅ Sentry para monitoreo de errores
3. ✅ Headers de seguridad
4. ✅ Dependencias actualizadas

## Integración en app.py

Agrega estas líneas a tu `app.py`:

```python
# Después de crear la app
from utils.rate_limiter import init_limiter
from utils.sentry_config import init_sentry
from utils.security_headers import add_security_headers

# Inicializar seguridad
limiter = init_limiter(app)
init_sentry(app)
add_security_headers(app)
```

## Uso de Rate Limiting en Rutas

En tus controladores (ej: `controllers/auth.py`):

```python
from utils.rate_limiter import rate_limit_login, rate_limit_register

@auth_bp.route('/login', methods=['POST'])
@limiter.limit(rate_limit_login)
def login():
    # Tu código aquí
    pass

@auth_bp.route('/registro', methods=['POST'])
@limiter.limit(rate_limit_register)
def registro():
    # Tu código aquí
    pass
```

## Configurar Sentry (Opcional)

1. Crea una cuenta en https://sentry.io
2. Crea un nuevo proyecto
3. Copia el DSN
4. Agrégalo a tu `.env`:
   ```
   SENTRY_DSN=https://tu-dsn@sentry.io/proyecto
   ```

## Habilitar CSRF Protection

En `app.py`, descomenta:

```python
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)
```

## Testing

Prueba el rate limiting:

```bash
# Hacer múltiples requests rápidos
for i in {1..10}; do curl http://localhost:5000/login; done
```

Deberías ver un error 429 (Too Many Requests) después de 5 intentos.

## Próximos Pasos

1. Revisar logs en `logs/app.log`
2. Configurar Sentry en producción
3. Ajustar límites de rate limiting según necesidad
4. Implementar tests de seguridad
"""
    
    with open('INTEGRACION_SEGURIDAD.md', 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print("✅ Guía creada en INTEGRACION_SEGURIDAD.md\n")

def main():
    """Ejecutar todas las mejoras"""
    print("="*60)
    print("🚀 APLICANDO MEJORAS DE SEGURIDAD")
    print("="*60)
    print()
    
    try:
        check_and_install_packages()
        update_requirements()
        create_limiter_config()
        create_sentry_config()
        create_security_headers()
        create_env_example_update()
        create_integration_guide()
        
        print("="*60)
        print("✅ MEJORAS APLICADAS EXITOSAMENTE")
        print("="*60)
        print()
        print("📋 Próximos pasos:")
        print("1. Revisa INTEGRACION_SEGURIDAD.md")
        print("2. Integra los cambios en app.py")
        print("3. Prueba el rate limiting")
        print("4. Configura Sentry (opcional)")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
