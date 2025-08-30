# 🚀 GUÍA DE MODIFICACIÓN Y EXTENSIÓN

## 🎯 Cómo Modificar el Chatbot

### 📝 Agregar Nuevos Comandos

Para agregar un comando personalizado, modifica la función `procesar_mensaje()`:

```python
# En servidor_webhook.py, línea ~570

# Verificar comando personalizado
if mensaje_usuario.strip().lower() == "/comando_nuevo":
    # Tu lógica aquí
    respuesta = "Tu respuesta personalizada"
    enviar_mensaje_whatsapp(numero, respuesta)
    return
```

### 🔍 Agregar Nuevos Tipos de Búsqueda

Para detectar nuevos tipos de consulta, modifica la sección de detección:

```python
# En servidor_webhook.py, línea ~620

# Agregar nueva detección
elif any(palabra in mensaje_lower for palabra in ['nueva_busqueda', 'buscar_especial']):
    datos_especificos = tu_nueva_funcion_busqueda()
```

### 📊 Agregar Nuevas Funciones de Análisis

Crea una nueva función siguiendo el patrón existente:

```python
def tu_nueva_funcion():
    """Nueva función de análisis de inventario"""
    global df_inventario
    if df_inventario is None:
        return "No hay inventario disponible"

    try:
        # Tu lógica de análisis aquí
        resultado = "Tu análisis formateado"
        return resultado

    except Exception as e:
        return f"Error en análisis: {e}"
```

---

## 🔧 Configuraciones Importantes

### 🔑 Cambiar APIs

#### Gemini API

```python
# Línea 25
GEMINI_API_KEY = "tu_nueva_api_key"
```

#### Evolution API

```python
# Líneas 27-30
EVOLUTION_API_URL = "tu_nueva_url"
EVOLUTION_API_KEY = "tu_nueva_key"
INSTANCE_NAME = "tu_instancia"
```

### 📊 Cambiar Archivo de Inventario

```python
# Líneas 32-33
ARCHIVO_INVENTARIO = "tu_archivo.xlsx"
HOJA_PRODUCTOS = "tu_hoja"
```

### ⚙️ Ajustar Configuraciones del Sistema

```python
# Memoria de conversación (línea 450)
if len(conversaciones[numero]) > 10:  # Cambiar 10 por tu límite

# Límite de WhatsApp (línea 305)
LIMITE_WHATSAPP = 4000  # Cambiar límite de caracteres

# Delay entre mensajes (línea 330)
time.sleep(1)  # Cambiar tiempo de espera
```

---

## 🎨 Personalizar Respuestas

### 🎯 Mensajes de Sistema

#### Mensaje de Bienvenida

```python
# Línea ~580
mensaje_bienvenida = """🎯 **TU MENSAJE PERSONALIZADO**

¡Personaliza este mensaje de bienvenida!"""
```

#### Mensaje de Despedida

```python
# Línea ~590
mensaje_despedida = """👋 **TU MENSAJE DE DESPEDIDA**

¡Personaliza este mensaje de despedida!"""
```

### 🤖 Personalizar Prompt de Gemini

Modifica el prompt principal en la línea ~630:

```python
prompt = f"""
Eres un BOT personalizado para [TU EMPRESA].

[TUS REGLAS PERSONALIZADAS]

[TUS CAPACIDADES ESPECÍFICAS]
"""
```

---

## 📈 Agregar Nuevas Características

### 1. 📸 Análisis de Imágenes

```python
# Agregar después de las funciones de WhatsApp

def procesar_imagen(message_data):
    """Procesa mensajes con imágenes"""
    if message_data.get('messageType') == 'imageMessage':
        # Descargar imagen
        # Enviar a Gemini Vision
        # Retornar análisis
        pass
```

### 2. 📊 Dashboard Web

```python
# Agregar nuevo endpoint
@app.route('/dashboard')
def dashboard():
    """Dashboard de administración"""
    stats = {
        'sesiones_activas': len(sesiones_activas),
        'conversaciones': len(conversaciones),
        'inventario_productos': len(df_inventario) if df_inventario is not None else 0
    }
    return render_template('dashboard.html', stats=stats)
```

### 3. 🔔 Notificaciones Automáticas

```python
def enviar_notificacion_stock_bajo():
    """Envía notificaciones de stock bajo"""
    if df_inventario is None:
        return

    # Lógica para detectar stock bajo
    productos_bajo_stock = df_inventario[df_inventario['stock'] < 5]

    # Enviar notificación al administrador
    admin_numero = "TU_NUMERO_ADMIN"
    mensaje = f"⚠️ {len(productos_bajo_stock)} productos con stock bajo"
    enviar_mensaje_whatsapp(admin_numero, mensaje)
```

### 4. 💾 Base de Datos

Para migrar de Excel a base de datos:

