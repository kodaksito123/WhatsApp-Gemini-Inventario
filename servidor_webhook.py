#!/usr/bin/env python3
"""
🤖 CHATBOT EMPRESARIAL: WhatsApp + Gemini + Excel Inventario
================================================================================

DESCRIPCIÓN:
Este es un chatbot empresarial completo que integra WhatsApp, Google Gemini AI 
y análisis de inventario Excel. Funciona con control de sesiones estricto.

ARQUITECTURA:
WhatsApp ↔ Evolution API ↔ Flask Webhook ↔ Gemini AI ↔ Excel Reader

FUNCIONAMIENTO:
1. Usuario envía /inventario → Inicia sesión
2. Bot responde a consultas naturales sobre inventario
3. Usuario envía /fin → Termina sesión
4. Sin sesión activa → Bot completamente silencioso

CARACTERÍSTICAS:
✅ Control de sesiones (/inventario → /fin)
✅ Memoria conversacional (10 mensajes por usuario)
✅ Búsquedas semánticas inteligentes
✅ Cálculos automáticos (stock, valores, estadísticas)
✅ División automática de mensajes largos
✅ Integración completa con Excel (672 productos)
✅ Manejo robusto de errores

SERVIDOR: http://107.170.78.13:8000
WEBHOOK: http://107.170.78.13:8000/webhook
STATUS:  http://107.170.78.13:8000/status

AUTOR: Sistema automatizado
FECHA: 2025
VERSIÓN: Producción estable
"""

from flask import Flask, request, jsonify
import requests
import google.generativeai as genai
import logging
import pandas as pd
from pathlib import Path
import os
from dotenv import load_dotenv

# Cargar variables de entorno al inicio
load_dotenv()

# ============================================================================
# 🔧 CONFIGURACIÓN DEL SISTEMA
# ============================================================================
"""
Esta sección contiene todas las configuraciones críticas del chatbot.
Las variables sensibles se cargan desde .env para seguridad.
"""

# 🤖 GEMINI AI CONFIGURATION
# API Key para Google Gemini (IA conversacional) - Desde .env
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY no encontrada. Verifica tu archivo .env")

# 📱 EVOLUTION API CONFIGURATION (WhatsApp Cloud Service)
# Servicio cloud para integración WhatsApp empresarial - Desde .env
EVOLUTION_API_URL = os.getenv('EVOLUTION_API_URL')
EVOLUTION_API_KEY = os.getenv('EVOLUTION_API_KEY')
INSTANCE_NAME = os.getenv('INSTANCE_NAME', 'whatsapp-bot')

if not EVOLUTION_API_URL or not EVOLUTION_API_KEY:
    raise ValueError("❌ Configuración de Evolution API incompleta. Verifica tu archivo .env")

# 📊 INVENTARIO EXCEL CONFIGURATION
# Configuración del archivo Excel con productos empresariales - Desde .env
ARCHIVO_INVENTARIO = os.getenv('ARCHIVO_INVENTARIO', 'Inventario_Completo.xlsx')
HOJA_PRODUCTOS = os.getenv('HOJA_PRODUCTOS', 'Productos')

# 🔒 CONFIGURACIONES DE SEGURIDAD
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', 'webhook_secret_default')
FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'flask_secret_default')

# 🚀 CONFIGURACIÓN DE SERVIDOR
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
PORT = int(os.getenv('PORT', 8000))

# ============================================================================
# 🤖 INICIALIZACIÓN DE GEMINI AI
# ============================================================================
"""
Configuración y inicialización del modelo de IA Google Gemini.
Modelo usado: gemini-2.5-flash (optimizado para velocidad y precisión)
"""

def inicializar_gemini():
    """
    Inicializa el cliente de Google Gemini AI
    
    Returns:
        GenerativeModel: Instancia del modelo Gemini o None si hay error
    
    Nota: Esta función se ejecuta automáticamente al iniciar el servidor
    """
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.5-flash")
        print("✅ Gemini inicializado correctamente")
        return model
    except Exception as e:
        print(f"❌ Error inicializando Gemini: {e}")
        return None

# ============================================================================
# 📊 FUNCIONES PARA LEER INVENTARIO
# ============================================================================

# Variable global para almacenar el DataFrame completo
df_inventario = None

