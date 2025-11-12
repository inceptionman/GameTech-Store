# 🔧 Actualización del Controlador de Facturas

## ⚠️ IMPORTANTE: Reemplazar controllers/invoice.py

El archivo `controllers/invoice.py` necesita ser actualizado completamente.

### Cambios Necesarios:

1. **Importar función de envío de email:**
```python
from utils.email_sender import enviar_factura_por_email
```

2. **Después de generar el PDF (línea ~96):**
```python
# Enviar factura por email
try:
    email_enviado = enviar_factura_por_email(invoice, current_user, full_pdf_path)
    if email_enviado:
        flash(f'¡Factura generada y enviada a {current_user.email}!', 'success')
    else:
        flash(f'Factura generada. Email no pudo ser enviado.', 'warning')
except Exception as e:
    current_app.logger.error(f'Error enviando email: {str(e)}')
    flash(f'Factura generada. Error al enviar email.', 'warning')
```

3. **Actualizar validación de NIT:**
```python
# Validar formato de NIT (simplificado)
if len(nit) < 7 or len(nit) > 20:
    flash('NIT/CC inválido', 'danger')
    return render_template(SOLICITAR_FACTURA, order=order, user=current_user)
```

4. **Actualizar creación de factura:**
```python
user_fiscal_data = {
    'nit': nit,
    'tipo_documento': tipo_documento,
    'razon_social': razon_social,
    'direccion_fiscal': direccion_fiscal,
    'ciudad': ciudad,
    'departamento': departamento,
    'codigo_postal': codigo_postal,
    'telefono': telefono,
    'email_receptor': current_user.email,
    'forma_pago': forma_pago
}
```

5. **Guardar datos en usuario:**
```python
if request.form.get('guardar_datos'):
    current_user.rfc = nit  # Reutilizamos el campo rfc para NIT
    current_user.razon_social = razon_social
    current_user.direccion_fiscal = direccion_fiscal
    current_user.codigo_postal = codigo_postal
```

---

## 📝 Código Completo para Reemplazar

Ver archivo: `controllers/invoice_colombia.py.new`

---

## 🚀 Pasos para Aplicar:

1. Hacer backup del archivo actual:
```bash
cp controllers/invoice.py controllers/invoice.py.backup
```

2. Actualizar el archivo con los cambios

3. Reiniciar la aplicación

4. Probar generación de factura

---

## ✅ Verificación:

Después de actualizar, verificar:
- [ ] Factura se genera correctamente
- [ ] Email se envía automáticamente
- [ ] PDF se adjunta al email
- [ ] Usuario recibe el correo
- [ ] Datos colombianos se guardan correctamente

---

**Nota:** El código actual del controlador tiene referencias a RFC y CFDI mexicano que deben ser reemplazadas por NIT y campos colombianos.
