# 🤖 CONTEXTO PARA IA - CHATBOT WHATSAPP + GEMINI

## 🎯 INFORMACIÓN ESENCIAL PARA IA

### Descripción del Proyecto

Este es un **chatbot empresarial** que integra WhatsApp + Google Gemini + Excel para consultas de inventario. Funciona con **control de sesiones estricto** donde solo responde entre comandos `/inventario` y `/fin`.

### Estado Actual del Proyecto

- ✅ **COMPLETAMENTE FUNCIONAL** en producción
- ✅ **DESPLEGADO** en servidor 107.170.78.13:8000
- ✅ **INTEGRADO** con Evolution API cloud
- ✅ **CONECTADO** a inventario Excel con 672 productos
- ✅ **OPTIMIZADO** para WhatsApp con división automática de mensajes
- ✅ **LIMPIO** - Solo archivos esenciales después de cleanup

---

## 📂 Archivos del Proyecto

### Archivos Actuales (Solo Esenciales)

```
├── servidor_webhook.py          # ⭐ ARCHIVO PRINCIPAL (753 líneas)
├── requirements_whatsapp.txt    # 📦 Dependencias Python
├── .env                        # 🔐 Variables entorno (vacío)
├── README.md                   # 📖 Documentación principal
├── DOCUMENTACION_TECNICA.md    # 📚 Docs técnicas detalladas
├── GUIA_MODIFICACION.md        # 🛠️ Guía para modificar
└── Inventario_Completo.xlsx    # 📊 Base datos productos (672 items)
```

### Archivos Eliminados (No Usar)

- `bot_simple.py`, `chatbot_simple.py` - Versiones obsoletas
- `src/` folder - Código no usado
- Docker files - No necesarios
- Scripts de configuración - Ya configurado
- READMEs antiguos - Reemplazados

---

## 🔧 Configuración Técnica

### APIs y Servicios

```python
# Gemini AI
API_KEY = "AIzaSyB-oKvbiRYzUDFxN12KvO4mRXIs1uGLx3A"
MODEL = "gemini-2.5-flash"

# Evolution API (WhatsApp Cloud)
URL = "https://automatizacion-evolution-api.cmnivw.easypanel.host"
API_KEY = "927F90B2922D-40EA-A341-2A5256F2E94F"
INSTANCE = "whatsapp-bot"

# Servidor
HOST = "107.170.78.13:8000"
WEBHOOK = "/webhook"
STATUS = "/status"
```

### Dependencias

```
google-generativeai  # Gemini AI
flask               # Servidor web
requests            # HTTP requests
pandas              # Excel processing
openpyxl            # Excel reader
```

---

## 🎮 Funcionalidades Implementadas

### Control de Sesiones

- **Comando inicio**: `/inventario` - Inicia sesión y da bienvenida
- **Comando fin**: `/fin` - Termina sesión y limpia memoria
- **Sin sesión**: Bot completamente silencioso (ignora mensajes)
- **Con sesión**: Responde a todas las consultas

### Capacidades de IA

- **Búsquedas semánticas**: "algo para regalo" → encuentra productos relevantes
- **Consultas naturales**: "cámara para galpón 20x20" → busca por características
- **Cálculos automáticos**: stock total, valores, promedios, estadísticas
- **Memoria conversacional**: Recuerda últimos 10 mensajes por usuario
- **Manejo de errores**: Respuestas robustas a consultas incorrectas

### Integración Excel

- **Archivo**: `Inventario_Completo.xlsx`, hoja "Productos"
- **Productos**: 672 items con todos los campos disponibles
- **Campos**: Marca, Categoría, Tipo, Stock, Precio, Características, etc.
- **Búsqueda**: En todos los campos, tolerante a errores de escritura

### WhatsApp Optimizado

- **División automática**: Mensajes largos divididos en partes < 4000 chars
- **Numeración**: Partes múltiples numeradas automáticamente
- **Delay**: 1 segundo entre partes para evitar spam
- **Formato**: Mantiene estructura de productos completos

---

## 🧠 Arquitectura del Sistema

### Flujo de Mensajes

```
WhatsApp User → Evolution API → Webhook → Flask Server → Gemini AI
                                    ↓
                               Excel Reader
                                    ↓
                            Memory Management
                                    ↓
                          Response Processing
                                    ↓
                        WhatsApp User (Response)
```

### Componentes Principales

1. **Webhook Receiver** - Recibe mensajes de Evolution API
2. **Session Controller** - Maneja sesiones `/inventario` → `/fin`
3. **Memory Manager** - Historial de conversación por usuario
4. **Excel Processor** - Lee y analiza inventario
5. **Gemini Interface** - Procesa consultas con IA
6. **Message Splitter** - Divide respuestas largas
7. **WhatsApp Sender** - Envía respuestas formateadas

---

## 📊 Datos y Estructura

### Variables Globales Importantes

```python
df_inventario = None           # DataFrame con productos Excel
conversaciones = {}           # Dict: numero → [mensajes]
sesiones_activas = {}        # Dict: numero → True
gemini_model = None          # Instancia Gemini
inventario_texto = None      # String formateado para IA
```

### Funciones Críticas

