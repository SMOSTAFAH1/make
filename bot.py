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
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ==================== CONFIGURACIÓN ====================

BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required")  

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

class VideoDownloader:
    """Descargador de videos de Instagram, YouTube y TikTok usando yt-dlp"""
    
    def __init__(self):
        # Dominios soportados
        self.supported_domains = {
            'instagram': ['instagram.com', 'www.instagram.com'],
            'youtube': ['youtube.com', 'youtu.be', 'm.youtube.com', 'www.youtube.com'],
            'tiktok': ['tiktok.com', 'vm.tiktok.com', 'vt.tiktok.com', 'www.tiktok.com', 'm.tiktok.com']
        }
    
    def is_supported_url(self, url):
        """Verificar si la URL es de una plataforma soportada"""
        url = url.strip().lower()
        
        # Verificar cada plataforma
        for platform, domains in self.supported_domains.items():
            for domain in domains:
                if domain in url:
                    return True, platform
        
        return False, None
      
    def download(self, video_url):
        """
        Descargar video de Instagram, YouTube o TikTok con configuración optimizada
        
        Returns:
            tuple: (ruta_archivo, mensaje) o (None, mensaje_error)
        """
        try:
            import yt_dlp
            
            # Crear directorio temporal
            temp_dir = tempfile.mkdtemp()
            logger.info(f"Descargando: {video_url}")
            
            # Detectar plataforma
            is_supported, platform = self.is_supported_url(video_url)
            if not is_supported:
                return None, "URL no soportada"
            
            # Configurar yt-dlp con opciones específicas por plataforma
            ydl_opts = {
                'format': 'best',
                'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                'noplaylist': True,
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'writethumbnail': False,
                'writeinfojson': False,
                'ignoreerrors': False,
                'retries': 10,
                'fragment_retries': 10,
                'socket_timeout': 60,
                'nocheckcertificate': True,
                'age_limit': None,
            }
            
            # Configuraciones específicas por plataforma
            if platform == 'instagram':
                ydl_opts.update({
                    'format': 'best',
                    'http_headers': {
                        'User-Agent': 'Instagram 76.0.0.15.395 Android (24/7.0; 640dpi; 1440x2560; samsung; SM-G930F; herolte; samsungexynos8890; en_US; 138226743)',
                    },
                })
            elif platform == 'youtube':
                ydl_opts.update({
                    'format': 'best[ext=mp4]/best',
                })
            elif platform == 'tiktok':
                # TikTok: usar configuración MINIMALISTA
                ydl_opts = {
                    'outtmpl': os.path.join(temp_dir, '%(id)s.%(ext)s'),
                    'format': 'best',
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': False,
                    'nocheckcertificate': True,
                }
            
            # Descargar - MÉTODO SIMPLE
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])
            except Exception as download_error:
                # Si falla, simplificar al máximo
                logger.warning(f"Fallo descarga {platform}, usando modo ultra simple: {download_error}")
                simple_opts = {
                    'outtmpl': os.path.join(temp_dir, 'video.%(ext)s'),
                    'format': 'best',
                    'quiet': True,
                }
                with yt_dlp.YoutubeDL(simple_opts) as ydl_simple:
                    ydl_simple.download([video_url])
            
            # Buscar archivo descargado (buscar CUALQUIER extensión de video)
            video_extensions = ('.mp4', '.mkv', '.webm', '.mov', '.avi', '.flv', '.m4v', '.3gp')
            for file in os.listdir(temp_dir):
                if file.endswith(video_extensions):
                    video_path = os.path.join(temp_dir, file)
                    
                    # Verificar tamaño del archivo (límite de Telegram: 50MB)
                    file_size = os.path.getsize(video_path)
                    if file_size > 50 * 1024 * 1024:  # 50MB
                        shutil.rmtree(temp_dir)
                        return None, f"Video muy grande ({file_size:,} bytes). Máximo 50MB."
                    
                    # Mover a archivo temporal con nombre fijo
                    final_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
                    shutil.move(video_path, final_path)
                    
                    # Limpiar directorio temporal
                    shutil.rmtree(temp_dir)
                    
                    logger.info(f"✅ Descarga exitosa: {file_size} bytes desde {platform}")
                    return final_path, f"Video de {platform.title()} descargado ({file_size:,} bytes)"
            
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
downloader = VideoDownloader()

# Diccionario para rastrear descargas activas por usuario
active_downloads = {}

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /start"""
    welcome_msg = """
🤖 **Video Downloader Bot**

