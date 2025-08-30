# 📚 DOCUMENTACIÓN TÉCNICA - FUNCIONES

## 🧠 Funciones de Inicialización

### `inicializar_gemini()`

**Propósito**: Configura y inicializa el cliente de Google Gemini  
**Parámetros**: Ninguno  
**Retorna**: `GenerativeModel` object o `None` si hay error  
**Uso**: Se ejecuta automáticamente al iniciar el servidor

```python
def inicializar_gemini():
    """Inicializa el cliente de Gemini"""
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")
    return model
```

---

## 📊 Funciones de Inventario

### `cargar_inventario()`

**Propósito**: Carga el archivo Excel y lo convierte a texto para la IA  
**Parámetros**: Ninguno (usa `ARCHIVO_INVENTARIO` global)  
**Retorna**: String con el inventario formateado o `None`  
**Comportamiento**:

- Busca el archivo en múltiples ubicaciones
- Carga la hoja "Productos"
- Convierte a texto legible para Gemini

```python
def cargar_inventario():
    posibles_rutas = [
        Path(ARCHIVO_INVENTARIO),
        Path("..") / ARCHIVO_INVENTARIO,
        Path("../..") / ARCHIVO_INVENTARIO,
        Path("/opt/webhook") / ARCHIVO_INVENTARIO
    ]
```

### `convertir_inventario_a_texto(df)`

**Propósito**: Convierte DataFrame de pandas a texto estructurado  
**Parámetros**: `df` (pandas.DataFrame) - DataFrame del inventario  
**Retorna**: String formateado con todos los productos  
**Formato**: Incluye todos los campos disponibles por producto

### `obtener_todas_las_categorias()`

**Propósito**: Extrae todas las categorías únicas del inventario  
**Parámetros**: Ninguno  
**Retorna**: String con lista de categorías formateada  
**Lógica**: Busca columnas que contengan "categoria", "category", "tipo"

### `calcular_stock_total()`

**Propósito**: Suma todo el stock disponible en el inventario  
**Parámetros**: Ninguno  
**Retorna**: String con resumen de stock total  
**Cálculos**: Total de unidades, productos con stock, promedio por producto

### `calcular_valor_inventario()`

**Propósito**: Calcula el valor monetario total del inventario  
**Parámetros**: Ninguno  
**Retorna**: String con valor total del inventario  
**Fórmula**: `precio × stock` para cada producto

### `buscar_productos_especificos(terminos)`

**Propósito**: Busca productos que coincidan con términos específicos  
**Parámetros**: `terminos` (list) - Lista de palabras a buscar  
**Retorna**: String con productos encontrados y totales  
**Búsqueda**: Case-insensitive en todas las columnas del DataFrame

---

## 📱 Funciones de WhatsApp

### `enviar_mensaje_whatsapp(numero, mensaje)`

**Propósito**: Función principal para enviar mensajes por WhatsApp  
**Parámetros**:

- `numero` (str) - Número de teléfono sin @s.whatsapp.net
- `mensaje` (str) - Texto del mensaje a enviar  
  **Retorna**: Boolean - True si se envió exitosamente  
  **Características**:
- Verifica límite de 4000 caracteres
- Divide automáticamente mensajes largos
- Maneja errores de envío

### `enviar_mensaje_simple(numero, mensaje)`

**Propósito**: Envía un mensaje simple sin verificaciones  
**Parámetros**:

- `numero` (str) - Número de teléfono
- `mensaje` (str) - Texto del mensaje  
  **Retorna**: Boolean - True si response.status_code in [200, 201]  
  **API**: Usa Evolution API `/message/sendText/` endpoint

### `dividir_mensaje(mensaje, limite)`

**Propósito**: Divide mensajes largos en partes más pequeñas  
**Parámetros**:

- `mensaje` (str) - Mensaje original
- `limite` (int) - Máximo de caracteres por parte  
  **Retorna**: List[str] - Lista de partes del mensaje  
  **Lógica**: Respeta estructura de productos y líneas

### `dividir_por_productos(mensaje, limite)`

**Propósito**: División especializada para mensajes con productos  
**Parámetros**:

- `mensaje` (str) - Mensaje con productos
- `limite` (int) - Límite de caracteres  
  **Retorna**: List[str] - Partes del mensaje  
  **Comportamiento**: Mantiene productos completos, no los corta

---

## 💾 Funciones de Memoria

### `obtener_conversacion(numero)`

**Propósito**: Obtiene el historial de conversación de un usuario  
**Parámetros**: `numero` (str) - Número de teléfono del usuario  
**Retorna**: List[str] - Lista de mensajes del historial  
**Inicialización**: Crea lista vacía si no existe

### `agregar_mensaje_a_conversacion(numero, mensaje, es_usuario=True)`

**Propósito**: Agrega un mensaje al historial de conversación  
**Parámetros**:

- `numero` (str) - Número de teléfono
- `mensaje` (str) - Texto del mensaje
- `es_usuario` (bool) - True si es mensaje del usuario, False si es del bot  
  **Comportamiento**: Mantiene solo los últimos 10 mensajes

### `formatear_historial(numero)`

