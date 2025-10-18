# Docker Deployment Guide

Complete guide for deploying the Flask crawl4ai Scraper API using Docker.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Building the Image](#building-the-image)
3. [Running the Container](#running-the-container)
4. [Docker Compose](#docker-compose)
5. [Environment Variables](#environment-variables)
6. [Production Deployment](#production-deployment)
7. [Troubleshooting](#troubleshooting)
8. [Performance Tuning](#performance-tuning)

---

## Quick Start

### Using Docker Compose (Recommended)

**Default (Development):**
```bash
# Build and start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

**For Low-Resource Servers (1 CPU, 1-2GB RAM):**
```bash
# Use minimal configuration
docker-compose -f docker-compose.minimal.yml up -d
```

**For Production Servers (2+ CPUs, 4+ GB RAM):**
```bash
# Use production configuration with resource limits
docker-compose -f docker-compose.production.yml up -d
```

The API will be available at `http://localhost:5000`

### Using Docker CLI

```bash
# Build the image
docker build -t flask-crawl4ai-scraper .

# Run the container
docker run -d -p 5000:5000 --name scraper-api flask-crawl4ai-scraper

# View logs
docker logs -f scraper-api

# Stop the container
docker stop scraper-api
docker rm scraper-api
```

---

## Building the Image

### Development Build

Uses Flask's built-in development server:

```bash
docker build -t flask-crawl4ai-scraper:latest .
```

### Production Build (Recommended)

Uses Gunicorn WSGI server with 4 workers:

```bash
docker build -f Dockerfile.production -t flask-crawl4ai-scraper:production .
```

**Key Differences:**
- `Dockerfile` - Flask development server (good for testing)
- `Dockerfile.production` - Gunicorn with 4 workers (production-ready)

### Build with Custom Tag

```bash
docker build -t myregistry/flask-crawl4ai-scraper:v1.0.0 .
```

### Build Arguments (if needed)

```bash
docker build \
  --build-arg PYTHON_VERSION=3.11 \
  -t flask-crawl4ai-scraper:latest .
```

### Check Image Size

```bash
docker images flask-crawl4ai-scraper
```

Expected size: ~1.5-2GB (includes Chromium browser)

---

## Running the Container

### Basic Run

```bash
docker run -d \
  --name scraper-api \
  -p 5000:5000 \
  flask-crawl4ai-scraper:latest
```

### Run with Custom Port

```bash
docker run -d \
  --name scraper-api \
  -p 8080:5000 \
  flask-crawl4ai-scraper:latest
```

The API will be available at `http://localhost:8080`

### Run with Resource Limits

```bash
docker run -d \
  --name scraper-api \
  -p 5000:5000 \
  --memory="2g" \
  --cpus="2" \
  flask-crawl4ai-scraper:latest
```

### Run with Volume Mounts (for logs)

```bash
docker run -d \
  --name scraper-api \
  -p 5000:5000 \
  -v $(pwd)/logs:/app/logs \
  flask-crawl4ai-scraper:latest
```

### Run in Foreground (for debugging)

```bash
docker run --rm -it \
  --name scraper-api \
  -p 5000:5000 \
  flask-crawl4ai-scraper:latest
```

---

## Docker Compose

### Configuration File

The included `docker-compose.yml` provides:
- Automatic container restart
- Health checks
- Resource limits
- Port mapping

### Commands

```bash
# Start services in background
docker-compose up -d

# Start services in foreground (see logs)
docker-compose up

# View logs
docker-compose logs -f scraper-api

# Restart service
docker-compose restart

# Stop services
docker-compose stop

# Stop and remove containers
docker-compose down

# Rebuild and restart
docker-compose up -d --build

# View service status
docker-compose ps
```

### Scaling (Multiple Instances)

```bash
# Run 3 instances behind a load balancer
docker-compose up -d --scale scraper-api=3
```

**Note:** You'll need to modify the `docker-compose.yml` to remove the container_name and use a load balancer like nginx.

---

## Environment Variables

### Available Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_ENV` | `production` | Flask environment (development/production) |
| `PYTHONUNBUFFERED` | `1` | Disable Python output buffering |
| `HOST` | `0.0.0.0` | Flask bind address |
| `PORT` | `5000` | Flask port |

### Setting Environment Variables

**Docker CLI:**
```bash
docker run -d \
  -e FLASK_ENV=production \
  -e PORT=8000 \
  -p 8000:8000 \
  flask-crawl4ai-scraper:latest
```

**Docker Compose:**
```yaml
services:
  scraper-api:
    environment:
      - FLASK_ENV=production
      - PORT=5000
```

**Environment File (.env):**
```bash
# Create .env file
cat > .env << EOF
FLASK_ENV=production
PORT=5000
EOF

# Use with docker-compose
docker-compose --env-file .env up -d
```

---

## Production Deployment

### 1. Use Production WSGI Server

Update `Dockerfile` CMD to use Gunicorn:

```dockerfile
# Install gunicorn
RUN pip install gunicorn

# Change CMD
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--timeout", "120", "app:app"]
```

### 2. Enable HTTPS (with Nginx)

Create `nginx.conf`:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://scraper-api:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Increase timeout for slow scrapes
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
}
```

Update `docker-compose.yml`:

```yaml
services:
  scraper-api:
    # ... existing config ...
    expose:
      - "5000"
    networks:
      - backend

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - ./certs:/etc/nginx/certs
    depends_on:
      - scraper-api
    networks:
      - backend

networks:
  backend:
```

### 3. Health Monitoring

The Dockerfile includes a health check:

```bash
# Check container health
docker inspect --format='{{.State.Health.Status}}' scraper-api

# View health check logs
docker inspect --format='{{json .State.Health}}' scraper-api | jq
```

### 4. Logging

**View Logs:**
```bash
# Real-time logs
docker logs -f scraper-api

# Last 100 lines
docker logs --tail 100 scraper-api

# Logs with timestamps
docker logs -t scraper-api
```

**Configure Log Driver:**
```yaml
services:
  scraper-api:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check container logs
docker logs scraper-api

# Check container status
docker ps -a

# Inspect container
docker inspect scraper-api

# Run container in interactive mode
docker run -it --rm --entrypoint /bin/bash flask-crawl4ai-scraper
```

### Playwright Browser Issues

```bash
# Verify Playwright installation inside container
docker exec scraper-api python -m playwright --version

# Test browser launch
docker exec scraper-api python -c "from playwright.sync_api import sync_playwright; sync_playwright().start()"
```

### Memory Issues

```bash
# Check container resource usage
docker stats scraper-api

# Increase memory limit
docker update --memory="4g" scraper-api
```

### Port Already in Use

```bash
# Find process using port 5000
lsof -i :5000  # Linux/Mac
netstat -ano | findstr :5000  # Windows

# Use different port
docker run -p 8080:5000 flask-crawl4ai-scraper
```

### Slow Performance

```bash
# Increase CPU and memory
docker run -d \
  --cpus="4" \
  --memory="4g" \
  -p 5000:5000 \
  flask-crawl4ai-scraper
```

---

## Performance Tuning

### Resource Allocation

**Development:**
- CPUs: 1-2
- Memory: 1-2GB

**Production:**
- CPUs: 2-4
- Memory: 2-4GB

### Concurrency

For handling multiple requests, use Gunicorn with multiple workers:

```bash
# 4 worker processes
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 app:app

# Auto-scale workers (2 * CPU cores + 1)
gunicorn -w $((2 * $(nproc) + 1)) -b 0.0.0.0:5000 app:app
```

### Caching

Enable caching in crawl4ai by modifying `app.py`:

```python
config = CrawlerRunConfig(
    cache_mode=CacheMode.ENABLED,  # Enable caching
    # ... other config
)
```

### Docker Build Optimization

Use BuildKit for faster builds:

```bash
# Enable BuildKit
export DOCKER_BUILDKIT=1

# Build with cache
docker build --cache-from flask-crawl4ai-scraper:latest -t flask-crawl4ai-scraper:latest .
```

---

## CI/CD Integration

### GitHub Actions

```yaml
name: Build and Push Docker Image

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker image
        run: docker build -t flask-crawl4ai-scraper:${{ github.sha }} .
      
      - name: Test image
        run: |
          docker run -d -p 5000:5000 --name test-api flask-crawl4ai-scraper:${{ github.sha }}
          sleep 10
          curl http://localhost:5000/
          docker stop test-api
```

### GitLab CI

```yaml
build:
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
```

---

## Security Best Practices

1. **Run as Non-Root User** ✅ (Already implemented in Dockerfile)

2. **Keep Base Image Updated**
   ```bash
   docker pull python:3.11-slim
   docker build --no-cache -t flask-crawl4ai-scraper .
   ```

3. **Scan for Vulnerabilities**
   ```bash
   docker scan flask-crawl4ai-scraper
   ```

4. **Use Secrets Management**
   ```bash
   docker secret create api_key ./api_key.txt
   docker service create --secret api_key flask-crawl4ai-scraper
   ```

5. **Network Isolation**
   ```yaml
   services:
     scraper-api:
       networks:
         - internal
       # Don't expose ports publicly
   ```

---

## Useful Commands

```bash
# Get shell inside container
docker exec -it scraper-api /bin/bash

# Copy files from container
docker cp scraper-api:/app/logs ./logs

# Export container as image
docker commit scraper-api my-scraper-snapshot

# Save image to file
docker save flask-crawl4ai-scraper:latest | gzip > scraper-image.tar.gz

# Load image from file
gunzip -c scraper-image.tar.gz | docker load

# Remove all stopped containers
docker container prune

# Remove unused images
docker image prune

# Remove everything (use with caution!)
docker system prune -a
```

---

## Support

For issues related to:
- **Docker**: Check Docker logs and documentation
- **crawl4ai**: See [crawl4ai documentation](https://docs.crawl4ai.com/)
- **API Usage**: See main README.md

---

## License

This project is provided as-is for educational and commercial use.

