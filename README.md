# 🤖 Instagram Downloader Bot

Bot de Telegram ultra simple que descarga videos de Instagram automáticamente.

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

**🚀 Configuración rápida:**
```bash
# 1. Obtén tu token de @BotFather en Telegram
# 2. Configura la variable de entorno:
export BOT_TOKEN="tu_token_aqui"
python bot.py
```

**📋 Usando archivo .env (Recomendado):**
```bash
# 1. Copia el archivo de ejemplo
cp .env.example .env

# 2. Edita .env y pon tu token real
# BOT_TOKEN=123456789:ABCDEFghijklmnopqrstuvwxyz123456789

# 3. Carga las variables y ejecuta
export $(cat .env | grep -v '^#' | xargs)
python bot.py
```

**🔧 Script de ayuda:**
```bash
# Usa nuestro script para validar tu configuración
python setup_bot.py
```

**⚠️ Formato del token:**
Tu token debe verse así: `123456789:ABCDEFghijklmnopqrstuvwxyz123456789`
- Primera parte: números (tu bot ID)
- Separador: dos puntos `:`  
- Segunda parte: letras, números, guiones

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

## 🆘 Solución de Problemas

**❌ Error: "BOT_TOKEN no está configurado"**
```bash
# Configura tu token:
export BOT_TOKEN='8169625627:AAFQ5eBXUrlzs65J8AZeUtgiIXhFZah35C4'
```

**❌ Error: "Token inválido"** 
- Verifica que el token tenga el formato: `números:letras_números`
- Usa el script de ayuda: `python setup_bot.py`

**❌ El bot no responde en Telegram**
- Verifica que el token sea correcto (de @BotFather)
- Asegúrate de que el bot esté ejecutándose sin errores
- Revisa los logs en `bot.log`

**💡 Comandos útiles:**
```bash
# Validar configuración actual
python setup_bot.py

# Ver logs del bot
tail -f bot.log

# Verificar formato de token
echo $BOT_TOKEN
```
