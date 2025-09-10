#!/bin/bash

# Script de despliegue automatizado para DigitalOcean

echo "🚀 Iniciando despliegue en DigitalOcean..."

# Verificar si doctl está instalado
if ! command -v doctl &> /dev/null; then
    echo "❌ doctl no está instalado. Instálalo desde: https://docs.digitalocean.com/reference/doctl/how-to/install/"
    exit 1
fi

# Verificar autenticación
if ! doctl account get &> /dev/null; then
    echo "❌ No estás autenticado con DigitalOcean. Ejecuta: doctl auth init"
    exit 1
fi

# Variables
APP_NAME="clinica-sistema"
REGION="nyc1"

echo "📦 Creando aplicación en App Platform..."

# Crear aplicación usando el archivo de configuración
doctl apps create --spec .do/app.yaml

echo "✅ Aplicación creada exitosamente!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Ve al panel de DigitalOcean App Platform"
echo "2. Conecta tu repositorio de GitHub/GitLab"
echo "3. La aplicación se desplegará automáticamente"
echo ""
echo "🔗 Panel: https://cloud.digitalocean.com/apps"
echo "💰 Costo estimado: ~$5-12/mes"
