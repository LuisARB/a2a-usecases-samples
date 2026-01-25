#!/bin/bash
# Script para generar el paquete ZIP de la aplicación de Teams
# con la URL del túnel configurada automáticamente
set -e

cd "$(dirname "$0")/.."

echo "🔍 Buscando túnel 'teams-a2a-chatprompt'..."

# Obtener URL del túnel automáticamente (puerto 3980)
TUNNEL_URL=$(devtunnel show teams-a2a-chatprompt 2>/dev/null | grep -oP 'https://\K[^/]+' | grep '3980' | head -1 || true)

# Si no hay puerto 3980, intentar con cualquier puerto disponible
if [ -z "$TUNNEL_URL" ]; then
    TUNNEL_URL=$(devtunnel show teams-a2a-chatprompt 2>/dev/null | grep -oP 'https://\K[^/]+' | head -1 || true)
fi

if [ -z "$TUNNEL_URL" ]; then
    echo "⚠️  No se encontró el túnel 'teams-a2a-chatprompt'"
    echo ""
    echo "Opciones:"
    echo "  1. Crear el túnel:"
    echo "     devtunnel create teams-a2a-chatprompt --allow-anonymous"
    echo "     devtunnel port create teams-a2a-chatprompt -p 3980"
    echo ""
    echo "  2. O especificar la URL manualmente:"
    echo "     BOT_DOMAIN=tu-url.devtunnels.ms ./scripts/build-package.sh"
    echo ""
    
    if [ -z "$BOT_DOMAIN" ]; then
        exit 1
    fi
    TUNNEL_URL="$BOT_DOMAIN"
fi

echo "🔗 URL del túnel: $TUNNEL_URL"

# Guardar variables pasadas desde fuera (tienen prioridad)
EXTERNAL_BOT_ID="${BOT_ID:-}"
EXTERNAL_TEAMS_APP_ID="${TEAMS_APP_ID:-}"

# Cargar variables de entorno base si existen
if [ -f env/.env.dev ]; then
    echo "📄 Cargando variables desde env/.env.dev..."
    export $(cat env/.env.dev | grep -v '^#' | grep -v '^$' | xargs 2>/dev/null) || true
fi

# Restaurar variables externas (tienen prioridad sobre .env.dev)
if [ -n "$EXTERNAL_BOT_ID" ]; then
    export BOT_ID="$EXTERNAL_BOT_ID"
fi
if [ -n "$EXTERNAL_TEAMS_APP_ID" ]; then
    export TEAMS_APP_ID="$EXTERNAL_TEAMS_APP_ID"
fi

# Configurar variables del túnel
export BOT_DOMAIN="$TUNNEL_URL"
export BOT_ENDPOINT="https://$TUNNEL_URL"

# Generar IDs si no existen
if [ -z "$TEAMS_APP_ID" ]; then
    export TEAMS_APP_ID=$(cat /proc/sys/kernel/random/uuid 2>/dev/null || uuidgen | tr '[:upper:]' '[:lower:]')
    echo "🆔 Generado nuevo TEAMS_APP_ID: $TEAMS_APP_ID"
fi

if [ -z "$BOT_ID" ]; then
    export BOT_ID="$TEAMS_APP_ID"
fi

export APP_NAME_SUFFIX="${APP_NAME_SUFFIX:-dev}"
export TEAMSFX_ENV="${TEAMSFX_ENV:-dev}"

# Crear directorio de build
mkdir -p appPackage/build

# Verificar que envsubst está disponible
if ! command -v envsubst &> /dev/null; then
    echo "❌ Error: 'envsubst' no está instalado. Instálalo con:"
    echo "   apt-get install gettext-base  # Debian/Ubuntu"
    echo "   brew install gettext          # macOS"
    exit 1
fi

# Generar manifest con variables resueltas
# El manifest de Teams Toolkit usa formato ${{VARIABLE}}, lo convertimos con sed
echo "📝 Generando manifest..."
sed -e "s/\${{TEAMS_APP_ID}}/$TEAMS_APP_ID/g" \
    -e "s/\${{APP_NAME_SUFFIX}}/$APP_NAME_SUFFIX/g" \
    -e "s/\${{BOT_ID}}/$BOT_ID/g" \
    -e "s/\${{BOT_DOMAIN}}/$BOT_DOMAIN/g" \
    appPackage/manifest.json > appPackage/build/manifest.json

