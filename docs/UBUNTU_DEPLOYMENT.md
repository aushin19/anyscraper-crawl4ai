# Ubuntu Server Deployment Guide

Complete guide for deploying the Flask crawl4ai Scraper API on Ubuntu Server.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Method 1: Docker Deployment (Recommended)](#method-1-docker-deployment-recommended)
3. [Method 2: Direct Python Installation](#method-2-direct-python-installation)
4. [Nginx Reverse Proxy Setup](#nginx-reverse-proxy-setup)
5. [SSL/HTTPS Configuration](#sslhttps-configuration)
6. [Firewall Configuration](#firewall-configuration)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Server Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 1 core | 2+ cores |
| RAM | 2 GB | 4 GB |
| Disk | 10 GB | 20 GB |
| OS | Ubuntu 20.04+ | Ubuntu 22.04 LTS |

### Initial Server Setup

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install essential tools
sudo apt install -y curl wget git ufw

# Create a non-root user (if not already exists)
sudo adduser scraper-admin
sudo usermod -aG sudo scraper-admin

# Switch to the new user
su - scraper-admin
```

---

## Method 1: Docker Deployment (Recommended)

Docker provides the easiest and most reliable deployment method.

### Step 1: Install Docker

```bash
# Remove old Docker versions (if any)
sudo apt remove docker docker-engine docker.io containerd runc

# Install Docker dependencies
sudo apt update
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Set up Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Verify installation
sudo docker --version
```

### Step 2: Install Docker Compose

```bash
# Download Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make it executable
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
```

### Step 3: Add User to Docker Group

```bash
# Add current user to docker group
sudo usermod -aG docker $USER

# Apply the new group membership
newgrp docker

# Test Docker without sudo
docker run hello-world
```

### Step 4: Deploy the Application

```bash
# Create application directory
mkdir -p ~/flask-crawl4ai-scraper
cd ~/flask-crawl4ai-scraper

# Upload your files or clone from git
# Option 1: Upload files via SCP/SFTP
# Option 2: Clone from repository
# git clone <your-repo-url> .

# If uploading manually, you need these files:
# - app.py
# - requirements.txt
# - Dockerfile.production
# - docker-compose.yml

# Build and start the service
docker-compose up -d

# Check if it's running
docker-compose ps
docker-compose logs -f
```

### Step 5: Test the Deployment

```bash
# Test health endpoint
curl http://localhost:5000/

# Expected output:
# {"status":"healthy","service":"crawl4ai-scraper"}

# Test scraping
curl -X POST http://localhost:5000/scrape \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com"}'
```

### Step 6: Enable Auto-Start on Reboot

```bash
# Enable Docker to start on boot
sudo systemctl enable docker

# Docker Compose services will auto-restart (already configured in docker-compose.yml)
```

---

## Method 2: Direct Python Installation

Use this method if you prefer not to use Docker.

### Step 1: Install Python and Dependencies

```bash
# Install Python 3.11
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# Install pip
curl -sS https://bootstrap.pypa.io/get-pip.py | sudo python3.11

# Install system dependencies for Playwright
sudo apt install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2
```

### Step 2: Set Up Application

```bash
# Create application directory
sudo mkdir -p /opt/flask-scraper
sudo chown $USER:$USER /opt/flask-scraper
cd /opt/flask-scraper

# Upload your application files here
# - app.py
# - requirements.txt

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers
python -m playwright install chromium
python -m playwright install-deps chromium

# Optional: Run crawl4ai setup
crawl4ai-setup
```

### Step 3: Install Gunicorn for Production

```bash
# Still in virtual environment
pip install gunicorn

# Test the application
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app
```

### Step 4: Create Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/flask-scraper.service
```

Add the following content:

```ini
[Unit]
Description=Flask crawl4ai Scraper API
After=network.target

[Service]
Type=notify
User=scraper-admin
Group=scraper-admin
WorkingDirectory=/opt/flask-scraper
Environment="PATH=/opt/flask-scraper/venv/bin"
ExecStart=/opt/flask-scraper/venv/bin/gunicorn \
    --workers 4 \
    --bind 0.0.0.0:5000 \
    --timeout 120 \
    --access-logfile /var/log/flask-scraper/access.log \
    --error-logfile /var/log/flask-scraper/error.log \
    --log-level info \
    app:app

# Restart policy
Restart=always
RestartSec=10

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
```

### Step 5: Create Log Directory and Enable Service

```bash
# Create log directory
sudo mkdir -p /var/log/flask-scraper
sudo chown scraper-admin:scraper-admin /var/log/flask-scraper

# Reload systemd
sudo systemctl daemon-reload

# Start the service
sudo systemctl start flask-scraper

# Enable auto-start on boot
sudo systemctl enable flask-scraper

# Check status
sudo systemctl status flask-scraper

# View logs
sudo journalctl -u flask-scraper -f
```

---

## Nginx Reverse Proxy Setup

Set up Nginx as a reverse proxy for better performance and SSL support.

### Step 1: Install Nginx

```bash
sudo apt update
sudo apt install -y nginx
```

### Step 2: Configure Nginx

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/flask-scraper
```

Add the following configuration:

```nginx
# HTTP Configuration
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;  # Change this!

    # Increase timeouts for slow scraping operations
    proxy_connect_timeout 300s;
    proxy_send_timeout 300s;
    proxy_read_timeout 300s;

    # Increase buffer sizes
    proxy_buffer_size 128k;
    proxy_buffers 4 256k;
    proxy_busy_buffers_size 256k;

    # Logging
    access_log /var/log/nginx/flask-scraper-access.log;
    error_log /var/log/nginx/flask-scraper-error.log;

    # Proxy to Flask application
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Disable buffering for real-time logs
        proxy_buffering off;
    }

    # Health check endpoint (no auth needed)
    location = / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        access_log off;
    }
}
```

### Step 3: Enable Nginx Configuration

```bash
# Enable the site
sudo ln -s /etc/nginx/sites-available/flask-scraper /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx

# Enable auto-start
sudo systemctl enable nginx
```

### Step 4: Test Through Nginx

```bash
# Test with domain or server IP
curl http://your-domain.com/
curl http://your-server-ip/
```

---

## SSL/HTTPS Configuration

Use Let's Encrypt for free SSL certificates.

### Step 1: Install Certbot

```bash
sudo apt update
sudo apt install -y certbot python3-certbot-nginx
```

### Step 2: Obtain SSL Certificate

```bash
# Make sure your domain points to your server's IP
# Then run certbot
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Follow the prompts:
# - Enter email address
# - Agree to terms
# - Choose whether to redirect HTTP to HTTPS (recommended: Yes)
```

### Step 3: Test SSL Configuration

```bash
# Test HTTPS
curl https://your-domain.com/

# Check SSL grade
# Visit: https://www.ssllabs.com/ssltest/
```

### Step 4: Set Up Auto-Renewal

```bash
# Test renewal process
sudo certbot renew --dry-run

# Certbot automatically creates a cron job for renewal
# Check it's there:
sudo systemctl list-timers | grep certbot
```

---

## Firewall Configuration

Configure UFW (Uncomplicated Firewall) for security.

```bash
# Allow SSH (IMPORTANT: Do this first!)
sudo ufw allow OpenSSH
sudo ufw allow 22/tcp

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# If you need direct access to Flask (not recommended for production)
# sudo ufw allow 5000/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status verbose

# Expected output:
# Status: active
# To                         Action      From
# --                         ------      ----
# 22/tcp                     ALLOW       Anywhere
# 80/tcp                     ALLOW       Anywhere
# 443/tcp                    ALLOW       Anywhere
```

---

## Monitoring & Maintenance

### Health Monitoring

Create a simple monitoring script:

```bash
# Create monitoring script
nano ~/monitor-scraper.sh
```

Add the following content:

```bash
#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if service is running
echo -e "\n=== Service Status ==="
if systemctl is-active --quiet flask-scraper 2>/dev/null; then
    echo -e "${GREEN}✓ Service is running${NC}"
elif docker ps | grep -q flask-crawl4ai-scraper; then
    echo -e "${GREEN}✓ Docker container is running${NC}"
else
    echo -e "${RED}✗ Service is not running${NC}"
fi

# Check API health
echo -e "\n=== API Health Check ==="
if curl -s http://localhost:5000/ | grep -q "healthy"; then
    echo -e "${GREEN}✓ API is responding${NC}"
else
    echo -e "${RED}✗ API is not responding${NC}"
fi

# Check resource usage
echo -e "\n=== Resource Usage ==="
if command -v docker &> /dev/null && docker ps | grep -q scraper; then
    docker stats --no-stream flask-crawl4ai-scraper
else
    ps aux | grep gunicorn | grep -v grep | awk '{print "CPU: "$3"% | Memory: "$4"%"}'
fi

# Check disk space
echo -e "\n=== Disk Space ==="
df -h / | tail -1 | awk '{print "Used: "$3" / "$2" ("$5")"}'

# Check logs for errors (last 10)
echo -e "\n=== Recent Errors ==="
if [ -f /var/log/flask-scraper/error.log ]; then
    tail -10 /var/log/flask-scraper/error.log | grep -i error | tail -5
elif docker ps | grep -q scraper; then
    docker logs --tail 10 flask-crawl4ai-scraper 2>&1 | grep -i error | tail -5
else
    echo "No errors found"
fi
```

Make it executable:

```bash
chmod +x ~/monitor-scraper.sh
./monitor-scraper.sh
```

### View Logs

```bash
# Docker logs
docker-compose logs -f --tail 100

# Systemd service logs
sudo journalctl -u flask-scraper -f --lines 100

# Nginx logs
sudo tail -f /var/log/nginx/flask-scraper-access.log
sudo tail -f /var/log/nginx/flask-scraper-error.log
```

### Automatic Backups

Create a backup script:

```bash
# Create backup directory
mkdir -p ~/backups

# Create backup script
nano ~/backup-scraper.sh
```

Add the following:

```bash
#!/bin/bash

BACKUP_DIR=~/backups
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="flask-scraper-backup-$DATE.tar.gz"

# Backup application files
cd ~/flask-crawl4ai-scraper || /opt/flask-scraper
tar -czf "$BACKUP_DIR/$BACKUP_FILE" \
    app.py \
    requirements.txt \
    docker-compose.yml \
    Dockerfile* \
    2>/dev/null

echo "Backup created: $BACKUP_FILE"

# Keep only last 7 backups
cd "$BACKUP_DIR"
ls -t flask-scraper-backup-*.tar.gz | tail -n +8 | xargs rm -f 2>/dev/null

echo "Old backups cleaned up"
```

Make it executable and set up cron:

```bash
chmod +x ~/backup-scraper.sh

# Add to crontab (daily at 2 AM)
crontab -e

# Add this line:
0 2 * * * /home/scraper-admin/backup-scraper.sh >> /home/scraper-admin/backup.log 2>&1
```

### Updating the Application

**Docker method:**
```bash
cd ~/flask-crawl4ai-scraper

# Pull latest changes (if using git)
git pull

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Check logs
docker-compose logs -f
```

**Systemd method:**
```bash
cd /opt/flask-scraper

# Activate virtual environment
source venv/bin/activate

# Update dependencies
git pull  # if using git
pip install --upgrade -r requirements.txt

# Restart service
sudo systemctl restart flask-scraper

# Check status
sudo systemctl status flask-scraper
```

---

## Troubleshooting

### Service Won't Start

```bash
# Check service status
sudo systemctl status flask-scraper

# View detailed logs
sudo journalctl -u flask-scraper -n 50 --no-pager

# Check if port is already in use
sudo lsof -i :5000
sudo netstat -tulpn | grep 5000

# Check permissions
ls -la /opt/flask-scraper
```

### High Memory Usage

```bash
# Check memory usage
free -h
htop  # Install with: sudo apt install htop

# For Docker
docker stats

# Restart service to clear memory
docker-compose restart  # Docker
sudo systemctl restart flask-scraper  # Systemd
```

### Can't Access from Internet

```bash
# Check if Nginx is running
sudo systemctl status nginx

# Check firewall
sudo ufw status

# Check if service is listening
sudo netstat -tulpn | grep 5000
sudo netstat -tulpn | grep 80

# Test locally first
curl http://localhost:5000/
curl http://localhost/

# Check Nginx configuration
sudo nginx -t
```

### SSL Certificate Issues

```bash
# Check certificate status
sudo certbot certificates

# Renew certificate manually
sudo certbot renew --nginx

# Check Nginx SSL configuration
sudo nginx -t

# View certificate expiry
echo | openssl s_client -servername your-domain.com -connect your-domain.com:443 2>/dev/null | openssl x509 -noout -dates
```

### Playwright Browser Errors

```bash
# Reinstall Playwright browsers
source /opt/flask-scraper/venv/bin/activate
python -m playwright install chromium
python -m playwright install-deps chromium

# For Docker, rebuild image
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## Performance Optimization

### 1. Increase Worker Processes

Edit systemd service or docker-compose.yml:

```bash
# For systemd
sudo nano /etc/systemd/system/flask-scraper.service
# Change: --workers 4  to  --workers 8

# For docker-compose, edit Dockerfile.production
# Change: --workers 4  to  --workers 8
```

### 2. Enable Nginx Caching (Optional)

```bash
sudo nano /etc/nginx/sites-available/flask-scraper
```

Add caching configuration:

```nginx
# Add at the top
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=scraper_cache:10m max_size=100m inactive=60m;

# In location block
location /scrape {
    proxy_cache scraper_cache;
    proxy_cache_valid 200 10m;
    proxy_cache_key "$request_uri|$request_body";
    
    # ... rest of proxy configuration
}
```

### 3. Monitor with Prometheus (Advanced)

See DOCKER.md for Prometheus integration examples.

---

## Quick Command Reference

```bash
# Docker Commands
docker-compose up -d              # Start services
docker-compose down               # Stop services
docker-compose logs -f            # View logs
docker-compose restart            # Restart services
docker-compose ps                 # Service status

# Systemd Commands
sudo systemctl start flask-scraper    # Start
sudo systemctl stop flask-scraper     # Stop
sudo systemctl restart flask-scraper  # Restart
sudo systemctl status flask-scraper   # Status
sudo journalctl -u flask-scraper -f   # Logs

# Nginx Commands
sudo systemctl restart nginx      # Restart
sudo nginx -t                     # Test config
sudo systemctl status nginx       # Status

# Firewall Commands
sudo ufw status                   # Check status
sudo ufw allow 80/tcp             # Allow port
sudo ufw deny 5000/tcp            # Deny port

# SSL Commands
sudo certbot renew                # Renew certificates
sudo certbot certificates         # List certificates
```

---

## Security Checklist

- [ ] Created non-root user for running services
- [ ] Enabled firewall (UFW) and configured rules
- [ ] Disabled direct access to Flask port (5000) from internet
- [ ] Set up Nginx reverse proxy
- [ ] Enabled SSL/HTTPS with Let's Encrypt
- [ ] Configured auto-renewal for SSL certificates
- [ ] Set up automatic security updates
- [ ] Reviewed and hardened SSH configuration
- [ ] Implemented rate limiting (optional)
- [ ] Set up monitoring and alerts
- [ ] Configured log rotation
- [ ] Created backup system

---

## Next Steps

1. **Add Authentication**: Implement API key authentication
2. **Rate Limiting**: Use Nginx or Flask-Limiter
3. **Monitoring**: Set up Prometheus + Grafana
4. **Load Balancing**: Deploy multiple instances
5. **CDN**: Use Cloudflare for DDoS protection

---

## Support

For issues specific to:
- **Ubuntu Setup**: Check this guide
- **Docker Deployment**: See [DOCKER.md](DOCKER.md)
- **API Usage**: See [README.md](README.md)
- **Quick Start**: See [QUICKSTART.md](QUICKSTART.md)

---

**Congratulations! Your Flask crawl4ai Scraper API is now running on Ubuntu Server!** 🎉

