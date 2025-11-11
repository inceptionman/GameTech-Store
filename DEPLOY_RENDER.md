# 🚀 Despliegue en Render

## Variables de Entorno Requeridas

Debes configurar estas variables de entorno en Render:

### Base de Datos
```
DATABASE_URL=tu_url_de_postgresql
```

### Flask
```
SECRET_KEY=tu_clave_secreta_segura
FLASK_ENV=production
```

### Email (Gmail)
```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu_email@gmail.com
MAIL_PASSWORD=tu_contraseña_de_aplicacion
MAIL_DEFAULT_SENDER=tu_email@gmail.com
```

## Pasos para Configurar en Render

1. **Crear Web Service**
   - Ve a tu dashboard de Render
   - Click en "New +" → "Web Service"
   - Conecta tu repositorio de GitHub

2. **Configuración del Servicio**
   - **Name:** GameTech-Store
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`

3. **Variables de Entorno**
   - Ve a "Environment" en el panel izquierdo
   - Agrega todas las variables listadas arriba
   - **IMPORTANTE:** No incluyas las variables de email si no las necesitas inmediatamente

4. **Base de Datos PostgreSQL**
   - Render te proporciona una URL de PostgreSQL
   - Copia esa URL y úsala como `DATABASE_URL`

5. **Ejecutar Migraciones**
   - Una vez desplegado, ve a "Shell" en Render
   - Ejecuta: `python migrations/add_email_verification.py`

## Solución de Problemas

### Error: "Exited with status 1"
- Verifica que todas las dependencias estén en `requirements.txt`
- Asegúrate de que `DATABASE_URL` esté configurada
- Revisa los logs de despliegue para más detalles

### Error de Base de Datos
- Verifica que la URL de PostgreSQL sea correcta
- Asegúrate de que la base de datos esté accesible

### Error de Email
- Las variables de email son opcionales para el despliegue inicial
- Puedes agregarlas después cuando las necesites

## Comandos Útiles

### Ver logs en tiempo real
En el dashboard de Render, ve a "Logs"

### Reiniciar el servicio
Click en "Manual Deploy" → "Deploy latest commit"

### Ejecutar comandos
Ve a "Shell" y ejecuta comandos Python directamente
