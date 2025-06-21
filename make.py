#!/usr/bin/env python3
"""
Bot de Telegram para descargar videos de Instagram usando savegram.app
"""

import os
import re
import requests
import tempfile
import time
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
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
        self.savegram_url = "https://savegram.app"
          def setup_driver(self):
        """Configurar el driver de Chrome para headless browsing"""
        from selenium.webdriver.chrome.service import Service
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            # Usar el ChromeDriver local
            driver_path = os.path.join(os.path.dirname(__file__), "drivers", "chromedriver.exe")
            if os.path.exists(driver_path):
                service = Service(driver_path)
                driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                driver = webdriver.Chrome(options=chrome_options)
            
            # Ejecutar script para evitar detección
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return driver
        except Exception as e:
            logger.error(f"Error configurando Chrome driver: {e}")
            return None
    
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
    
    def download_from_savegram(self, instagram_url):
        """Descargar video usando savegram.app"""
        driver = self.setup_driver()
        if not driver:
            return None, "Error configurando el navegador"
        
        try:
            # Ir a savegram.app
            driver.get(self.savegram_url)
            time.sleep(3)
            
            # Encontrar el campo de input
            input_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='Instagram']"))
            )
            
            # Limpiar y pegar la URL
            input_field.clear()
            input_field.send_keys(instagram_url)
            time.sleep(1)
            
            # Hacer clic en el botón de descarga
            download_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'], .btn-download, button:contains('Download')"))
            )
            download_button.click()
            
            # Esperar a que aparezcan los enlaces de descarga
            time.sleep(5)
            
            # Buscar enlaces de descarga de video
            video_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='.mp4'], a[download*='.mp4']")
            
            if not video_links:
                # Intentar buscar otros selectores posibles
                video_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='video'], .download-link")
            
            if video_links:
                video_url = video_links[0].get_attribute('href')
                
                # Descargar el video
                video_response = requests.get(video_url, stream=True)
                if video_response.status_code == 200:
                    # Crear archivo temporal
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
                        for chunk in video_response.iter_content(chunk_size=8192):
                            temp_file.write(chunk)
                        return temp_file.name, "Video descargado exitosamente"
                else:
                    return None, "Error descargando el video"
            else:
                return None, "No se encontraron enlaces de descarga"
                
        except Exception as e:
            logger.error(f"Error en savegram: {e}")
            return None, f"Error procesando la descarga: {str(e)}"
        
        finally:
            driver.quit()

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
        video_path, message = downloader.download_from_savegram(message_text)
        
        if video_path:
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