def cargar_inventario():
    """Carga el inventario desde el archivo Excel y lo convierte a texto para la IA"""
    global df_inventario
    try:
        # Buscar archivo en diferentes ubicaciones
        posibles_rutas = [
            Path(ARCHIVO_INVENTARIO),
            Path("..") / ARCHIVO_INVENTARIO,
            Path("../..") / ARCHIVO_INVENTARIO,
            Path("/opt/webhook") / ARCHIVO_INVENTARIO
        ]
        
        archivo_encontrado = None
        for ruta in posibles_rutas:
            if ruta.exists():
                archivo_encontrado = str(ruta)
                break
        
        if not archivo_encontrado:
            print(f"⚠️ No se encontró el archivo {ARCHIVO_INVENTARIO}")
            return None
        
        print(f"📊 Cargando inventario desde: {archivo_encontrado}")
        
        # Leer la hoja de productos y guardar DataFrame completo
        df_inventario = pd.read_excel(archivo_encontrado, sheet_name=HOJA_PRODUCTOS)
        
        # Convertir a texto legible para la IA
        texto_inventario = convertir_inventario_a_texto(df_inventario)
        
        print(f"✅ Inventario cargado: {len(df_inventario)} productos")
        return texto_inventario
        
    except Exception as e:
        print(f"❌ Error cargando inventario: {e}")
        return None

def convertir_inventario_a_texto(df):
    """Convierte el DataFrame del inventario a texto legible para la IA - TODOS los campos disponibles"""
    try:
        # Limpiar datos
        df = df.fillna("")  # Reemplazar valores NaN con cadena vacía
        
        # Crear texto estructurado con TODOS los campos
        texto = "=== INVENTARIO COMPLETO DE PRODUCTOS ===\n\n"
        texto += f"Total de productos: {len(df)}\n"
        texto += f"Campos disponibles: {', '.join(df.columns)}\n\n"
        
        # Agregar cada producto con TODOS sus campos
        for index, row in df.iterrows():
            texto += f"PRODUCTO {index + 1}:\n"
            
            # Mostrar TODAS las columnas disponibles
            for columna in df.columns:
                valor = str(row[columna]).strip()
                if valor and valor != "" and valor.lower() != "nan":
                    # Formatear nombre de columna más legible
                    nombre_campo = columna.replace('_', ' ').title()
                    texto += f"  {nombre_campo}: {valor}\n"
            texto += "\n"
        
        return texto
        
    except Exception as e:
        print(f"❌ Error convirtiendo inventario a texto: {e}")
        return "Error al procesar inventario"

def obtener_todas_las_categorias():
    """Extrae todas las categorías únicas del inventario"""
    global df_inventario
    if df_inventario is None:
        return "No hay inventario disponible"
    
    try:
        # Buscar columna de categoría
        columnas_categoria = ['categoria', 'categoría', 'category', 'tipo_categoria', 'tipo']
        columna_encontrada = None
        
        for col in df_inventario.columns:
            if any(cat.lower() in col.lower() for cat in columnas_categoria):
                columna_encontrada = col
                break
        
        if not columna_encontrada:
            return "No se encontró columna de categoría en el inventario"
        
        # Obtener categorías únicas
        categorias = df_inventario[columna_encontrada].dropna().unique()
        categorias = [str(cat).strip() for cat in categorias if str(cat).strip() and str(cat).lower() != 'nan']
        
        # Formatear respuesta
        resultado = "📋 **TODAS LAS CATEGORÍAS DISPONIBLES:**\n\n"
        for i, categoria in enumerate(sorted(categorias), 1):
            resultado += f"{i}. {categoria}\n"
        
        resultado += f"\n**Total de categorías: {len(categorias)}**"
        return resultado
        
    except Exception as e:
        return f"Error obteniendo categorías: {e}"

