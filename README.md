# 🤖 ChatBot WhatsApp + Gemini con Inventario

## 📋 Descripción del Proyecto

Este es un chatbot inteligente que integra **WhatsApp**, **Google Gemini AI** y **Excel** para proporcionar un sistema completo de consultas de inventario empresarial. El bot funciona con un sistema de sesiones controladas y memoria conversacional.

### 🎯 Características Principales

- ✅ **Integración WhatsApp**: Usa Evolution API para comunicación
- ✅ **IA Avanzada**: Google Gemini 2.5-flash para respuestas inteligentes
- ✅ **Inventario Excel**: Lee y analiza archivos Excel con productos
- ✅ **Control de Sesiones**: Sistema `/inventario` → `/fin` para controlar acceso
- ✅ **Memoria Conversacional**: Recuerda los últimos 10 mensajes por usuario
- ✅ **Búsquedas Inteligentes**: Búsquedas semánticas y por palabras clave
- ✅ **Cálculos Automáticos**: Stock total, valores, estadísticas
- ✅ **División de Mensajes**: Maneja automáticamente mensajes largos
- ✅ **Seguridad**: Solo responde dentro de sesiones activas

## 🏗️ Arquitectura del Sistema

```
┌─────────────────┐    ┌────────────────┐    ┌─────────────────┐
│   WhatsApp      │◄──►│  Evolution API │◄──►│ Servidor Flask  │
│   (Usuario)     │    │   (Cloud)      │    │ (Tu Servidor)   │
└─────────────────┘    └────────────────┘    └─────────────────┘
                                                      │
                                              ┌───────▼────────┐
                                              │   Gemini AI    │
                                              │ (Google Cloud) │
                                              └────────────────┘
                                                      │
                                              ┌───────▼────────┐
                                              │ Inventario.xlsx│
                                              │  (672 prod.)   │
                                              └────────────────┘
```

## 📂 Estructura del Proyecto

```
chatbotia/gemini-chatbot/
├── servidor_webhook.py          # 🎯 Archivo principal del bot
├── requirements_whatsapp.txt    # 📦 Dependencias de Python
├── .env                        # 🔐 Variables de entorno (vacío)
├── README.md                   # 📖 Esta documentación
└── Inventario_Completo.xlsx    # 📊 Base de datos de productos
```

## 🔧 Configuración

### 🔐 Variables de Entorno

Este proyecto usa variables de entorno para mantener las API keys seguras.

1. **Copia el archivo de ejemplo:**

   ```bash
   cp .env.example .env
   ```

2. **Edita el archivo `.env` con tus credenciales:**

   ```env
   # 🤖 GEMINI AI CONFIGURATION
   GEMINI_API_KEY=tu_gemini_api_key_aqui

   # 📱 EVOLUTION API CONFIGURATION
   EVOLUTION_API_URL=tu_evolution_api_url_aqui
   EVOLUTION_API_KEY=tu_evolution_api_key_aqui
   INSTANCE_NAME=tu_instancia_whatsapp

   # 🔒 SEGURIDAD
   WEBHOOK_SECRET=tu_webhook_secret_seguro
   FLASK_SECRET_KEY=tu_flask_secret_key_seguro
   ```

### 📊 Configuración del Inventario

- Coloca tu archivo Excel en la raíz del proyecto
- Por defecto busca: `Inventario_Completo.xlsx`
- Hoja por defecto: `Productos`
- Puedes cambiar estos valores en el archivo `.env`

## 🚀 Instalación y Uso

### 1. Instalación de Dependencias

```bash
pip install -r requirements_whatsapp.txt
```

### 2. Ejecutar el Servidor

```bash
python servidor_webhook.py
```

### 3. Configurar Webhook en Evolution API

El webhook debe apuntar a: `http://107.170.78.13:8000/webhook`

### 4. Uso del Bot

1. **Iniciar sesión**: Enviar `/inventario` por WhatsApp
2. **Hacer consultas**: Cualquier pregunta sobre productos
3. **Terminar sesión**: Enviar `/fin`

## 💬 Comandos y Funcionalidades

### Comandos de Control

| Comando       | Descripción                    |
| ------------- | ------------------------------ |
| `/inventario` | Inicia sesión de consultas     |
| `/fin`        | Termina sesión y borra memoria |

### Consultas Disponibles

| Tipo            | Ejemplos                                    |
| --------------- | ------------------------------------------- |
| **Búsquedas**   | "buscar cámaras", "productos Samsung"       |
| **Categorías**  | "categorías", "todas las categorías"        |
| **Cálculos**    | "stock total", "valor total del inventario" |
| **Precios**     | "precio de laptop HP", "productos baratos"  |
| **Específicas** | "algo para regalo", "para el frío"          |

### Búsquedas Inteligentes

El bot entiende consultas naturales:

- "Algo bonito para mi mamá" → Encuentra joyas, perfumes, etc.
- "Para el frío" → Encuentra chamarras, mantas, etc.
- "Cámara para galpón 20x20" → Busca por características
