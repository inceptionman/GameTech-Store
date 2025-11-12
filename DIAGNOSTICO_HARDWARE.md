# 🔍 Diagnóstico: Hardware y Configurador PC

## 🐛 Problemas Reportados:
1. ❌ Botón de hardware no funciona
2. ❌ Configurador de PC no muestra componentes

---

## 📋 Posibles Causas:

### **1. Error en get_especificaciones()**
Si `especificaciones` es `NULL` o string vacío en la base de datos:
```python
def get_especificaciones(self):
    return json.loads(self.especificaciones) if self.especificaciones else {}
```
- Si `self.especificaciones` es `None` → retorna `{}`
- Si `self.especificaciones` es `""` → puede causar error en `json.loads()`

### **2. Datos de Hardware Vacíos**
Si no hay hardware en la base de datos:
- `Hardware.get_all_hardware()` retorna lista vacía
- Templates no muestran nada

### **3. Error en API /api/hardware/buscar**
El configurador de PC usa esta API:
```javascript
const compResponse = await fetch(`/api/hardware/buscar?q=${tipo}`);
```
Si esta API falla, no se cargan componentes.

---

## 🔧 Soluciones a Implementar:

### **Solución 1: Mejorar get_especificaciones()**
```python
def get_especificaciones(self):
    """Obtener especificaciones como dict"""
    if not self.especificaciones:
        return {}
    try:
        return json.loads(self.especificaciones)
    except (json.JSONDecodeError, TypeError):
        return {}
```

### **Solución 2: Verificar Datos en Base de Datos**
```sql
-- Verificar si hay hardware
SELECT COUNT(*) FROM hardware;

-- Verificar especificaciones
SELECT id, tipo, marca, modelo, especificaciones FROM hardware LIMIT 5;
```

### **Solución 3: Agregar Logging**
```python
@hardware_bp.route('/api/hardware/buscar')
def api_buscar_hardware():
    query = request.args.get('q', '')
    app.logger.info(f'Buscando hardware: {query}')
    resultados = Hardware.buscar_hardware(query)
    app.logger.info(f'Resultados encontrados: {len(resultados)}')
    # ...
```

---

## 🧪 Pruebas a Realizar:

### **1. Verificar que /hardware carga**
```
URL: https://tu-app.onrender.com/hardware
Esperado: Página con componentes
```

### **2. Verificar API en consola del navegador**
```javascript
// Abrir consola (F12)
fetch('/api/hardware/tipos')
  .then(r => r.json())
  .then(d => console.log('Tipos:', d));

fetch('/api/hardware/buscar?q=CPU')
  .then(r => r.json())
  .then(d => console.log('CPUs:', d));
```

### **3. Verificar Logs de Render**
Buscar en logs:
- `Buscando hardware:`
- `Resultados encontrados:`
- Errores de JSON
- Errores de base de datos

---

## 📝 Información Necesaria:

Por favor proporciona:

1. **¿Qué error específico ves?**
   - [ ] Página en blanco
   - [ ] Error 500
   - [ ] Componentes no se cargan
   - [ ] Otro: ___________

2. **¿En qué URL ocurre?**
   - [ ] /hardware
   - [ ] /configurador-pc
   - [ ] Ambas

3. **¿Hay errores en la consola del navegador?** (F12)
   - [ ] Sí → Copiar error
   - [ ] No

4. **¿Hay errores en los logs de Render?**
   - [ ] Sí → Copiar últimas 50 líneas
   - [ ] No

---

## 🚀 Próximos Pasos:

1. Implementar mejora en `get_especificaciones()`
2. Agregar logging a las APIs
3. Verificar datos en base de datos
4. Revisar logs de Render
