# 🤖 Bot Downloader & Transcriptor

Bot de Telegram que descarga videos sin marca de agua y transcribe audios de voz.

## 📋 TODO

- [ ] Quitar soporte de YouTube (solo dejar Instagram y TikTok para videos)
- [ ] Eliminar el mensaje de texto que acompaña al video (enviar video sin caption)
- [ ] Añadir soporte para Spotify → descargar como MP3
- [ ] Añadir transcripción de audio de voz a texto

## ⚡ Quick Start

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar token del bot
export BOT_TOKEN="tu_token_aqui"

# 3. Ejecutar bot
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

### 🔐 Token del Bot (Requerido)

Para mayor seguridad, el token del bot se obtiene de una variable de entorno:

**Desarrollo local:**
```bash
export BOT_TOKEN="tu_token_aqui"
python bot.py
```

**O usando un archivo .env:**
```bash
echo "BOT_TOKEN=tu_token_aqui" > .env
export $(cat .env | xargs)
python bot.py
```

**CI/CD (GitHub Actions):**
El token debe configurarse como un secreto en GitHub:
- Ve a Settings > Secrets and variables > Actions
- Crea un nuevo secret llamado `BOT_TOKEN`
- Pega tu token como valor

> ⚠️ **Nunca hagas commit del token en el código fuente**

## � Formatos soportados

- Posts: `instagram.com/p/xxxxx/`
- Reels: `instagram.com/reel/xxxxx/`  
- IGTV: `instagram.com/tv/xxxxx/`

## 🛡️ Notas

- Respeta los términos de Instagram
- Los archivos se autolimpian
- Logs guardados en `bot.log`