# Verificar que las imágenes existen
if [ ! -f appPackage/color.png ] || [ ! -f appPackage/outline.png ]; then
    echo "⚠️  Advertencia: Faltan color.png o outline.png en appPackage/"
    echo "   Creando imágenes placeholder..."
    
    # Crear imágenes placeholder si no existen
    if [ ! -f appPackage/color.png ]; then
        # Crear un PNG simple de 192x192 (color)
        echo "iVBORw0KGgoAAAANSUhEUgAAAMAAAADACAMAAABlApw1AAAABGdBTUEAALGPC/xhBQAAAAFzUkdCAK7OHOkAAAAgY0hSTQAAeiYAAICEAAD6AAAAgOgAAHUwAADqYAAAOpgAABdwnLpRPAAAANhQTFRFAAAAKZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7/KZ7////+yx6fUAAAADN0Uk5TAAABAgMEBQYHCAkKCwwNDg8QERITFBUWFxgZGhscHR4fICEiIyQlJicoKSorLC0uLzAxMjM0NTY3ODk6Ozw9Pj9AQUJDREVGR0hJSktMTU5PUFFSU1RVVldYWVpbXF1eX2BhYmNkZWZnaGlqa2xtbm9wcXJzdHV2d3h5ent8fX5/gIGCg4SFhoeIiYqLjI2Oj5CRkpOUlZaXmJmam5ydnp+goaKjpKWmp6ipqqusra6vsLGys7S1tre4ubq7vL2+v8DBwsPExcbHyMnKy8zNzs/Q0dLT1NXW19jZ2tvc3d7f4OHi4+Tl5ufo6err7O3u7/Dx8vP09fb3+Pn6+/z9/uGaP5cAAAABYktHROsIB5d6AAAB5klEQVR42u3d91vTQBjAcQqCiKKCe++9N+69xb333nuAe+89QFBQEUVFEETFhfv/8pLwQJN7L82l796PP+T7u+R9LrmmpRERERERERERERERERERkUlVqYhI+Qw1Oo2IoVb5mlRB41rJ//R0deq8bnL9yldHoyb/L0C9Rs3+X8BWrf9XwLbJP0FTgJZt2v6/gO0StksaQEf/LUDnLsn/B+iW0C1h++79+v+3AL0S9u2f/D+Aww9L/j9An4R+CQMOOuz/BTgi4cihyf8HOC7h+BH/H+Dk0+J+xzYdDJzQ1X8LcOoZCR0N/LcAZ52TcPYF/y3AuRckv+DiyxJefOX/BTj/moTXLvlvAd64IeGNW/5bgLeEt96+4z8FePe+hHff908B3nsg4YMH/luAD0P+IcDHT0T8BOCT/xbgM0lffE7+/wFeJvw3/y/A18u48vbNhB8+/W8BvvtBwo8/+X8Bfv7lF/8twG/Cv/ldwkq//L8Af0hY+a//F+Dv4H8I8E/CShLw7wL8s0xY+d//C7B8hYRVVvpvAf4j6eqVk1eXsBry7wL8V8Kq/i1ANcI11cNq+G8BqhN+m/y/ADUSatXxbwHq1Jdw3fX+K8D6Gye/6kYJb+bfAtRsJOHWjZL/lttuu+02+y8l7c6+gOCvIQAAACV0RVh0ZGF0ZTpjcmVhdGUAMjAxOS0wMy0wNlQxMjo1MToxOCswMDowMHy8RHQAAAAJREF0jdgAAAAABgAAABAAAAAAACAAD/YBMwAAAABJRU5ErkJggg==" | base64 -d > appPackage/color.png 2>/dev/null || echo "No se pudo crear color.png"
    fi
    if [ ! -f appPackage/outline.png ]; then
        cp appPackage/color.png appPackage/outline.png 2>/dev/null || echo "No se pudo crear outline.png"
    fi
fi

# Crear paquete ZIP
echo "📦 Creando paquete ZIP..."
cd appPackage/build
zip -j ../teams-a2a-chatprompt.zip manifest.json ../color.png ../outline.png

echo ""
echo "════════════════════════════════════════════════════════════"
echo "✅ Paquete generado: appPackage/teams-a2a-chatprompt.zip"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "📋 Configuración aplicada:"
echo "   BOT_DOMAIN    = $BOT_DOMAIN"
echo "   BOT_ENDPOINT  = $BOT_ENDPOINT"
echo "   BOT_ID        = $BOT_ID"
echo "   TEAMS_APP_ID  = $TEAMS_APP_ID"
echo ""
echo "📌 Próximos pasos:"
echo "   1. Actualiza el endpoint del bot en Azure:"
echo "      az bot update --resource-group <RG> --name <BOT> \\"
echo "        --endpoint 'https://$BOT_DOMAIN/api/messages'"
echo ""
echo "   2. Sube el paquete a Teams:"
echo "      Apps → Manage your apps → Upload an app → Upload a custom app"
echo ""