```python
import sqlite3

def crear_base_datos():
    """Crea base de datos SQLite"""
    conn = sqlite3.connect('inventario.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY,
        nombre TEXT,
        categoria TEXT,
        precio REAL,
        stock INTEGER
    )
    ''')

    conn.commit()
    conn.close()

def cargar_desde_bd():
    """Carga inventario desde base de datos"""
    conn = sqlite3.connect('inventario.db')
    df = pd.read_sql_query("SELECT * FROM productos", conn)
    conn.close()
    return df
```

---

## 🔍 Debugging y Logs

### Agregar Logs Personalizados

```python
import logging

# Configurar logger personalizado
custom_logger = logging.getLogger('mi_bot')
custom_logger.setLevel(logging.DEBUG)

# Usar en tus funciones
custom_logger.info("Mi log personalizado")
custom_logger.error("Error personalizado")
```

### Endpoint de Debug

```python
@app.route('/debug')
def debug():
    """Información de debug"""
    return jsonify({
        'conversaciones': dict(conversaciones),
        'sesiones_activas': dict(sesiones_activas),
        'memoria_total': len(conversaciones),
        'gemini_status': gemini_model is not None
    })
```

---

## 🚀 Optimizaciones

### 1. Cache de Respuestas

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def busqueda_cacheada(terminos_busqueda):
    """Búsqueda con cache"""
    return buscar_productos_especificos(terminos_busqueda.split(','))
```

### 2. Procesamiento Asíncrono

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=4)

def procesar_mensaje_async(message_data):
    """Procesa mensaje de forma asíncrona"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    future = executor.submit(procesar_mensaje, message_data)
    return future
```

### 3. Compresión de Respuestas

```python
def comprimir_respuesta(respuesta):
    """Comprime respuestas largas"""
    if len(respuesta) > 2000:
        # Resumir con Gemini
        prompt_resumen = f"Resume este texto en 500 caracteres: {respuesta}"
        respuesta_resumida = gemini_model.generate_content(prompt_resumen)
        return respuesta_resumida.text
    return respuesta
```

---

## 🔒 Seguridad

### Control de Acceso por Número

```python
NUMEROS_AUTORIZADOS = [
    "1234567890",
    "0987654321"
]

def usuario_autorizado(numero):
    """Verifica si el usuario está autorizado"""
    return numero in NUMEROS_AUTORIZADOS

# Usar en procesar_mensaje()
if not usuario_autorizado(numero):
    logger.warning(f"⛔ Usuario no autorizado: {numero}")
    return
```

### Rate Limiting

```python
from time import time

ultimas_consultas = {}

def verificar_rate_limit(numero, limite_por_minuto=10):
    """Verifica límite de consultas por minuto"""
    ahora = time()
    if numero not in ultimas_consultas:
        ultimas_consultas[numero] = []

    # Filtrar consultas del último minuto
    ultimas_consultas[numero] = [
        t for t in ultimas_consultas[numero]
        if ahora - t < 60
    ]

    if len(ultimas_consultas[numero]) >= limite_por_minuto:
        return False

    ultimas_consultas[numero].append(ahora)
    return True
```

---

## 📝 Testing

### Tests Básicos

```python
import unittest

class TestBot(unittest.TestCase):

    def test_inicializar_gemini(self):
        """Test de inicialización de Gemini"""
        model = inicializar_gemini()
        self.assertIsNotNone(model)

    def test_cargar_inventario(self):
        """Test de carga de inventario"""
        inventario = cargar_inventario()
        self.assertIsNotNone(inventario)

    def test_sesiones(self):
        """Test de control de sesiones"""
        numero_test = "1234567890"

        # Iniciar sesión
        iniciar_sesion_inventario(numero_test)
        self.assertTrue(tiene_sesion_activa(numero_test))

        # Finalizar sesión
        finalizar_sesion_inventario(numero_test)
        self.assertFalse(tiene_sesion_activa(numero_test))

if __name__ == '__main__':
    unittest.main()
```

---

## 🌐 Despliegue

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements_whatsapp.txt .
RUN pip install -r requirements_whatsapp.txt

COPY . .

EXPOSE 8000

CMD ["python", "servidor_webhook.py"]
```

### Systemd Service

```ini
[Unit]
Description=WhatsApp Gemini Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/whatsapp-bot
ExecStart=/usr/bin/python3 servidor_webhook.py
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## 📋 Lista de Verificación para Modificaciones

Antes de hacer cambios:

- [ ] Hacer backup del código actual
- [ ] Probar en entorno de desarrollo
- [ ] Verificar logs después de cambios
- [ ] Probar todos los comandos existentes
- [ ] Verificar manejo de errores
- [ ] Documentar cambios realizados

Después de hacer cambios:

- [ ] Reiniciar el servidor
- [ ] Probar comando `/inventario`
- [ ] Probar comando `/fin`
- [ ] Verificar endpoint `/status`
- [ ] Probar búsquedas básicas
- [ ] Verificar logs por errores
