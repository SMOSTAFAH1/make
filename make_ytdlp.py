#!/usr/bin/env python3
"""
Bot de Telegram para descargar videos de Instagram usando yt-dlp
Versión ultra simplificada y más confiable
"""

import os
import tempfile
import re
import subprocess
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
        pass
    
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
        return False    def download_with_ytdlp(self, instagram_url):
        """Descargar video usando yt-dlp como módulo de Python"""
        try:
            import yt_dlp
            
            # Crear directorio temporal
            temp_dir = tempfile.mkdtemp()
            
            # Configurar yt-dlp
            ydl_opts = {
                'format': 'best[ext=mp4]/best',
                'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                'noplaylist': True,
            }
            
            # Descargar con yt-dlp
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([instagram_url])
            
            # Buscar el archivo descargado
            for file in os.listdir(temp_dir):
                if file.endswith(('.mp4', '.mkv', '.webm')):
                    video_path = os.path.join(temp_dir, file)
                    return video_path, "Video descargado exitosamente con yt-dlp"
            
            return None, "No se encontró archivo de video"
                
        except Exception as e:
            logger.error(f"Error con yt-dlp: {e}")
            return None, f"Error: {str(e)}"

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
        "Solo pega el enlace y yo me encargo del resto! 🚀\n\n"
        "Powered by yt-dlp 💪"
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
    processing_msg = await update.message.reply_text("🔄 Descargando con yt-dlp... esto puede tomar unos segundos.")
    
    try:
        # Descargar el video
        video_path, message = downloader.download_with_ytdlp(message_text)
        
        if video_path and os.path.exists(video_path):
            # Verificar que el archivo no esté vacío
            if os.path.getsize(video_path) > 0:
                # Enviar el video
                await processing_msg.edit_text("✅ ¡Video descargado! Enviando...")
                
                with open(video_path, 'rb') as video_file:
                    await update.message.reply_video(
                        video=video_file,
                        caption="📱 Video descargado de Instagram\n🔧 Powered by yt-dlp"
                    )
                
                # Limpiar archivo temporal
                os.unlink(video_path)
                
                # Eliminar mensaje de procesamiento
                await processing_msg.delete()
            else:
                await processing_msg.edit_text("❌ Error: El archivo descargado está vacío")
                if os.path.exists(video_path):
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
    logger.info("🤖 Bot iniciado con yt-dlp. Esperando mensajes...")
    application.run_polling()

if __name__ == "__main__":
    main()
