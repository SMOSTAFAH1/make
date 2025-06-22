#!/usr/bin/env python3
"""
🤖 Instagram Downloader Bot para Telegram
Bot que descarga automáticamente videos de Instagram usando yt-dlp

Uso:
    python bot.py

Características:
    ✅ Descarga Reels, Posts, IGTV
    ✅ Powered by yt-dlp (ultra confiable)
    ✅ Manejo automático de archivos temporales
    ✅ Logs detallados para debugging
"""

import os
import tempfile
import re
import shutil
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ==================== CONFIGURACIÓN ====================

BOT_TOKEN = "8169625627:AAFQ5eBXUrlzs65J8AZeUtgiIXhFZah35C4"

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== DOWNLOADER ====================

class InstagramDownloader:
    """Descargador de videos de Instagram usando yt-dlp"""
    
    def __init__(self):
        # Patrones más flexibles para Instagram
        self.instagram_domains = ['instagram.com', 'www.instagram.com']
    
    def is_instagram_url(self, url):
        """Verificar si la URL es de Instagram - método súper flexible"""
        url = url.strip().lower()
          # Verificar si contiene instagram.com en cualquier parte
        if 'instagram.com' in url:
            # Verificar que sea una URL válida
            if url.startswith('http://') or url.startswith('https://'):
                return True
            # Si no tiene protocolo, asumir que es válida
            elif url.startswith('instagram.com') or url.startswith('www.instagram.com'):
                return True
        
        return False
      
    def download(self, instagram_url):
        """
        Descargar video de Instagram con configuración optimizada
        
        Returns:
            tuple: (ruta_archivo, mensaje) o (None, mensaje_error)
        """
        try:
            import yt_dlp
            
            # Crear directorio temporal
            temp_dir = tempfile.mkdtemp()
            logger.info(f"Descargando: {instagram_url}")
            
            # Configurar yt-dlp con opciones avanzadas para Instagram
            ydl_opts = {
                'format': 'best[ext=mp4]/best',
                'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                'noplaylist': True,
                'quiet': True,
                'no_warnings': True,
                # Opciones específicas para Instagram
                'extract_flat': False,
                'writethumbnail': False,
                'writeinfojson': False,
                'ignoreerrors': True,
                # Headers para evitar bloqueos
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-us,en;q=0.5',
                    'Accept-Encoding': 'gzip,deflate',
                    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
                    'Connection': 'keep-alive',
                },
                # Reintentos
                'retries': 3,
                'socket_timeout': 30,
            }
            
            # Descargar
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([instagram_url])
            
            # Buscar archivo descargado
            for file in os.listdir(temp_dir):
                if file.endswith(('.mp4', '.mkv', '.webm')):
                    video_path = os.path.join(temp_dir, file)
                    
                    # Mover a archivo temporal con nombre fijo
                    final_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
                    shutil.move(video_path, final_path)
                    
                    # Limpiar directorio temporal
                    shutil.rmtree(temp_dir)
                    
                    file_size = os.path.getsize(final_path)
                    logger.info(f"✅ Descarga exitosa: {file_size} bytes")
                    return final_path, f"Video descargado ({file_size:,} bytes)"
            
            # No se encontró archivo
            shutil.rmtree(temp_dir)
            logger.warning("No se encontró archivo de video")
            return None, "No se encontró archivo de video"
                
        except Exception as e:
            logger.error(f"Error descargando: {e}")
            # Limpiar en caso de error
            if 'temp_dir' in locals():
                try:
                    shutil.rmtree(temp_dir)
                except:
                    pass
            return None, f"Error: {str(e)}"

# ==================== BOT HANDLERS ====================

# Instancia global del descargador
downloader = InstagramDownloader()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /start"""
    welcome_msg = """
🤖 **Instagram Downloader Bot**

¡Hola! Envíame un enlace de Instagram y te descargaré el video automáticamente.

