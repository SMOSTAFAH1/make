# 🤖 Instagram Downloader Bot

Bot de Telegram que descarga automáticamente videos de Instagram usando savegram.app

## 🚀 Características

- ✅ Descarga automática de videos de Instagram
- ✅ Soporta Reels, Posts, IGTV y Stories
- ✅ Interfaz simple por Telegram
- ✅ Descarga directa de archivos MP4
- ✅ Navegación web automatizada

## 📋 Requisitos

- Python 3.7+
- Google Chrome instalado
- Conexión a internet

## 🛠️ Instalación

1. **Clona o descarga este proyecto**

2. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **El ChromeDriver ya está incluido en la carpeta `drivers/`**

## 🎯 Uso

1. **Inicia el bot:**
   ```bash
   python start_bot.py
   ```

2. **En Telegram:**
   - Busca tu bot usando el token proporcionado
   - Envía `/start` para comenzar
   - Pega cualquier enlace de Instagram
   - ¡Recibe tu video descargado automáticamente!

## 📱 Formatos soportados

- `https://www.instagram.com/p/xxxxx/` - Posts
- `https://www.instagram.com/reel/xxxxx/` - Reels  
- `https://www.instagram.com/tv/xxxxx/` - IGTV
- `https://www.instagram.com/stories/xxxxx/` - Stories

## 🔧 Configuración

El token del bot está configurado en `make.py`:
```python
BOT_TOKEN = "8169625627:AAFQ5eBXUrlzs65J8AZeUtgiIXhFZah35C4"
```

## 🛡️ Características de seguridad

- Navegación headless (invisible)
- Evasión de detección de bots
- Manejo de errores robusto
- Archivos temporales autolimpiados

## 📝 Logs

El bot registra toda la actividad para debugging:
- Mensajes recibidos
- URLs procesadas  
- Errores de descarga
- Estado del navegador

## ⚠️ Notas importantes

- Respeta los términos de servicio de Instagram
- El bot usa savegram.app como servicio de descarga
- Algunos videos pueden requerir autenticación
- La velocidad depende de tu conexión a internet

## 🔄 Actualizaciones futuras

- [ ] Soporte para múltiples enlaces
- [ ] Descarga de fotos
- [ ] Integración con bases de datos
- [ ] Programación de descargas
- [ ] Conversión automática de formatos