def calcular_stock_total():
    """Calcula el stock total de todos los productos"""
    global df_inventario
    if df_inventario is None:
        return "No hay inventario disponible"
    
    try:
        # Buscar columna de stock
        columnas_stock = ['stock_actual', 'stock', 'cantidad', 'existencias', 'disponible']
        columna_encontrada = None
        
        for col in df_inventario.columns:
            if any(stock.lower() in col.lower() for stock in columnas_stock):
                columna_encontrada = col
                break
        
        if not columna_encontrada:
            return "No se encontró columna de stock en el inventario"
        
        # Convertir a numérico y sumar
        stock_numerico = pd.to_numeric(df_inventario[columna_encontrada], errors='coerce')
        stock_total = stock_numerico.sum()
        productos_con_stock = stock_numerico.notna().sum()
        
        resultado = f"📊 **RESUMEN DE STOCK:**\n\n"
        resultado += f"• Stock total: **{stock_total:,.0f}** unidades\n"
        resultado += f"• Productos con stock registrado: **{productos_con_stock}**\n"
        resultado += f"• Promedio por producto: **{stock_total/productos_con_stock:.1f}** unidades"
        
        return resultado
        
    except Exception as e:
        return f"Error calculando stock: {e}"

def calcular_valor_inventario():
    """Calcula el valor total del inventario"""
    global df_inventario
    if df_inventario is None:
        return "No hay inventario disponible"
    
    try:
        # Buscar columnas de precio y stock
        columnas_precio = ['precio', 'price', 'valor', 'costo']
        columnas_stock = ['stock_actual', 'stock', 'cantidad', 'existencias']
        
        col_precio = None
        col_stock = None
        
        for col in df_inventario.columns:
            if any(precio.lower() in col.lower() for precio in columnas_precio):
                col_precio = col
            if any(stock.lower() in col.lower() for stock in columnas_stock):
                col_stock = col
        
        if not col_precio:
            return "No se encontró columna de precio en el inventario"
        if not col_stock:
            return "No se encontró columna de stock en el inventario"
        
        # Calcular valor total
        precios = pd.to_numeric(df_inventario[col_precio], errors='coerce')
        stocks = pd.to_numeric(df_inventario[col_stock], errors='coerce')
        
        valores_producto = precios * stocks
        valor_total = valores_producto.sum()
        productos_valorados = valores_producto.notna().sum()
        
        resultado = f"💰 **VALOR DEL INVENTARIO:**\n\n"
        resultado += f"• Valor total: **${valor_total:,.2f}**\n"
        resultado += f"• Productos valorados: **{productos_valorados}**\n"
        resultado += f"• Valor promedio por producto: **${valor_total/productos_valorados:.2f}**"
        
        return resultado
        
    except Exception as e:
        return f"Error calculando valor: {e}"

def buscar_productos_especificos(terminos):
    """Busca productos específicos y puede calcular totales"""
    global df_inventario
    if df_inventario is None:
        return "No hay inventario disponible"
    
    try:
        # Buscar productos que coincidan
        mask = df_inventario.astype(str).apply(
            lambda x: x.str.contains('|'.join(terminos), case=False, na=False)
        ).any(axis=1)
        
        productos_encontrados = df_inventario[mask]
        
        if len(productos_encontrados) == 0:
            return f"No se encontraron productos con: {', '.join(terminos)}"
        
        # Buscar columnas relevantes
        col_precio = None
        col_stock = None
        for col in df_inventario.columns:
            if any(p in col.lower() for p in ['precio', 'price', 'valor', 'costo']):
                col_precio = col
            if any(s in col.lower() for s in ['stock', 'cantidad', 'existencias']):
                col_stock = col
        
        resultado = f"🔍 **PRODUCTOS ENCONTRADOS: {len(productos_encontrados)}**\n\n"
        
        # Mostrar productos encontrados con campos relevantes para mostrar al usuario
        campos_mostrar = ['marca', 'categoria', 'tipo', 'stock', 'precio', 'caracteristica', 'observaciones']
        
        for idx, row in productos_encontrados.iterrows():
            resultado += f"**Producto {idx + 1}:**\n"
            
            # Mostrar todos los campos relevantes que existan
            for col in df_inventario.columns:
                col_lower = col.lower()
                if any(campo in col_lower for campo in campos_mostrar):
                    valor = str(row[col]).strip()
                    if valor and valor.lower() != 'nan':
                        nombre_campo = col.replace('_', ' ').title()
                        resultado += f"  {nombre_campo}: {valor}\n"
            resultado += "\n"
        
        # Calcular totales si hay precio y stock
        if col_precio and col_stock:
            precios = pd.to_numeric(productos_encontrados[col_precio], errors='coerce')
            stocks = pd.to_numeric(productos_encontrados[col_stock], errors='coerce')
            
            total_stock = stocks.sum()
            valor_total = (precios * stocks).sum()
            
            resultado += f"📊 **TOTALES:**\n"
            resultado += f"• Stock total: {total_stock:,.0f} unidades\n"
            resultado += f"• Valor total: ${valor_total:,.2f}\n"
        
        return resultado
        
    except Exception as e:
        return f"Error en búsqueda: {e}"