¡Hola! Envíame un enlace y te descargaré el video automáticamente.

📱 **Plataformas soportadas:**
• 📸 Instagram (Posts, Reels, IGTV)
• ▶️ YouTube (Videos y Shorts)
• 🎵 TikTok (Videos y efectos)

🚀 **Uso:**
Solo pega el enlace y yo me encargo del resto!

🔧 **Powered by yt-dlp** - Ultra confiable y rápido

⚡ **Características:**
• Reintentos automáticos (hasta 6 intentos)
• Auto-limpieza de mensajes
• Soporte para múltiples formatos
    """.strip()
    
    await update.message.reply_text(welcome_msg)
    logger.info(f"Usuario {update.effective_user.id} inició el bot")

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /stop - Cancelar descarga actual"""
    user_id = update.effective_user.id
    
    if user_id in active_downloads and active_downloads[user_id]:
        active_downloads[user_id] = False
        await update.message.reply_text("🛑 **Descarga cancelada**\nPuedes enviar otro enlace.")
        logger.info(f"Usuario {user_id} canceló su descarga")
    else:
        await update.message.reply_text("ℹ️ No tienes ninguna descarga activa.")

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manejar URLs de videos de Instagram, YouTube y TikTok"""
    url = update.message.text.strip()
    user_id = update.effective_user.id
    
    # Cancelar si ya tiene una descarga activa
    if user_id in active_downloads and active_downloads[user_id]:
        await update.message.reply_text("⚠️ Ya tienes una descarga en proceso. Usa /stop para cancelarla.")
        return
    
    # Marcar descarga como activa
    active_downloads[user_id] = True
    
    # Verificar URL
    is_supported, platform = downloader.is_supported_url(url)
    if not is_supported:
        active_downloads[user_id] = False
        await update.message.reply_text(
            "❌ **URL no soportada**\n\n"
            "Por favor, envía un enlace válido de:\n"
            "• 📸 Instagram\n"
            "• ▶️ YouTube\n"
            "• 🎵 TikTok"
        )
        logger.warning(f"Usuario {user_id} envió URL no soportada: {url}")
        return
    
    # Mensaje de procesamiento
    platform_emoji = {'instagram': '📸', 'youtube': '▶️', 'tiktok': '🎵'}
    processing_msg = await update.message.reply_text(
        f"🔄 **Procesando {platform_emoji.get(platform, '📹')} {platform.title()}...**\n"
        "Descargando tu video, esto puede tomar unos segundos."
    )
    
    try:
        # Sistema de reintentos INFINITOS - hasta que funcione o usuario diga /stop
        attempt = 0
        video_path = None
        message = ""
        
        while active_downloads.get(user_id, False):
            attempt += 1
            
            # Actualizar mensaje cada intento
            if attempt == 1:
                await processing_msg.edit_text(
                    f"🔄 **Procesando {platform_emoji.get(platform, '📹')} {platform.title()}...**\n"
                    "Descargando tu video...\n\n"
                    "💡 Usa /stop para cancelar"
                )
            else:
                await processing_msg.edit_text(
                    f"🔄 **Intento #{attempt} - {platform_emoji.get(platform, '📹')} {platform.title()}**\n"
                    f"Reintentando descarga...\n\n"
                    f"💡 Usa /stop para cancelar"
                )
                logger.info(f"Reintento {attempt} para usuario {user_id} - {platform}")
            
            # Descargar video
            video_path, message = downloader.download(url)
            
            # Si la descarga fue exitosa, salir del bucle
            if video_path and os.path.exists(video_path) and os.path.getsize(video_path) > 0:
                break
            
            # Esperar antes del siguiente intento (incrementa con cada fallo)
            wait_time = min(3 + (attempt * 0.5), 10)  # Max 10 segundos
            await asyncio.sleep(wait_time)
        
        # Verificar si la descarga fue exitosa o si fue cancelada
        if not active_downloads.get(user_id, False):
            # Usuario canceló
            await processing_msg.edit_text("🛑 **Descarga cancelada por el usuario**")
            await asyncio.sleep(3)
            await processing_msg.delete()
            await update.message.delete()
            active_downloads[user_id] = False
            return
        
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
                        caption=f"{platform_emoji.get(platform, '�')} **Video de {platform.title()}**\n🔧 Powered by yt-dlp"
                    )
                
                # Limpiar archivo
                os.unlink(video_path)
                
                # Eliminar mensaje de procesamiento
                await processing_msg.delete()
                
                # Borrar mensaje original del usuario (solo si fue exitoso)
                try:
                    await update.message.delete()
                    logger.info(f"✅ Mensaje original eliminado para usuario {user_id}")
                except Exception as delete_error:
                    logger.warning(f"No se pudo eliminar mensaje original: {delete_error}")
                
                logger.info(f"✅ Video enviado exitosamente a usuario {user_id} después de {attempt} intentos")
                active_downloads[user_id] = False
            else:
                # Archivo vacío
                error_msg = await processing_msg.edit_text(
                    f"❌ **Error: Archivo vacío**\n"
                    f"Se intentó {attempt} veces sin éxito.\n"
                    f"Este mensaje se eliminará en 10 segundos."
                )
                if video_path:
                    os.unlink(video_path)
                
                active_downloads[user_id] = False
                await asyncio.sleep(10)
                try:
                    await error_msg.delete()
                    await update.message.delete()
                    logger.info(f"🧹 Mensajes limpiados después de fallo para usuario {user_id}")
                except Exception as cleanup_error:
                    logger.warning(f"No se pudieron limpiar mensajes: {cleanup_error}")
        else:
            # Error de descarga
            error_msg = await processing_msg.edit_text(
                f"❌ **Error de descarga**\n"
                f"{message}\n"
                f"Se intentó {attempt} veces.\n"
                f"Este mensaje se eliminará en 10 segundos."
            )
            
            active_downloads[user_id] = False
            await asyncio.sleep(10)
            try:
                await error_msg.delete()
                await update.message.delete()
                logger.info(f"🧹 Mensajes limpiados después de fallo para usuario {user_id}")
            except Exception as cleanup_error:
                logger.warning(f"No se pudieron limpiar mensajes: {cleanup_error}")
            
    except Exception as e:
        logger.error(f"Error procesando mensaje de usuario {user_id}: {e}")
        active_downloads[user_id] = False
        error_msg = await processing_msg.edit_text(
            f"❌ **Error inesperado**\n"
            f"Por favor, inténtalo de nuevo.\n"
            f"Detalles: `{str(e)}`\n"
            f"Este mensaje se eliminará en 10 segundos."
        )
        
        # Esperar 10 segundos y limpiar mensajes
        await asyncio.sleep(10)
        try:
            await error_msg.delete()
            await update.message.delete()
            logger.info(f"🧹 Mensajes limpiados después de error inesperado para usuario {user_id}")
        except Exception as cleanup_error:
            logger.warning(f"No se pudieron limpiar mensajes: {cleanup_error}")

async def handle_other_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manejar mensajes que no son URLs soportadas"""
    await update.message.reply_text(
        "🤔 **No entiendo ese mensaje**\n\n"
        "Envíame un enlace de video para descargarlo:\n"
        "• 📸 Instagram\n"
        "• ▶️ YouTube\n"
        "• 🎵 TikTok\n\n"
        "Usa /start para ver las instrucciones completas."
    )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manejar errores del bot"""
    logger.error(f"Error del bot: {context.error}")

# ==================== MAIN ====================

def main():
    """Función principal del bot"""
    print("🚀 Iniciando Video Downloader Bot...")
    print("📸 Instagram | ▶️ YouTube | 🎵 TikTok")
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
        
        # Crear aplicación CON CONFIGURACIÓN ESPECIAL
        application = (
            Application.builder()
            .token(BOT_TOKEN)
            .concurrent_updates(True)
            .build()
        )
        
        # Añadir handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("stop", stop_command))
        application.add_handler(MessageHandler(
            filters.TEXT & (
                filters.Regex(r'.*instagram\.com.*') |
                filters.Regex(r'.*youtube\.com.*') |
                filters.Regex(r'.*youtu\.be.*') |
                filters.Regex(r'.*tiktok\.com.*') |
                filters.Regex(r'.*m\.youtube\.com.*')
            ),
            handle_url
        ))
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_other_messages
        ))
        application.add_error_handler(error_handler)
        
        # MÉTODO ANTI-CRASH DEFINITIVO
        logger.info("🤖 Bot iniciado con método anti-crash...")
        
        # Ejecutar con run_polling pero SIN CLEANUP
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
            close_loop=False,
            stop_signals=None  # CRÍTICO: Esto evita el error
        )
        
    except KeyboardInterrupt:
        print("\n👋 Bot detenido por el usuario")
        logger.info("Bot detenido por el usuario")
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        logger.error(f"Error crítico: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
