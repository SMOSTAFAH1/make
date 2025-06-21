# 🤖 Instagram Downloader Bot

Bot de Telegram ultra simple que descarga videos de Instagram automáticamente.

## ⚡ Quick Start

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar bot
python bot.py
```

## 🎯 Características

- ✅ **Ultra confiable** - Powered by yt-dlp
- ✅ **Simple** - Solo envía el enlace
- ✅ **Rápido** - Sin navegadores web
- ✅ **Limpio** - Auto-limpieza de archivos temporales

## 📱 Uso

1. **Inicia el bot:** `python bot.py`
2. **En Telegram:** Busca tu bot
3. **Envía:** Cualquier enlace de Instagram
4. **Recibe:** Tu video descargado automáticamente

##  Configuración

Edita `BOT_TOKEN` en `bot.py`:
```python
BOT_TOKEN = "tu_token_aqui"
```

## � Formatos soportados

- Posts: `instagram.com/p/xxxxx/`
- Reels: `instagram.com/reel/xxxxx/`  
- IGTV: `instagram.com/tv/xxxxx/`

## 🛡️ Notas

- Respeta los términos de Instagram
- Los archivos se autolimpian
- Logs guardados en `bot.log`