# ============================================================================
# 📱 FUNCIONES DE WHATSAPP
# ============================================================================

def enviar_mensaje_whatsapp(numero, mensaje):
    """Envía un mensaje por WhatsApp, verificando límites y dividiendo automáticamente"""
    try:
        LIMITE_WHATSAPP = 4000
        
        # Verificar límite ANTES de enviar
        if len(mensaje) <= LIMITE_WHATSAPP:
            # Mensaje normal
            return enviar_mensaje_simple(numero, mensaje)
        
        # Mensaje largo - dividir automáticamente
        logger.info(f"📏 Mensaje largo detectado ({len(mensaje)} caracteres). Dividiendo...")
        
        partes = dividir_mensaje(mensaje, LIMITE_WHATSAPP)
        logger.info(f"📄 Mensaje dividido en {len(partes)} partes")
        
        # Enviar cada parte con delay
        import time
        for i, parte in enumerate(partes):
            if i == 0:
                # Primera parte sin modificar
                mensaje_enviar = parte
            else:
                # Partes adicionales con numeración
                mensaje_enviar = f"📄 Parte {i+1}/{len(partes)}:\n\n{parte}"
            
            if not enviar_mensaje_simple(numero, mensaje_enviar):
                logger.error(f"❌ Error enviando parte {i+1}/{len(partes)}")
                return False
            
            logger.info(f"✅ Parte {i+1}/{len(partes)} enviada exitosamente")
            
            # Delay entre mensajes (excepto el último)
            if i < len(partes) - 1:
                time.sleep(1)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error enviando mensaje: {e}")
        return False

def enviar_mensaje_simple(numero, mensaje):
    """Envía un mensaje simple por WhatsApp"""
    try:
        url = f"{EVOLUTION_API_URL}/message/sendText/{INSTANCE_NAME}"
        headers = {
            "Content-Type": "application/json",
            "apikey": EVOLUTION_API_KEY
        }
        data = {
            "number": numero,
            "text": mensaje
        }
        
        response = requests.post(url, headers=headers, json=data)
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"❌ Error enviando mensaje simple: {e}")
        return False

def dividir_mensaje(mensaje, limite):
    """Divide un mensaje largo en partes más pequeñas, respetando la estructura de productos"""
    partes = []
    
    # Si el mensaje tiene productos, dividir por productos completos
    if "PRODUCTO " in mensaje:
        return dividir_por_productos(mensaje, limite)
    
    # División normal por líneas
    lineas = mensaje.split('\n')
    parte_actual = ""
    
    for linea in lineas:
        # Si agregar esta línea excede el límite
        if len(parte_actual + linea + '\n') > limite:
            if parte_actual:
                partes.append(parte_actual.strip())
                parte_actual = linea + '\n'
            else:
                # Línea muy larga, cortarla por palabras
                palabras = linea.split()
                linea_temp = ""
                for palabra in palabras:
                    if len(linea_temp + palabra + ' ') > limite:
                        if linea_temp:
                            partes.append(linea_temp.strip())
                            linea_temp = palabra + ' '
                        else:
                            # Palabra muy larga, cortarla
                            partes.append(palabra[:limite])
                            linea_temp = palabra[limite:] + ' '
                    else:
                        linea_temp += palabra + ' '
                parte_actual = linea_temp + '\n'
        else:
            parte_actual += linea + '\n'
    
    # Agregar la última parte
    if parte_actual.strip():
        partes.append(parte_actual.strip())
    
    return partes

