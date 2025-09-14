#!/usr/bin/env python3
"""
🔧 Script de configuración para el Bot de Instagram Downloader

Este script ayuda a configurar correctamente la variable de entorno BOT_TOKEN
"""

import os
import re
import sys

def validate_token_format(token):
    """Validar que el token tenga el formato correcto"""
    pattern = r'^\d+:[A-Za-z0-9_-]+$'
    return bool(re.match(pattern, token))

def main():
    print("🤖 Configurador del Bot de Instagram Downloader")
    print("=" * 50)
    
    # Verificar token actual
    current_token = os.getenv('BOT_TOKEN')
    if current_token:
        if validate_token_format(current_token):
            print("✅ Ya tienes un token configurado y válido!")
            print(f"   Token: {current_token[:10]}...{current_token[-5:]}")
            return
        else:
            print("⚠️  Tienes un token configurado pero el formato es incorrecto")
            print(f"   Token actual: {current_token}")
    else:
        print("ℹ️  No hay token configurado actualmente")
    
    print("\n🔗 Para obtener tu token:")
    print("1. Ve a https://t.me/BotFather en Telegram")
    print("2. Envía /newbot y sigue las instrucciones")
    print("3. Copia el token que te da BotFather")
    
    print("\n📝 Formato del token:")
    print("   Debe ser: números:letras_números")
    print("   Ejemplo: 123456789:ABCDEFghijklmnopqrstuvwxyz123456789")
    
    print("\n💾 Para configurar el token:")
    print("   Opción 1 - Variable de entorno (temporal):")
    print("     export BOT_TOKEN='tu_token_aqui'")
    print("     python bot.py")
    
    print("\n   Opción 2 - Archivo .env (recomendado):")
    print("     echo 'BOT_TOKEN=tu_token_aqui' > .env")
    print("     python bot.py")
    
    # Ofrecer validar un token
    print("\n🧪 ¿Quieres validar un token? (s/N): ", end="")
    response = input().lower()
    if response in ['s', 'si', 'y', 'yes']:
        print("Pega tu token: ", end="")
        test_token = input().strip()
        
        if validate_token_format(test_token):
            print("✅ Formato de token correcto!")
        else:
            print("❌ Formato de token incorrecto.")
            print("   Debe ser: números:letras_números")

if __name__ == "__main__":
    main()