# Script de despliegue automatizado para DigitalOcean (PowerShell)

Write-Host "🚀 Iniciando despliegue en DigitalOcean..." -ForegroundColor Green

# Verificar si doctl está instalado
try {
    doctl account get | Out-Null
} catch {
    Write-Host "❌ doctl no está instalado o no estás autenticado." -ForegroundColor Red
    Write-Host "1. Instala doctl: https://docs.digitalocean.com/reference/doctl/how-to/install/" -ForegroundColor Yellow
    Write-Host "2. Autentica: doctl auth init" -ForegroundColor Yellow
    exit 1
}

# Variables
$APP_NAME = "clinica-sistema"
$REGION = "nyc1"

Write-Host "📦 Creando aplicación en App Platform..." -ForegroundColor Blue

# Crear aplicación usando el archivo de configuración
try {
    doctl apps create --spec .do/app.yaml
    
    Write-Host "✅ Aplicación creada exitosamente!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Próximos pasos:" -ForegroundColor Cyan
    Write-Host "1. Ve al panel de DigitalOcean App Platform" -ForegroundColor White
    Write-Host "2. Conecta tu repositorio de GitHub/GitLab" -ForegroundColor White
    Write-Host "3. La aplicación se desplegará automáticamente" -ForegroundColor White
    Write-Host ""
    Write-Host "🔗 Panel: https://cloud.digitalocean.com/apps" -ForegroundColor Blue
    Write-Host "💰 Costo estimado: ~$5-12/mes" -ForegroundColor Yellow
} catch {
    Write-Host "❌ Error al crear la aplicación: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