**Propósito**: Formatea el historial para incluir en prompts de Gemini  
**Parámetros**: `numero` (str) - Número de teléfono  
**Retorna**: String formateado con historial  
**Formato**: "HISTORIAL DE CONVERSACIÓN:\nUsuario: ...\nBot: ..."

---

## 🎯 Funciones de Control de Sesiones

### `iniciar_sesion_inventario(numero)`

**Propósito**: Inicia una sesión de inventario para un usuario  
**Parámetros**: `numero` (str) - Número de teléfono  
**Efecto**: Agrega el número al diccionario `sesiones_activas`

### `finalizar_sesion_inventario(numero)`

**Propósito**: Finaliza una sesión y limpia la memoria  
**Parámetros**: `numero` (str) - Número de teléfono  
**Efecto**: Elimina sesión activa y conversación del usuario

### `tiene_sesion_activa(numero)`

**Propósito**: Verifica si un usuario tiene sesión activa  
**Parámetros**: `numero` (str) - Número de teléfono  
**Retorna**: Boolean - True si tiene sesión activa

---

## 🌐 Funciones del Servidor Flask

### `webhook()` - POST /webhook

**Propósito**: Endpoint principal que recibe mensajes de Evolution API  
**Método**: POST  
**Parámetros**: JSON con datos del mensaje  
**Retorna**: JSON con status  
**Proceso**:

1. Recibe datos del webhook
2. Valida formato
3. Procesa mensaje(s)
4. Retorna confirmación

### `procesar_mensaje(message_data)`

**Propósito**: Procesa un mensaje individual de WhatsApp  
**Parámetros**: `message_data` (dict) - Datos del mensaje  
**Lógica Principal**:

1. Verifica que sea mensaje de conversación
2. Extrae número y mensaje
3. Maneja comandos `/inventario` y `/fin`
4. Verifica sesión activa
5. Procesa con Gemini si hay sesión

### `status()` - GET /status

**Propósito**: Endpoint para verificar estado del servidor  
**Método**: GET  
**Retorna**: JSON con información del sistema  
**Información**: Estado de Gemini, inventario, conversaciones activas, etc.

### `home()` - GET /

**Propósito**: Página de inicio con información básica  
**Método**: GET  
**Retorna**: HTML con instrucciones y estado

---

## 🧠 Lógica de Procesamiento de Mensajes

### Flujo Principal

1. **Recepción**: Webhook recibe mensaje de Evolution API
2. **Validación**: Verifica que sea mensaje de conversación
3. **Extracción**: Obtiene número de teléfono y texto
4. **Control de Sesión**:
   - `/inventario` → Inicia sesión
   - `/fin` → Termina sesión
   - Sin sesión → Ignora mensaje
5. **Procesamiento IA**:
   - Obtiene historial de conversación
   - Detecta tipo de consulta
   - Genera datos específicos si es necesario
   - Envía prompt a Gemini
   - Procesa respuesta
6. **Envío**: Manda respuesta por WhatsApp

### Tipos de Consulta Detectados

```python
# Categorías
['categorías', 'categorias', 'todas las categorias']

# Cálculos de stock
['suma', 'total', 'stock total', 'cuanto stock']

# Valores monetarios
['valor total', 'costo total', 'precio total']

# Búsquedas de productos
['buscar', 'mostrar', 'productos']
```

### Prompt de Gemini

El sistema usa un prompt unificado que incluye:

- Historial de conversación
- Reglas y capacidades del bot
- Datos específicos para la consulta
- Inventario completo
- Mensaje actual del usuario

---

## 🔧 Variables Globales

### Configuración

- `GEMINI_API_KEY`: Clave API de Google Gemini
- `EVOLUTION_API_URL`: URL base de Evolution API
- `EVOLUTION_API_KEY`: Clave API de Evolution
- `INSTANCE_NAME`: Nombre de la instancia de WhatsApp
- `ARCHIVO_INVENTARIO`: Nombre del archivo Excel
- `HOJA_PRODUCTOS`: Nombre de la hoja a leer

### Estado del Sistema

- `df_inventario`: DataFrame global con datos del Excel
- `conversaciones`: Dict con historiales por número de teléfono
- `sesiones_activas`: Dict con sesiones activas
- `gemini_model`: Instancia del modelo Gemini
- `inventario_texto`: String con inventario formateado para IA

---

## 🚀 Inicialización del Sistema

Al ejecutar `servidor_webhook.py`:

1. Se configura logging
2. Se inicializa Gemini
3. Se carga el inventario Excel
4. Se inicia el servidor Flask en puerto 8000
5. Se muestran URLs de acceso

### Endpoints Disponibles

- `POST /webhook` - Recibe mensajes de WhatsApp
- `GET /status` - Estado del sistema
- `GET /` - Página de inicio

### Logs y Debugging

El sistema registra:

- Mensajes recibidos
- Sesiones iniciadas/terminadas
- Errores de procesamiento
- Respuestas enviadas
- División de mensajes largos

---

# Cambios Realizados

## Reemplazo de `google-generativeai` por `google-genai`

Se actualizó la importación y uso del cliente de Gemini:

```python
# Actual (google-generativeai) → Recomendado (google-genai)
from google import genai
client = genai.Client(api_key=API_KEY)
```
