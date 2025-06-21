#!/usr/bin/env python3
"""
Script para instalar ChromeDriver automáticamente
"""

import os
import sys
import requests
import zipfile
import platform
from pathlib import Path

def get_chrome_driver():
    """Descargar e instalar ChromeDriver"""
    
    # Detectar sistema operativo
    system = platform.system().lower()
    
    if system == "windows":
        driver_url = "https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_win32.zip"
        driver_name = "chromedriver.exe"
    elif system == "darwin":  # macOS
        driver_url = "https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_mac64.zip"
        driver_name = "chromedriver"
    else:  # Linux
        driver_url = "https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip"
        driver_name = "chromedriver"
    
    print(f"Descargando ChromeDriver para {system}...")
    
    # Crear directorio drivers si no existe
    drivers_dir = Path("drivers")
    drivers_dir.mkdir(exist_ok=True)
    
    # Descargar ChromeDriver
    response = requests.get(driver_url)
    if response.status_code == 200:
        zip_path = drivers_dir / "chromedriver.zip"
        
        with open(zip_path, 'wb') as f:
            f.write(response.content)
        
        # Extraer el archivo
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(drivers_dir)
        
        # Eliminar el archivo zip
        zip_path.unlink()
        
        # Hacer ejecutable en sistemas Unix
        if system != "windows":
            driver_path = drivers_dir / driver_name
            os.chmod(driver_path, 0o755)
        
        print(f"✅ ChromeDriver instalado en: {drivers_dir / driver_name}")
        
        # Añadir al PATH
        current_path = os.environ.get('PATH', '')
        drivers_abs_path = str(drivers_dir.absolute())
        
        if drivers_abs_path not in current_path:
            print(f"📝 Añade esta ruta a tu PATH: {drivers_abs_path}")
            
    else:
        print("❌ Error descargando ChromeDriver")
        sys.exit(1)

if __name__ == "__main__":
    get_chrome_driver()
