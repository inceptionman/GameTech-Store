# 📋 Cómo Ver los Logs de Render - Paso a Paso

## 🎯 Necesito que copies los logs para diagnosticar el error

---

## 📍 **Paso 1: Acceder a Render Dashboard**

1. Abre tu navegador
2. Ve a: **https://dashboard.render.com/**
3. Inicia sesión con tu cuenta

---

## 📍 **Paso 2: Seleccionar tu Servicio**

1. En el dashboard, verás una lista de servicios
2. Busca y haz click en: **"GameTech Store"** (o el nombre de tu servicio)

---

## 📍 **Paso 3: Abrir la Pestaña de Logs**

1. En la página del servicio, verás varias pestañas en la parte superior:
   - Overview
   - Events
   - **Logs** ← Click aquí
   - Shell
   - Settings

2. Click en **"Logs"**

---

## 📍 **Paso 4: Ver los Logs en Tiempo Real**

Verás algo como esto:
```
[2025-11-11 19:03:45] INFO: Starting application...
[2025-11-11 19:03:46] INFO: ✅ CSRF Protection habilitado
[2025-11-11 19:03:47] INFO: Hardware encontrado: 0 componentes
[2025-11-11 19:03:48] ERROR: ...
```

---

## 📍 **Paso 5: Copiar los Logs**

### **Opción A: Copiar Todo**
1. Presiona **Ctrl+A** (seleccionar todo)
2. Presiona **Ctrl+C** (copiar)
3. Pega aquí en el chat

### **Opción B: Copiar Solo Errores**
1. Busca líneas que digan **ERROR** o **Traceback**
2. Copia desde el error hasta el final del stack trace
3. Pega aquí en el chat

---

## 🔍 **Qué Buscar Específicamente:**

### **1. Cuando accedes a /hardware:**
```
[INFO] Hardware encontrado: X componentes
[INFO] Categorías: [...]
```
O
```
[ERROR] Error en lista_hardware: ...
Traceback (most recent call last):
  ...
```

### **2. Cuando accedes a /configurador-pc:**
```
[INFO] API buscar hardware: query=CPU
[INFO] Resultados encontrados: X
```
O
```
[ERROR] Error en api_buscar_hardware: ...
```

### **3. Errores de Base de Datos:**
```
[ERROR] OperationalError: ...
[ERROR] no such table: hardware
[ERROR] column hardware.especificaciones does not exist
```

---

## 📸 **Alternativa: Screenshot**

Si es más fácil, puedes:
1. Tomar captura de pantalla de los logs
2. Compartir la imagen

---

## ⚡ **Acción Rápida:**

**Copia y pega aquí las últimas 100 líneas de logs**, especialmente:
- Las líneas que aparecen cuando intentas acceder a `/hardware`
- Las líneas que aparecen cuando intentas acceder a `/configurador-pc`
- Cualquier línea que diga **ERROR** o **Traceback**

---

## 🎯 **Ejemplo de lo que necesito ver:**

```
[2025-11-11 19:03:45] INFO: Starting gunicorn
[2025-11-11 19:03:46] INFO: ✅ CSRF Protection habilitado
[2025-11-11 19:03:47] INFO: Hardware encontrado: 0 componentes
[2025-11-11 19:03:48] ERROR: Error en lista_hardware: 'NoneType' object has no attribute 'get'
Traceback (most recent call last):
  File "/opt/render/project/src/controllers/hardware.py", line 15, in lista_hardware
    categorias[componente.tipo] = []
AttributeError: 'NoneType' object has no attribute 'tipo'
```

---

## ❓ **¿No puedes acceder a los logs?**

Si no puedes ver los logs, dime:
1. ¿Qué URL exacta estás visitando cuando sale el error?
2. ¿Aparece algún mensaje de error en la página?
3. Abre la consola del navegador (F12) y copia cualquier error que veas

---

**Una vez que me compartas los logs, podré ver exactamente qué está fallando y solucionarlo.** 🔍
