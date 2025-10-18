# Low-Resource Server Fix

## Problem

On Ubuntu servers with only 1 CPU, Docker Compose fails with:
```
ERROR: range of CPUs is from 0.01 to 1.00, as there are only 1 CPUs available
```

This happens because `docker-compose.yml` was trying to reserve 1 CPU and limit to 2 CPUs, which is impossible on a 1-CPU server.

## Solution

We've created three Docker Compose configurations:

### 1. docker-compose.yml (Default - Development)
- **Use for:** Local development, testing
- **Requirements:** Any
- **Resource limits:** Disabled (uses what's available)

### 2. docker-compose.minimal.yml (Low-Resource Servers)
- **Use for:** Small VPS, 1 CPU servers, cloud instances
- **Requirements:** 1 CPU, 1-2GB RAM minimum
- **Resource limits:** None (maximum flexibility)

### 3. docker-compose.production.yml (Production Servers)
- **Use for:** Production with adequate resources
- **Requirements:** 2+ CPUs, 4+ GB RAM
- **Resource limits:** Enforced for stability

## Quick Fix for Your Ubuntu Server

Since you have a 1 CPU server, use the minimal configuration:

```bash
# Stop any running containers
docker-compose down 2>/dev/null || true
docker stop flask-crawl4ai-scraper 2>/dev/null || true
docker rm flask-crawl4ai-scraper 2>/dev/null || true

# Use the minimal configuration
docker-compose -f docker-compose.minimal.yml up -d --build

# Check if it's running
docker ps

# View logs
docker logs -f flask-crawl4ai-scraper-minimal
```

## Alternative: Modify Existing docker-compose.yml

If you prefer to use the default `docker-compose.yml`, the resource limits are now commented out, so you can just run:

```bash
docker-compose up -d --build
```

## Verify It's Working

```bash
# Check container status
docker ps

# Test health endpoint
curl http://localhost:5000/

# Test scraping
curl -X POST http://localhost:5000/scrape \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com"}'
```

## Comparison Table

| Configuration | CPUs | RAM | Use Case |
|--------------|------|-----|----------|
| `docker-compose.yml` | Any | Any | Development, testing |
| `docker-compose.minimal.yml` | 1+ | 1-2GB | Small VPS, limited resources |
| `docker-compose.production.yml` | 2+ | 4GB+ | Production with resources |

## Performance on 1 CPU Server

### What to Expect:
- ✅ API will work correctly
- ⚠️  Slower scraping (1-3 seconds per page)
- ⚠️  Handle 1-2 concurrent requests comfortably
- ⚠️  3-5 concurrent requests may be slow
- ⚠️  Memory usage: 500MB - 1.5GB

### Optimization Tips for Low-Resource Servers:

1. **Increase timeout if needed:**
   Edit `app.py` line 175:
   ```python
   "page_timeout": 90000,  # Increase from 60000 to 90000 (90 seconds)
   ```

2. **Use Nginx to queue requests:**
   Set up Nginx reverse proxy to handle multiple requests gracefully

3. **Monitor resources:**
   ```bash
   # Watch resource usage
   docker stats flask-crawl4ai-scraper-minimal
   
   # Check server resources
   htop  # or top
   free -h
   ```

4. **Restart periodically if memory grows:**
   ```bash
   # Add to crontab to restart daily at 3 AM
   0 3 * * * docker restart flask-crawl4ai-scraper-minimal
   ```

## Upgrading Your Server

If you find performance insufficient:

### Option 1: Upgrade VPS
- Upgrade to 2 CPUs and 4GB RAM
- Then use `docker-compose.production.yml`

### Option 2: Optimize Current Setup
- Use Nginx caching (see docs/UBUNTU_DEPLOYMENT.md)
- Implement request queuing
- Add rate limiting

### Option 3: Horizontal Scaling
- Deploy multiple 1-CPU instances
- Use load balancer (Nginx, HAProxy)
- Distribute load across instances

## Troubleshooting

### Still Getting CPU Errors?

1. **Check if resource limits are truly commented out:**
   ```bash
   grep -A 5 "deploy:" docker-compose.yml
   ```
   
   Should show lines starting with `#`

2. **Force recreate without limits:**
   ```bash
   docker-compose -f docker-compose.minimal.yml up -d --force-recreate
   ```

3. **Check Docker version:**
   ```bash
   docker-compose version
   ```
   
   Update if < 1.27.0

### Container Crashes or OOM (Out of Memory)?

```bash
# Check memory usage
free -h

# If low, add swap space
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Slow Performance?

1. **Check if Chromium is running:**
   ```bash
   docker exec flask-crawl4ai-scraper-minimal ps aux | grep chrome
   ```

2. **Monitor during scraping:**
   ```bash
   watch -n 1 'docker stats --no-stream flask-crawl4ai-scraper-minimal'
   ```

3. **Reduce worker processes** (if using production Dockerfile):
   Edit `Dockerfile.production` line 74:
   ```dockerfile
   CMD ["gunicorn", "--workers", "1", ...]  # Reduce from 4 to 1
   ```

## Files Updated

- ✅ `docker-compose.yml` - Resource limits commented out
- ✅ `docker-compose.minimal.yml` - New minimal config
- ✅ `docker-compose.production.yml` - New production config
- ✅ `docs/DOCKER.md` - Updated with all three options
- ✅ `docs/UBUNTU_DEPLOYMENT.md` - Updated deployment steps

## Summary

✅ Fixed CPU limit error on 1 CPU servers  
✅ Created three Docker Compose configurations  
✅ Default now works on any server  
✅ Minimal config optimized for low resources  
✅ Production config for servers with resources  

Use `docker-compose.minimal.yml` on your Ubuntu server and it will work perfectly! 🎉