def dividir_por_productos(mensaje, limite):
    """Divide un mensaje por productos completos"""
    partes = []
    productos = mensaje.split('PRODUCTO ')
    
    # Mantener el encabezado
    encabezado = productos[0] if productos else ""
    productos = productos[1:] if len(productos) > 1 else []
    
    parte_actual = encabezado
    
    for i, producto in enumerate(productos):
        producto_completo = f"PRODUCTO {producto}"
        
        # Si agregar este producto excede el límite
        if len(parte_actual + producto_completo) > limite:
            if parte_actual.strip():
                partes.append(parte_actual.strip())
                # Comenzar nueva parte con encabezado resumido
                parte_actual = f"=== CONTINUACIÓN INVENTARIO ===\n\n{producto_completo}"
            else:
                # Producto individual muy largo
                partes.append(producto_completo[:limite])
                parte_actual = producto_completo[limite:]
        else:
            parte_actual += producto_completo
    
    # Agregar la última parte
    if parte_actual.strip():
        partes.append(parte_actual.strip())
    
    return partes

# ============================================================================
# 💾 MEMORIA DE CONVERSACIONES
# ============================================================================

# Diccionario para almacenar conversaciones por número de teléfono
conversaciones = {}

# Diccionario para almacenar sesiones activas de inventario
sesiones_activas = {}

def obtener_conversacion(numero):
    """Obtiene el historial de conversación de un usuario"""
    if numero not in conversaciones:
        conversaciones[numero] = []
    return conversaciones[numero]

def agregar_mensaje_a_conversacion(numero, mensaje, es_usuario=True):
    """Agrega un mensaje al historial de conversación"""
    if numero not in conversaciones:
        conversaciones[numero] = []
    
    tipo = "Usuario" if es_usuario else "Bot"
    conversaciones[numero].append(f"{tipo}: {mensaje}")
    
    # Mantener solo los últimos 10 mensajes para no sobrecargar
    if len(conversaciones[numero]) > 10:
        conversaciones[numero] = conversaciones[numero][-10:]

def formatear_historial(numero):
    """Formatea el historial de conversación para incluir en el prompt"""
    historial = obtener_conversacion(numero)
    if not historial:
        return "Primera conversación con este usuario."
    
    return "HISTORIAL DE CONVERSACIÓN:\n" + "\n".join(historial[-6:]) + "\n\n"

def iniciar_sesion_inventario(numero):
    """Inicia una sesión de inventario para un usuario"""
    sesiones_activas[numero] = True
    logger.info(f"🟢 Sesión de inventario iniciada para {numero}")

def finalizar_sesion_inventario(numero):
    """Finaliza una sesión de inventario para un usuario"""
    if numero in sesiones_activas:
        del sesiones_activas[numero]
    if numero in conversaciones:
        del conversaciones[numero]
    logger.info(f"🔴 Sesión de inventario finalizada para {numero}")

def tiene_sesion_activa(numero):
    """Verifica si un usuario tiene una sesión activa"""
    return numero in sesiones_activas

# ============================================================================
# 🌐 SERVIDOR FLASK
# ============================================================================

app = Flask(__name__)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar Gemini al inicio
gemini_model = inicializar_gemini()

# Cargar inventario al inicio
print("📊 Cargando inventario...")
inventario_texto = cargar_inventario()
if inventario_texto:
    print("✅ Inventario cargado exitosamente")
else:
    print("⚠️ Inventario no disponible")

