#!/usr/bin/env python3
"""
Script para iniciar el bot de Telegram
"""

import os
import sys

def main():
    """Iniciar el bot"""
    try:
        print("🚀 Iniciando bot de Instagram downloader...")
        print("🔧 Presiona Ctrl+C para detener el bot")
        print("-" * 50)        # Importar y ejecutar el bot
        from make_ytdlp_fixed import main as bot_main
        bot_main()
        
    except KeyboardInterrupt:
        print("\n👋 Bot detenido por el usuario")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()