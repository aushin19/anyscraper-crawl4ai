# Docker Image Rebuild Instructions

## Issue Fixed

The Playwright browsers were not being properly installed in the Docker container, causing the error:
```
BrowserType.launch: Executable doesn't exist at /home/scraper/.cache/ms-playwright/chromium-1187/chrome-linux/chrome
```

## What Was Changed

### 1. Updated Dockerfile
- Changed Playwright installation command to use `--with-deps` flag
- Added proper browser cache copying to non-root user directory
- Ensured browsers are installed before switching to non-root user

### 2. Updated Dockerfile.production
- Same fixes as Dockerfile
- Maintains Gunicorn production configuration

### 3. Updated Documentation Links
- All documentation files now properly reference each other
- Moved documentation to `/docs` folder
- Updated all internal links to use relative paths

## How to Rebuild

### Step 1: Stop and Remove Old Container

```bash
# Stop the running container
docker stop scraper-api

# Remove the old container
docker rm scraper-api

# Remove the old image
docker rmi flask-crawl4ai-scraper
```

### Step 2: Rebuild the Image

**For Development:**
```bash
docker build -t flask-crawl4ai-scraper:latest .
```

**For Production:**
```bash
docker build -f Dockerfile.production -t flask-crawl4ai-scraper:production .
```

### Step 3: Run the New Container

**Using Docker CLI:**
```bash
docker run -d -p 5000:5000 --name scraper-api flask-crawl4ai-scraper:latest
```

**Using Docker Compose (Recommended):**
```bash
docker-compose up -d --build
```

### Step 4: Verify the Fix

```bash
# Check container is running
docker ps

# Check logs
docker logs scraper-api

# Test health endpoint
curl http://localhost:5000/

# Test scraping (should work now!)
curl -X POST http://localhost:5000/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

## Verification

You should see a successful response like:
```json
{
  "success": true,
  "url": "https://example.com",
  "markdown": "# Example Domain\n\nThis domain is for use in illustrative examples...",
  "metadata": {
    "title": "Example Domain",
    "description": "..."
  }
}
```

## Quick Rebuild Commands

Copy and paste these commands to rebuild quickly:

```bash
# Stop and clean up
docker stop scraper-api 2>/dev/null || true
docker rm scraper-api 2>/dev/null || true
docker rmi flask-crawl4ai-scraper 2>/dev/null || true

# Rebuild and run
docker build -t flask-crawl4ai-scraper .
docker run -d -p 5000:5000 --name scraper-api flask-crawl4ai-scraper

# Test
sleep 5
curl http://localhost:5000/
```

## Using Docker Compose (Easier)

If you're using Docker Compose:

```bash
# Stop, rebuild, and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# View logs
docker-compose logs -f
```

## Troubleshooting

### If Build Fails

```bash
# Clean Docker build cache
docker builder prune -a

# Try building again
docker build --no-cache -t flask-crawl4ai-scraper .
```

### If Container Still Fails

```bash
# Check container logs
docker logs scraper-api

# Get shell access to debug
docker exec -it scraper-api /bin/bash

# Inside container, check Playwright
python -m playwright install chromium --with-deps
```

### Verify Playwright Inside Container

```bash
# Run this command inside the container
docker exec -it scraper-api python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
```

## Windows-Specific Notes

If you're on Windows PowerShell, use these commands:

```powershell
# Stop and remove
docker stop scraper-api; docker rm scraper-api; docker rmi flask-crawl4ai-scraper

# Rebuild
docker build -t flask-crawl4ai-scraper .

# Run
docker run -d -p 5000:5000 --name scraper-api flask-crawl4ai-scraper

# Test
Start-Sleep -Seconds 5
curl http://localhost:5000/
```

## What's Next

Once your container is running successfully:
1. Test with various URLs
2. Try different configuration parameters
3. See [/docs/QUICKSTART.md](/docs/QUICKSTART.md) for usage examples
4. Check [/docs/DOCKER.md](/docs/DOCKER.md) for production deployment

## Summary of Changes

✅ Fixed Playwright browser installation  
✅ Fixed browser cache permissions for non-root user  
✅ Updated both development and production Dockerfiles  
✅ Organized documentation in `/docs` folder  
✅ Fixed all internal documentation links  

Your Docker container should now work perfectly! 🎉

