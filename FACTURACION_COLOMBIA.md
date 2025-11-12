# 🇨🇴 Sistema de Facturación Electrónica Colombiana

## 📋 Cambios Implementados

### **1. Modelo de Factura Adaptado**
- ✅ Cambiado de RFC (México) a NIT/CC (Colombia)
- ✅ Agregado tipo de documento (13=CC, 31=NIT)
- ✅ Campos colombianos: ciudad, departamento, teléfono
- ✅ IVA 19% (estándar Colombia)
- ✅ CUFE en lugar de UUID del SAT
- ✅ Código QR para validación DIAN
- ✅ Email del receptor para envío automático

### **2. Controlador Actualizado**
- ✅ Validación de NIT colombiano
- ✅ Generación de factura con datos colombianos
- ✅ **Envío automático por correo electrónico**
- ✅ PDF adjunto en el email
- ✅ Notificación HTML profesional

### **3. Envío de Email**
- ✅ Email automático al generar factura
- ✅ PDF adjunto
- ✅ Diseño HTML profesional
- ✅ Detalles completos de la factura
- ✅ Información de la DIAN

---

## 🔧 Estructura de la Factura Colombiana

### **Datos del Emisor (GameTech Store)**
```
Razón Social: GameTech Store SAS
NIT: 900123456-7
Régimen: Responsable de IVA
```

### **Datos del Receptor (Cliente)**
```
NIT/CC: [Del cliente]
Tipo Documento: 13 (CC) o 31 (NIT)
Razón Social: [Nombre del cliente]
Dirección: [Dirección completa]
Ciudad: [Ciudad]
Departamento: [Departamento]
Email: [Correo registrado]
Teléfono: [Opcional]
```

### **Montos**
```
Subtotal: Base gravable
IVA (19%): Impuesto sobre las ventas
Total: Subtotal + IVA
```

### **Identificadores**
```
Folio: Número consecutivo de factura
CUFE: Código Único de Factura Electrónica
QR: Código QR para validación en DIAN
```

---

## 📧 Envío Automático por Email

### **Cuándo se Envía:**
1. ✅ Al generar la factura desde el panel de usuario
2. ✅ Automáticamente después de crear el PDF
3. ✅ Al correo registrado del usuario

### **Contenido del Email:**
- ✅ Número de factura
- ✅ CUFE
- ✅ Fecha de emisión
- ✅ Datos del cliente
- ✅ Total a pagar
- ✅ PDF adjunto
- ✅ Información de contacto

### **Diseño del Email:**
- ✅ HTML responsive
- ✅ Colores corporativos
- ✅ Información clara y organizada
- ✅ Advertencia sobre validez DIAN

---

## 🚀 Flujo de Facturación

### **1. Usuario Completa Compra**
```
Usuario → Checkout → Orden Creada
```

### **2. Usuario Solicita Factura**
```
Mis Órdenes → Solicitar Factura → Formulario
```

### **3. Formulario de Datos Fiscales**
```
- NIT/CC
- Tipo de Documento
- Razón Social
- Dirección
- Ciudad
- Departamento
- Teléfono (opcional)
- Forma de Pago
```

### **4. Sistema Genera Factura**
```
1. Valida datos
2. Calcula IVA (19%)
3. Genera CUFE
4. Crea registro en BD
5. Genera PDF
6. **Envía email automáticamente**
7. Muestra confirmación
```

### **5. Usuario Recibe Email**
```
📧 Email con:
- Detalles de la factura
- PDF adjunto
- Instrucciones
```

---

## 📝 Campos del Formulario

### **Obligatorios:**
- ✅ NIT/CC
- ✅ Razón Social

### **Opcionales:**
- Dirección Fiscal
- Ciudad
- Departamento
- Código Postal
- Teléfono

### **Automáticos:**
- Email (del usuario registrado)
- Fecha de emisión
- CUFE
- Folio consecutivo

---

## 🔐 Validaciones

### **NIT/CC:**
```python
- Longitud: 10-11 caracteres
- Solo números y guión
- Formato: 900123456-7
```

### **Email:**
```python
- Tomado del usuario registrado
- Validado en el registro
- Usado para envío automático
```

---

## 📊 Diferencias México vs Colombia

| Aspecto | México (CFDI) | Colombia (FE) |
|---------|---------------|---------------|
| Identificador | RFC | NIT/CC |
| Código Único | UUID SAT | CUFE |
| IVA | 16% | 19% |
| Autoridad | SAT | DIAN |
| Uso CFDI | Sí | No |
| Régimen Fiscal | Varios | Responsable IVA |
| Forma Pago | Códigos SAT | Texto libre |

---

## 🎯 Ventajas del Sistema

### **Para el Usuario:**
- ✅ Recibe factura por email automáticamente
- ✅ PDF descargable
- ✅ Datos guardados para futuras compras
- ✅ Historial de facturas

### **Para el Negocio:**
- ✅ Cumplimiento DIAN
- ✅ Proceso automatizado
- ✅ Registro de todas las facturas
- ✅ Trazabilidad completa

---

## 📧 Configuración de Email

### **Variables de Entorno Necesarias:**
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu-email@gmail.com
MAIL_PASSWORD=tu-app-password
MAIL_DEFAULT_SENDER=noreply@gametechstore.com
```

### **Verificar Configuración:**
```python
# En app.py
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', '587'))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
```

---

## 🧪 Pruebas

### **1. Crear Orden de Prueba**
```
1. Agregar productos al carrito
2. Completar checkout
3. Verificar orden creada
```

### **2. Solicitar Factura**
```
1. Ir a "Mis Órdenes"
2. Click en "Solicitar Factura"
3. Llenar formulario con datos colombianos
4. Enviar
```

### **3. Verificar Email**
```
1. Revisar bandeja de entrada
2. Verificar que llegó el email
3. Descargar PDF adjunto
4. Verificar datos en PDF
```

---

## 🔄 Migración de Datos

### **Si ya tienes facturas mexicanas:**

```sql
-- Actualizar tabla invoices
ALTER TABLE invoices 
ADD COLUMN nit_receptor VARCHAR(20),
ADD COLUMN tipo_documento_receptor VARCHAR(10),
ADD COLUMN ciudad VARCHAR(100),
ADD COLUMN departamento VARCHAR(100),
ADD COLUMN telefono VARCHAR(20),
ADD COLUMN email_receptor VARCHAR(200),
ADD COLUMN cufe TEXT,
ADD COLUMN qr_code TEXT;

-- Copiar datos existentes
UPDATE invoices 
SET nit_receptor = rfc_receptor,
    tipo_documento_receptor = '31',
    email_receptor = (SELECT email FROM users WHERE users.id = invoices.user_id);
```

---

## 📞 Soporte

Si tienes problemas:
1. Verificar configuración de email
2. Revisar logs de Render
3. Verificar que el usuario tenga email registrado
4. Verificar que MAIL_PASSWORD sea App Password de Gmail

---

**¡Sistema de facturación colombiana listo y funcional!** 🇨🇴
