# 📧 Configuración de Verificación por Correo Electrónico

## 🎯 Resumen
Se ha implementado un sistema de verificación en 2 pasos mediante correo electrónico para nuevos usuarios.

## 🔧 Configuración Requerida

### Paso 1: Configurar Gmail

1. **Ir a tu cuenta de Google**
   - Visita: https://myaccount.google.com/

2. **Habilitar Verificación en 2 Pasos**
   - Click en "Seguridad" (menú izquierdo)
   - Busca "Cómo inicias sesión en Google"
   - Activa la "Verificación en 2 pasos"
   - Sigue las instrucciones para configurarla

3. **Generar Contraseña de Aplicación**
   - Una vez activada la verificación en 2 pasos
   - Busca "Contraseñas de aplicaciones"
   - Selecciona:
     - Aplicación: **Correo**
     - Dispositivo: **Windows Computer**
   - Click en "Generar"
   - Google te mostrará una contraseña de 16 caracteres
   - **¡GUARDA ESTA CONTRASEÑA!** (la necesitarás en el siguiente paso)

### Paso 2: Configurar Variables de Entorno

Edita tu archivo `.env` (en la raíz del proyecto) y agrega:

```env
# Configuración de correo electrónico (Gmail)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu_email@gmail.com
MAIL_PASSWORD=xxxx xxxx xxxx xxxx
MAIL_DEFAULT_SENDER=tu_email@gmail.com
```

**Reemplaza:**
- `tu_email@gmail.com` con tu correo de Gmail
- `xxxx xxxx xxxx xxxx` con la contraseña de aplicación de 16 caracteres que generaste

**Ejemplo:**
```env
MAIL_USERNAME=gametechstore@gmail.com
MAIL_PASSWORD=abcd efgh ijkl mnop
MAIL_DEFAULT_SENDER=gametechstore@gmail.com
```

### Paso 3: Reiniciar el Servidor

```bash
# Detener el servidor actual (Ctrl+C)
# Luego ejecutar:
python app.py
```

## ✅ Funcionalidades Implementadas

### 1. **Registro con Verificación**
- Al registrarse, el usuario recibe un correo con un enlace de verificación
- El enlace expira en 24 horas
- No puede iniciar sesión hasta verificar su correo

### 2. **Verificación de Email**
- El usuario hace click en el enlace del correo
- Su cuenta se marca como verificada
- Recibe un correo de bienvenida
- Ya puede iniciar sesión

### 3. **Reenvío de Verificación**
- Si el usuario no recibió el correo o expiró
- Puede solicitar un nuevo correo desde `/resend-verification`
- También hay un enlace en la página de login

### 4. **Bloqueo de Login**
- Los usuarios no verificados no pueden iniciar sesión
- Se muestra un mensaje indicando que deben verificar su correo
- Se ofrece un enlace para reenviar el correo

## 📁 Archivos Creados/Modificados

### Nuevos Archivos:
- `migrations/add_email_verification.py` - Migración de base de datos
- `utils/email_service.py` - Servicio de envío de correos
- `templates/emails/verify_email.html` - Template del correo de verificación
- `templates/emails/welcome.html` - Template del correo de bienvenida
- `templates/auth/resend_verification.html` - Página para reenviar verificación

### Archivos Modificados:
- `models/database_models.py` - Agregadas columnas: `email_verified`, `verification_token`, `token_expiry`
- `controllers/auth.py` - Lógica de verificación y envío de correos
- `templates/auth/login.html` - Mensaje de correo no verificado
- `app.py` - Configuración de Flask-Mail
- `.env.example` - Variables de entorno para correo

## 🔄 Flujo Completo

```
1. Usuario se registra
   ↓
2. Sistema genera token único
   ↓
3. Se envía correo con enlace de verificación
   ↓
4. Usuario hace click en el enlace
   ↓
5. Sistema verifica el token
   ↓
6. Cuenta marcada como verificada
   ↓
7. Se envía correo de bienvenida
   ↓
8. Usuario puede iniciar sesión
```

## 🧪 Pruebas

### Probar el Sistema:

1. **Registrar un nuevo usuario**
   - Ve a `/registro`
   - Completa el formulario
   - Verifica que recibes el correo

2. **Verificar el correo**
   - Abre el correo recibido
   - Haz click en "Verificar mi Cuenta"
   - Verifica que te redirige al login

3. **Intentar login sin verificar**
   - Registra otro usuario
   - NO hagas click en el enlace
   - Intenta iniciar sesión
   - Verifica que te bloquea

4. **Reenviar verificación**
   - Ve a `/resend-verification`
   - Ingresa el email
   - Verifica que recibes un nuevo correo

## 🚨 Solución de Problemas

### Error: "SMTPAuthenticationError"
- Verifica que la contraseña de aplicación esté correcta
- Asegúrate de que la verificación en 2 pasos esté activa

### Error: "Connection refused"
- Verifica que `MAIL_PORT=587`
- Verifica que `MAIL_USE_TLS=True`

### No recibo correos
- Revisa la carpeta de spam
- Verifica que el correo en `.env` sea correcto
- Revisa los logs del servidor para errores

### Token expirado
- Los tokens expiran en 24 horas
- Usa `/resend-verification` para obtener uno nuevo

## 📝 Notas Adicionales

- Los usuarios existentes fueron marcados automáticamente como verificados
- Solo los nuevos registros requerirán verificación
- Los correos se envían de forma asíncrona para no bloquear el registro
- Se recomienda usar un correo dedicado para la aplicación

## 🔐 Seguridad

- Los tokens son únicos y aleatorios (32 bytes)
- Los tokens expiran automáticamente
- Las contraseñas de aplicación son más seguras que la contraseña real
- No se almacenan contraseñas en texto plano

## 📧 Personalización

Para personalizar los correos, edita:
- `templates/emails/verify_email.html`
- `templates/emails/welcome.html`

Para cambiar el tiempo de expiración (24h por defecto):
- Edita `utils/email_service.py` → función `get_token_expiry()`