- `procesar_mensaje()` - Procesamiento principal de mensajes
- `cargar_inventario()` - Carga Excel y convierte a texto IA
- `enviar_mensaje_whatsapp()` - Envío con división automática
- `tiene_sesion_activa()` - Control de acceso por sesión
- `formatear_historial()` - Memoria conversacional para IA

---

## 🎯 Comportamiento del Bot

### Estados del Bot

1. **Sin sesión**: Completamente silencioso, ignora todos los mensajes
2. **Comando `/inventario`**: Inicia sesión, envía bienvenida, activa respuestas
3. **Con sesión activa**: Responde a consultas, mantiene memoria, usa Gemini
4. **Comando `/fin`**: Termina sesión, envía despedida, vuelve a silencioso

### Tipos de Consultas Soportadas

- **Categorías**: "categorías", "todas las categorías"
- **Búsquedas**: "buscar laptop", "productos Samsung"
- **Cálculos**: "stock total", "valor total del inventario"
- **Naturales**: "algo bonito para mi mamá", "para el frío"
- **Específicas**: "precio de...", "stock de...", "cuántos..."

### Respuestas del Bot

- **Formato estructurado**: Productos con campos relevantes
- **Totales incluidos**: Stock, valores, cantidades cuando aplique
- **Errores amigables**: Mensajes claros cuando no encuentra datos
- **División automática**: Respuestas largas en múltiples mensajes

---

## 🔧 Para IA: Cómo Modificar

### Cambios Comunes

1. **Agregar comandos**: Modificar `procesar_mensaje()` línea ~570
2. **Nuevas búsquedas**: Agregar detección en línea ~620
3. **Cambiar prompts**: Modificar prompt Gemini línea ~630
4. **Ajustar respuestas**: Cambiar mensajes bienvenida/despedida
5. **Configurar APIs**: Cambiar keys en líneas 25-30

### Puntos de Extensión

- **Análisis de imágenes**: Agregar procesamiento de `imageMessage`
- **Base de datos**: Reemplazar Excel con SQLite/PostgreSQL
- **Múltiples canales**: Agregar Telegram, Discord endpoints
- **Dashboard web**: Agregar rutas Flask adicionales
- **Notificaciones**: Sistema de alertas automáticas

### Consideraciones Importantes

- **Mantener sesiones**: Sistema de control es crítico para seguridad
- **Memory management**: Limpiar memoria en `/fin` para eficiencia
- **Error handling**: Bot debe ser robusto ante fallos
- **Message limits**: WhatsApp tiene límite 4000 chars, respetar división
- **Rate limiting**: Considerar límites de API Gemini/Evolution

---

## 🚀 Estado de Producción

### Servidor Activo

- **IP**: 107.170.78.13
- **Puerto**: 8000
- **Status**: ✅ Funcionando 24/7
- **Uptime**: Estable desde último deploy
- **Logs**: Sistema de logging configurado

### Métricas de Uso

- **Inventario**: 672 productos cargados
- **Memoria**: Gestión automática por usuario
- **Sesiones**: Control estricto funcionando
- **WhatsApp**: Integración estable con Evolution API
- **Gemini**: Respuestas consistentes y precisas

### Mantenimiento

- **Archivos limpios**: Solo esenciales después de cleanup
- **Documentación completa**: 3 archivos MD detallados
- **Código documentado**: Comentarios en español
- **Funciones testeadas**: Sistema robusto y confiable

---

## 🎓 Instrucciones para IA

### Cuando el Usuario Pida Modificaciones:

1. **Leer código actual** con `read_file()` si necesitas contexto
2. **Usar `replace_string_in_file()`** para cambios específicos
3. **Incluir 3-5 líneas de contexto** antes y después
4. **Probar cambios** si es posible
5. **Explicar qué se modificó** y por qué

### Cuando el Usuario Pregunte sobre Funcionalidad:

1. **Referirse a esta documentación** como base
2. **Explicar estado actual** del proyecto
3. **Sugerir mejoras realistas** basadas en arquitectura actual
4. **Mantener enfoque empresarial** (es un bot de inventario para negocio)

### Cuando el Usuario Reporte Errores:

1. **Revisar logs** si están disponibles
2. **Verificar configuración** de APIs
3. **Comprobar estructura de archivos**
4. **Sugerir solución específica** basada en el error

### Lo Que NO Hacer:

- ❌ No sugerir reescribir desde cero (está funcionando)
- ❌ No cambiar arquitectura sin justificación clara
- ❌ No romper sistema de sesiones (es crítico)
- ❌ No eliminar funcionalidad existente sin consultar
- ❌ No sugerir tecnologías complejas para cambios simples

---

## 🏆 Logros del Proyecto

✅ **Bot empresarial funcional** integrado con WhatsApp
✅ **IA conversacional** con Gemini para consultas naturales  
✅ **Inventario Excel** integrado con 672 productos
✅ **Control de sesiones** estricto para seguridad
✅ **Memoria conversacional** por usuario
✅ **División automática** de mensajes largos
✅ **Búsquedas semánticas** inteligentes
✅ **Cálculos automáticos** de stock y valores
✅ **Código limpio** y bien documentado
✅ **Despliegue en producción** estable

**Este es un proyecto maduro y funcional listo para uso empresarial.**