📱 **Formatos soportados:**
• Posts de Instagram
• Reels
• IGTV

🚀 **Uso:**
Solo pega el enlace y yo me encargo del resto!

🔧 **Powered by yt-dlp** - Ultra confiable y rápido
    """.strip()
    
    await update.message.reply_text(welcome_msg)
    logger.info(f"Usuario {update.effective_user.id} inició el bot")

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manejar URLs de Instagram"""
    url = update.message.text.strip()
    user_id = update.effective_user.id
    
    # Verificar URL
    if not downloader.is_instagram_url(url):
        await update.message.reply_text(
            "❌ **URL no válida**\n\n"
            "Por favor, envía un enlace válido de Instagram.\n"
            "Ejemplo: `https://www.instagram.com/p/...`"
        )
        logger.warning(f"Usuario {user_id} envió URL inválida: {url}")
        return
    
    # Mensaje de procesamiento
    processing_msg = await update.message.reply_text(
        "🔄 **Procesando...**\n"
        "Descargando tu video, esto puede tomar unos segundos."
    )
    
    try:
        # Descargar video
        video_path, message = downloader.download(url)
        
        if video_path and os.path.exists(video_path):
            file_size = os.path.getsize(video_path)
            
            if file_size > 0:
                # Actualizar mensaje
                await processing_msg.edit_text(
                    f"✅ **¡Descarga exitosa!**\n"
                    f"Tamaño: {file_size:,} bytes\n"
                    f"Enviando video..."
                )
                
                # Enviar video
                with open(video_path, 'rb') as video_file:
                    await update.message.reply_video(
                        video=video_file,
                        caption="📱 **Video de Instagram**\n🔧 Powered by yt-dlp"
                    )
                
                # Limpiar archivo
                os.unlink(video_path)
                
                # Eliminar mensaje de procesamiento
                await processing_msg.delete()
                
                logger.info(f"✅ Video enviado exitosamente a usuario {user_id}")
            else:
                await processing_msg.edit_text("❌ **Error:** Archivo vacío")
                os.unlink(video_path)
        else:
            await processing_msg.edit_text(f"❌ **Error de descarga**\n{message}")
            
    except Exception as e:
        logger.error(f"Error procesando mensaje de usuario {user_id}: {e}")
        await processing_msg.edit_text(
            f"❌ **Error inesperado**\n"
            f"Por favor, inténtalo de nuevo.\n"
            f"Detalles: `{str(e)}`"
        )

async def handle_other_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manejar mensajes que no son URLs de Instagram"""
    await update.message.reply_text(
        "🤔 **No entiendo ese mensaje**\n\n"
        "Envíame un enlace de Instagram para descargar el video.\n"
        "Usa /start para ver las instrucciones completas."
    )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manejar errores del bot"""
    logger.error(f"Error del bot: {context.error}")

# ==================== MAIN ====================

def main():
    """Función principal del bot"""
    print("🚀 Iniciando Instagram Downloader Bot...")
    print("🔧 Presiona Ctrl+C para detener")
    print("-" * 50)
    
    try:
        # Verificar dependencias
        try:
            import yt_dlp
            logger.info("✅ yt-dlp disponible")
        except ImportError:
            logger.error("❌ yt-dlp no instalado. Ejecuta: pip install yt-dlp")
            return
        
        # Crear aplicación
        application = Application.builder().token(BOT_TOKEN).build()
          # Añadir handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(MessageHandler(
            filters.TEXT & filters.Regex(r'.*instagram\.com.*'),
            handle_url
        ))
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_other_messages
        ))
        application.add_error_handler(error_handler)
        
        # Iniciar bot
        logger.info("🤖 Bot iniciado y esperando mensajes...")
        application.run_polling()
        
    except KeyboardInterrupt:
        print("\n👋 Bot detenido por el usuario")
        logger.info("Bot detenido por el usuario")
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        logger.error(f"Error crítico: {e}")

if __name__ == "__main__":
    main()
