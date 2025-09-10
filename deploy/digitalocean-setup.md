# Despliegue en DigitalOcean

## Opción 1: DigitalOcean App Platform (Recomendado - Más fácil)

### Paso 1: Preparar el repositorio
1. Sube tu código a GitHub/GitLab
2. Asegúrate de tener estos archivos:
   - `Dockerfile`
   - `requirements.txt`
   - `.dockerignore`

### Paso 2: Crear la aplicación en DigitalOcean
1. Ve a DigitalOcean App Platform
2. Crea una nueva app
3. Conecta tu repositorio de GitHub/GitLab
4. Configura:
   - **Source**: Tu repositorio
   - **Branch**: main
   - **Autodeploy**: Habilitado
   - **Build Command**: Docker
   - **Run Command**: Se detecta automáticamente del Dockerfile

### Paso 3: Configuración de la aplicación
- **Name**: clinica-sistema
- **Plan**: Basic ($5/mes para empezar)
- **Region**: NYC1 o la más cercana a tus usuarios

### Paso 4: Variables de entorno (opcional)
```
PYTHONUNBUFFERED=1
STREAMLIT_SERVER_PORT=8080
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

---

## Opción 2: DigitalOcean Droplet con Docker

### Paso 1: Crear Droplet
- **Imagen**: Ubuntu 22.04 LTS
- **Plan**: Basic $6/mes (1GB RAM, 1 vCPU)
- **Región**: Elige la más cercana
- **Autenticación**: SSH Key (recomendado)

### Paso 2: Conectar y configurar servidor
```bash
# Conectar vía SSH
ssh root@your-droplet-ip

# Actualizar sistema
apt update && apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Instalar Docker Compose
apt install docker-compose-plugin -y

# Instalar Git
apt install git -y
```

### Paso 3: Clonar y desplegar
```bash
# Clonar repositorio
git clone https://github.com/TU_USUARIO/clinica.git
cd clinica

# Crear directorio para datos persistentes
mkdir -p /opt/clinica-data

# Ejecutar con Docker Compose
docker compose up -d --build
```

### Paso 4: Configurar Nginx (Opcional - para dominio personalizado)
```bash
# Instalar Nginx
apt install nginx -y

# Crear configuración
cat > /etc/nginx/sites-available/clinica << 'EOF'
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
EOF

# Habilitar sitio
ln -s /etc/nginx/sites-available/clinica /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

### Paso 5: SSL con Let's Encrypt (Opcional)
```bash
# Instalar Certbot
apt install certbot python3-certbot-nginx -y

# Obtener certificado SSL
certbot --nginx -d your-domain.com
```

---

## Opción 3: DigitalOcean Container Registry + App Platform

### Paso 1: Configurar Container Registry
```bash
# Instalar doctl (DigitalOcean CLI)
# Seguir instrucciones en: https://docs.digitalocean.com/reference/doctl/how-to/install/

# Autenticarse
doctl auth init

# Crear registry
doctl registry create clinica-registry
```

### Paso 2: Build y Push
```bash
# Login al registry
doctl registry login

# Build imagen
docker build -t registry.digitalocean.com/clinica-registry/clinica-app:latest .

# Push imagen
docker push registry.digitalocean.com/clinica-registry/clinica-app:latest
```

### Paso 3: Desplegar en App Platform
- Usa la imagen del registry en lugar del código fuente
- Configurar según Opción 1

---

## Monitoreo y Mantenimiento

### Logs
```bash
# Ver logs (Droplet)
docker compose logs -f

# Ver logs (App Platform)
# Disponibles en el dashboard de DigitalOcean
```

### Updates
```bash
# Actualizar aplicación (Droplet)
git pull
docker compose up -d --build

# App Platform se actualiza automáticamente con git push
```

### Backup
```bash
# Backup base de datos (Droplet)
docker compose exec clinica-app cp /app/database/clinica.db /tmp/
docker cp $(docker compose ps -q clinica-app):/tmp/clinica.db ./backup-$(date +%Y%m%d).db
```

## Costos Estimados

| Opción | Costo Mensual | Pros | Contras |
|--------|---------------|------|---------|
| App Platform | $5-12 | Fácil, automático, escalable | Menos control |
| Droplet Basic | $6 | Control total, más barato | Requiere administración |
| Droplet + Registry | $6 + $2 | Profesional, CI/CD | Más complejo |

## Recomendación
- **Para comenzar**: App Platform (Opción 1)
- **Para producción**: Droplet + Nginx + SSL (Opción 2)
- **Para equipos**: Container Registry + App Platform (Opción 3)