@app.route('/webhook', methods=['POST'])
def webhook():
    """Endpoint principal que recibe mensajes de Evolution API"""
    try:
        # Obtener datos del webhook
        data = request.json
        logger.info(f"📨 Webhook recibido: {data}")

        # Verificar que hay datos
        if not data or 'data' not in data or not data['data']:
            return jsonify({"status": "no_data"}), 200

        # Procesar mensaje(s)
        if isinstance(data['data'], list):
            for message_data in data['data']:
                procesar_mensaje(message_data)
        elif isinstance(data['data'], dict):
            procesar_mensaje(data['data'])
        else:
            logger.error("Formato inesperado en data['data']")

        return jsonify({"status": "success"}), 200

    except Exception as e:
        logger.error(f"❌ Error en webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


def procesar_mensaje(message_data):
    """Procesa un mensaje individual"""
    try:
        # Verificar que es un mensaje de texto
        if message_data.get('messageType') != 'conversation':
            logger.info("📋 Mensaje ignorado (no es conversación)")
            return

        # ⚠️ Eliminado el filtro de "fromMe": ahora responde también a tus propios mensajes

        # Extraer información del mensaje
        remote_jid = message_data['key']['remoteJid']
        numero = remote_jid.replace('@s.whatsapp.net', '')
        mensaje_usuario = message_data['message']['conversation']

        logger.info(f"📱 Mensaje de +{numero}: {mensaje_usuario}")
        
        # ============================================================================
        # 🎯 CONTROL DE SESIONES DE INVENTARIO
        # ============================================================================
        
        # Verificar comando de inicio
        if mensaje_usuario.strip().lower() == "/inventario":
            iniciar_sesion_inventario(numero)
            mensaje_bienvenida = """🎯 **SESIÓN DE INVENTARIO INICIADA**

¡Hola! Ahora puedes preguntarme sobre el inventario:

📋 **Comandos disponibles:**
• "categorías" - Ver todas las categorías
• "stock total" - Calcular stock completo
• "buscar [producto]" - Buscar productos específicos
• "precio [producto]" - Ver precios
• "/fin" - Terminar sesión

¿En qué puedo ayudarte?"""
            
            enviar_mensaje_whatsapp(numero, mensaje_bienvenida)
            return
        
        # Verificar comando de finalización
        if mensaje_usuario.strip().lower() == "/fin":
            if tiene_sesion_activa(numero):
                finalizar_sesion_inventario(numero)
                mensaje_despedida = """👋 **SESIÓN DE INVENTARIO FINALIZADA**

¡Gracias por usar el sistema de inventario!

Para volver a consultar el inventario, escribe: `/inventario`"""
                
                enviar_mensaje_whatsapp(numero, mensaje_despedida)
            else:
                enviar_mensaje_whatsapp(numero, "No tienes una sesión activa. Para iniciar, escribe: `/inventario`")
            return
        
        # Verificar si tiene sesión activa
        if not tiene_sesion_activa(numero):
            # Usuario sin sesión activa - NO RESPONDER (ignorar completamente)
            logger.info(f"❌ Mensaje ignorado de +{numero}: No tiene sesión activa")
            return
        
        # ============================================================================
        # 🤖 PROCESAMIENTO DE MENSAJES (SOLO CON SESIÓN ACTIVA)
        # ============================================================================
        
        # Obtener historial de conversación
        historial = formatear_historial(numero)
        
        # Agregar mensaje del usuario al historial
        agregar_mensaje_a_conversacion(numero, mensaje_usuario, es_usuario=True)
        
        # Generar respuesta con Gemini
        if gemini_model:
            try:
                # Detectar tipo de consulta y generar datos específicos
                mensaje_lower = mensaje_usuario.lower()
                datos_especificos = ""
                
                # Consultas específicas que requieren análisis completo
                if any(palabra in mensaje_lower for palabra in ['categorías', 'categorias', 'todas las categorias']):
                    datos_especificos = obtener_todas_las_categorias()
                elif any(palabra in mensaje_lower for palabra in ['suma', 'total', 'stock total', 'cuanto stock']):
                    datos_especificos = calcular_stock_total()
                elif any(palabra in mensaje_lower for palabra in ['valor total', 'costo total', 'precio total']):
                    datos_especificos = calcular_valor_inventario()
                elif any(palabra in mensaje_lower for palabra in ['buscar', 'mostrar', 'productos']):
                    # Extraer términos de búsqueda
                    palabras = mensaje_usuario.split()
                    terminos = [p for p in palabras if len(p) > 2 and p.lower() not in ['buscar', 'mostrar', 'productos', 'dame', 'quiero']]
                    if terminos:
                        datos_especificos = buscar_productos_especificos(terminos)
                
                # Usar prompt unificado para todas las consultas
                if inventario_texto:
                    prompt = f"""
Eres un BOT de WhatsApp especializado en ayudar a clientes con consultas sobre inventario.

{historial}

CAPACIDADES Y REGLAS:


2. CONSULTAS NATURALES:
   - Entiende preguntas en lenguaje cotidiano como:
     "búscame una cámara buena para un galpón de 20x20"
     "qué notebooks tienen HDMI"
     "quiero un producto barato de la categoría impresoras"
   - Extrae las palabras clave (ej: "cámara", "HDMI", "galpón 20x20") y relaciónalas con los campos del inventario (Marca, Categoría, Tipo, Características, Observaciones, Precio).
   - Si el inventario no tiene esa información, responde:  
     "⚠️ Esa característica no está registrada en el inventario."

3. CATEGORÍAS:
   - Si piden categorías, muestra la lista completa de categorías únicas.

4. CÁLCULOS MATEMÁTICOS:
   ✅ Sumar stock total de productos  
   ✅ Calcular valores y precios totales  
   ✅ Contar productos por categoría  
   ✅ Sacar promedios y estadísticas  
   ✅ Operaciones matemáticas básicas  

5. BÚSQUEDAS Y RESPUESTAS:
   - Usa TODOS los campos disponibles del inventario.  
   - Al mostrar productos, prioriza: Marca, Categoría, Tipo, Stock, Precio, Características, Observaciones, Valor de venta.  
   - Ignora mayúsculas/minúsculas.  
   - Tolera errores de escritura de 1–2 letras.  
   - Incluye totales y cálculos si son relevantes.

6. LIMITACIONES:
   - No inventes datos que no estén en el inventario.  
   - Sé claro, breve y útil.  
   - Si el usuario pide una recomendación contextual (ej: “para un galpón 20x20”), usa lo que tengas en características/observaciones, pero nunca inventes compatibilidades técnicas.

DATOS ESPECÍFICOS PARA ESTA CONSULTA:
{datos_especificos}

INVENTARIO DISPONIBLE:
{inventario_texto}

Mensaje actual del cliente:
"{mensaje_usuario}"

Responde siguiendo las reglas anteriores. Interpreta la intención del usuario aunque no use comandos exactos.
"""
                
                respuesta = gemini_model.generate_content(prompt)
                respuesta_texto = respuesta.text
                
                # Agregar respuesta del bot al historial
                agregar_mensaje_a_conversacion(numero, respuesta_texto, es_usuario=False)
                
                logger.info(f"🤖 Respuesta generada: {respuesta_texto[:100]}...")
                
                # Enviar respuesta (la función ya maneja la división automáticamente)
                if enviar_mensaje_whatsapp(numero, respuesta_texto):
                    logger.info("✅ Respuesta enviada exitosamente")
                else:
                    logger.error("❌ Error enviando respuesta")
                    
            except Exception as e:
                logger.error(f"❌ Error con Gemini: {e}")
                # Enviar mensaje de error
                error_msg = "❌ Disculpa, tuve un problema procesando tu mensaje. ¿Podrías intentar de nuevo?"
                enviar_mensaje_whatsapp(numero, error_msg)
        else:
            logger.error("❌ Gemini no está inicializado")
            
    except Exception as e:
        logger.error(f"❌ Error procesando mensaje: {e}")

@app.route('/status', methods=['GET'])
def status():
    """Endpoint para verificar que el servidor está funcionando"""
    return jsonify({
        "status": "running",
        "bot": "WhatsApp + Gemini Webhook",
        "gemini": "initialized" if gemini_model else "error",
        "inventario": "loaded" if inventario_texto else "not_available",
        "webhook": "active",
        "conversaciones_activas": len(conversaciones),
        "sesiones_inventario_activas": len(sesiones_activas),
        "memoria": "enabled",
        "control_sesiones": "enabled"
    }), 200

@app.route('/', methods=['GET'])
def home():
    """Página de inicio"""
    return """
    <h1>🤖 Bot WhatsApp + Gemini</h1>
    <p>✅ Servidor webhook funcionando</p>
    <p>📡 Endpoint: /webhook</p>
    <p>📊 Estado: /status</p>
    <hr>
    <h2>🎯 Control de Sesiones</h2>
    <p><strong>/inventario</strong> - Iniciar sesión de inventario</p>
    <p><strong>/fin</strong> - Terminar sesión</p>
    <p>El bot solo responde dentro de sesiones activas</p>
    """

# ============================================================================
# 🚀 EJECUCIÓN
# ============================================================================

if __name__ == "__main__":
    print("🤖 Iniciando servidor webhook WhatsApp + Gemini")
    print("=" * 50)
    print("🌐 URL: http://107.170.78.13:8000")
    print("📡 Webhook: http://107.170.78.13:8000/webhook")
    print(f"📊 Estado: http://0.0.0.0:{PORT}/status")
    print("=" * 50)
    
    # Ejecutar servidor usando configuración desde .env
    app.run(host='0.0.0.0', port=PORT, debug=(FLASK_ENV == 'development'))
