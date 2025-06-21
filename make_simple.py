#!/usr/bin/env python3
"""
Bot de Telegram para descargar videos de Instagram usando savegram.app
Versión simplificada usando requests directamente
"""

import os
import re
import requests
import tempfile
import time
import json
from urllib.parse import urlparse, parse_qs
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Token del bot
BOT_TOKEN = "8169625627:AAFQ5eBXUrlzs65J8AZeUtgiIXhFZah35C4"

class InstagramDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def is_instagram_url(self, url):
        """Verificar si la URL es de Instagram"""
        instagram_patterns = [
            r'https?://(?:www\.)?instagram\.com/.*',
            r'https?://(?:www\.)?instagram\.com/p/.*',
            r'https?://(?:www\.)?instagram\.com/reel/.*',
            r'https?://(?:www\.)?instagram\.com/tv/.*'
        ]
        
        for pattern in instagram_patterns:
            if re.match(pattern, url):
                return True
        return False
    
    def download_from_savegram_api(self, instagram_url):
        """Descargar video usando una API alternativa más directa"""
        try:
            # Intentar con varios endpoints de descarga
            apis = [
                "https://savegram.app/en/api/ajaxSearch",
                "https://api.downloadgram.com/",
                "https://www.instagram.com/api/v1/media/web_info/"
            ]
            
            for api_url in apis:
                try:
                    if "savegram" in api_url:
                        # Probar con savegram
                        data = {
                            'q': instagram_url,
                            'vt': 'home',
                            't': 'media'
                        }
                        
                        response = self.session.post(api_url, data=data)
                        
                        if response.status_code == 200:
                            result = response.json()
                            
                            # Buscar enlaces de video en la respuesta
                            if 'data' in result:
                                html_content = result['data']
                                
                                # Extraer enlaces de descarga usando regex
                                video_links = re.findall(r'href="([^"]*\.mp4[^"]*)"', html_content)
                                if not video_links:
                                    video_links = re.findall(r'href="([^"]*video[^"]*)"', html_content)
                                
                                if video_links:
                                    video_url = video_links[0]
                                    return self.download_video_file(video_url)
                    
                except Exception as e:
                    logger.error(f"Error con API {api_url}: {e}")
                    continue
            
            # Si las APIs fallan, intentar scraping directo
            return self.download_direct_scraping(instagram_url)
            
        except Exception as e:
            logger.error(f"Error general: {e}")
            return None, f"Error procesando la descarga: {str(e)}"
    
    def download_direct_scraping(self, instagram_url):
        """Método de respaldo usando scraping directo de savegram"""
        try:
            # Ir a savegram y enviar el formulario
            savegram_url = "https://savegram.app/en"
            
            # Obtener la página principal
            response = self.session.get(savegram_url)
            if response.status_code != 200:
                return None, "No se pudo acceder a Savegram"
            
            # Enviar el formulario con la URL de Instagram
            form_data = {
                'url': instagram_url,
                'submit': 'Download'
            }
            
            # Hacer POST al formulario
            response = self.session.post(savegram_url, data=form_data)
            
            if response.status_code == 200:
                html_content = response.text
                
                # Buscar enlaces de descarga en el HTML
                video_patterns = [
                    r'href="([^"]*\.mp4[^"]*)"[^>]*download',
                    r'href="([^"]*\.mp4[^"]*)"',
                    r'data-href="([^"]*\.mp4[^"]*)"',
                    r'src="([^"]*\.mp4[^"]*)"'
                ]
                
                for pattern in video_patterns:
                    matches = re.findall(pattern, html_content)
                    if matches:
                        video_url = matches[0]
                        return self.download_video_file(video_url)
                
                return None, "No se encontraron enlaces de descarga"
            else:
                return None, "Error procesando en Savegram"
                
        except Exception as e:
            logger.error(f"Error en scraping directo: {e}")
            return None, f"Error en scraping: {str(e)}"
    
    def download_video_file(self, video_url):
        """Descargar el archivo de video"""
        try:
            # Si la URL es relativa, hacerla absoluta
            if video_url.startswith('//'):
                video_url = 'https:' + video_url
            elif video_url.startswith('/'):
                video_url = 'https://savegram.app' + video_url
            
            # Descargar el video
            video_response = self.session.get(video_url, stream=True)
            
            if video_response.status_code == 200:
                # Crear archivo temporal
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
                    for chunk in video_response.iter_content(chunk_size=8192):
                        if chunk:
                            temp_file.write(chunk)
                    return temp_file.name, "Video descargado exitosamente"
            else:
                return None, f"Error descargando video: {video_response.status_code}"
                
        except Exception as e:
            logger.error(f"Error descargando archivo: {e}")
            return None, f"Error descargando archivo: {str(e)}"

# Instancia del descargador
downloader = InstagramDownloader()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /start"""
    await update.message.reply_text(
        "¡Hola! 👋\n\n"
        "Envíame un enlace de Instagram y te descargaré el video automáticamente.\n\n"
        "Formatos soportados:\n"
        "• Posts de Instagram\n"
        "• Reels\n"
        "• IGTV\n\n"
        "Solo pega el enlace y yo me encargo del resto! 🚀"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manejar mensajes con enlaces de Instagram"""
    message_text = update.message.text
    
    # Verificar si el mensaje contiene una URL de Instagram
    if not downloader.is_instagram_url(message_text):
        await update.message.reply_text(
            "Por favor, envía un enlace válido de Instagram.\n\n"
            "Ejemplo: https://www.instagram.com/p/..."
        )
        return
    
    # Mensaje de procesamiento
    processing_msg = await update.message.reply_text("🔄 Procesando tu enlace... esto puede tomar unos segundos.")
    
    try:
        # Descargar el video
        video_path, message = downloader.download_from_savegram_api(message_text)
        
        if video_path and os.path.exists(video_path):
            # Verificar que el archivo no esté vacío
            if os.path.getsize(video_path) > 0:
                # Enviar el video
                await update.message.reply_text("✅ ¡Video descargado! Enviando...")
                
                with open(video_path, 'rb') as video_file:
                    await update.message.reply_video(
                        video=video_file,
                        caption="📱 Video descargado de Instagram"
                    )
                
                # Limpiar archivo temporal
                os.unlink(video_path)
                
                # Eliminar mensaje de procesamiento
                await processing_msg.delete()
            else:
                await processing_msg.edit_text("❌ Error: El archivo descargado está vacío")
                os.unlink(video_path)
        else:
            await processing_msg.edit_text(f"❌ Error: {message}")
            
    except Exception as e:
        logger.error(f"Error procesando mensaje: {e}")
        await processing_msg.edit_text(
            "❌ Ocurrió un error inesperado. Por favor, inténtalo de nuevo."
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manejar errores"""
    logger.error(f"Error: {context.error}")

def main():
    """Función principal"""
    # Crear la aplicación
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Añadir manejadores
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    
    # Iniciar el bot
    logger.info("🤖 Bot iniciado. Esperando mensajes...")
    application.run_polling()

if __name__ == "__main__":
    main()
