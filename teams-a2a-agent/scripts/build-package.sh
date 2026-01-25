#!/bin/bash
# Script para generar el paquete ZIP de la aplicación de Teams
# con la URL del túnel configurada automáticamente
set -e

cd "$(dirname "$0")/.."

TUNNEL_NAME="teams-a2a-bot"
APP_NAME="teams-a2a-agent"

echo "🔍 Buscando túnel '$TUNNEL_NAME'..."

# Obtener URL del túnel automáticamente
TUNNEL_URL=$(devtunnel show $TUNNEL_NAME 2>/dev/null | grep -oP 'https://\K[^/]+' | head -1 || true)

if [ -z "$TUNNEL_URL" ]; then
    echo "⚠️  No se encontró el túnel '$TUNNEL_NAME'"
    echo ""
    echo "Opciones:"
    echo "  1. Crear el túnel:"
    echo "     devtunnel create $TUNNEL_NAME --allow-anonymous"
    echo "     devtunnel port create $TUNNEL_NAME -p 3978"
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
fi

# Crear paquete ZIP
echo "📦 Creando paquete ZIP..."
cd appPackage/build
zip -j ../$APP_NAME.zip manifest.json ../color.png ../outline.png

echo ""
echo "════════════════════════════════════════════════════════════"
echo "✅ Paquete generado: appPackage/$APP_NAME.zip"
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
echo "      az bot update --resource-group <RG> --name teams-a2a-agent-direct \\"
echo "        --endpoint 'https://$BOT_DOMAIN/api/messages'"
echo ""
echo "   2. Sube el paquete a Teams:"
echo "      Apps → Manage your apps → Upload an app → Upload a custom app"
echo ""
