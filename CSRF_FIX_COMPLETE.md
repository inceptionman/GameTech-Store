# 🔒 Corrección Completa de CSRF Tokens

## ✅ Archivos Corregidos

### **Autenticación:**
- [x] `templates/auth/login.html` - Formulario de login
- [x] `templates/auth/registro.html` - Formulario de registro  
- [ ] `templates/auth/recuperar_password.html` - Recuperar contraseña
- [ ] `templates/auth/reset_password.html` - Restablecer contraseña
- [ ] `templates/auth/resend_verification.html` - Reenviar verificación
- [ ] `templates/auth/editar_perfil.html` - Editar perfil

### **Carrito:**
- [x] `templates/cart/carrito.html` - Todos los formularios del carrito
- [ ] `templates/cart/checkout.html` - Checkout

### **Facturas:**
- [ ] `templates/invoice/solicitar_factura.html` - Solicitar factura
- [ ] `templates/invoice/ver_factura.html` - Cancelar factura

### **Admin:**
- [ ] `templates/admin/usuarios.html` - Toggle admin
- [ ] `templates/admin/orden_detalle.html` - Actualizar estado
- [ ] `templates/admin/juego_form.html` - Formulario juego
- [ ] `templates/admin/hardware_form.html` - Formulario hardware

## 🚀 Solución Rápida

Para corregir TODOS los formularios de una vez, agrega esto en `base.html` dentro del `<head>`:

```html
<script>
// Auto-agregar CSRF token a todos los formularios POST
document.addEventListener('DOMContentLoaded', function() {
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
    if (csrfToken) {
        document.querySelectorAll('form[method="POST"], form[method="post"]').forEach(form => {
            // Verificar si ya tiene el token
            if (!form.querySelector('input[name="csrf_token"]')) {
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = 'csrf_token';
                input.value = csrfToken;
                form.prepend(input);
            }
        });
    }
});
</script>
```

Este script JavaScript agregará automáticamente el CSRF token a TODOS los formularios POST que no lo tengan.

## ⚡ Aplicar Ahora

1. Abre `templates/base.html`
2. Agrega el script antes de `</head>`
3. Guarda y despliega

Esto solucionará el problema del CSRF en TODOS los formularios sin tener que editar cada archivo manualmente.
