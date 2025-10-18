# Changelog

## [Fixed] Playwright Browser Installation Issue

**Date:** 2025-10-18

### Issue
Docker containers were failing with the error:
```
BrowserType.launch: Executable doesn't exist at /home/scraper/.cache/ms-playwright/chromium-1187/chrome-linux/chrome
```

### Root Cause
Playwright browsers were being installed as root user, but the application runs as a non-root user (`scraper`). The browser cache wasn't accessible to the non-root user.

### Changes Made

#### 1. Fixed Dockerfile
- **Changed:** Playwright installation command
  - **Old:** `python -m playwright install chromium && python -m playwright install-deps chromium`
  - **New:** `python -m playwright install chromium --with-deps`
- **Added:** Browser cache copying step
  ```dockerfile
  RUN mkdir -p /home/scraper/.cache && \
      cp -r /root/.cache/ms-playwright /home/scraper/.cache/ && \
      chown -R scraper:scraper /home/scraper/.cache
  ```
- **Added:** Verification step after switching to non-root user
  ```dockerfile
  RUN python -m playwright install chromium --with-deps 2>/dev/null || true
  ```

#### 2. Fixed Dockerfile.production
- Applied the same fixes as Dockerfile
- Maintains Gunicorn production configuration

#### 3. Documentation Reorganization
- Moved all documentation to `/docs` folder:
  - `DOCKER.md` → `/docs/DOCKER.md`
  - `QUICKSTART.md` → `/docs/QUICKSTART.md`
  - `UBUNTU_DEPLOYMENT.md` → `/docs/UBUNTU_DEPLOYMENT.md`
  - `SUMMARY.md` → `/docs/SUMMARY.md`
- Updated all internal documentation links to use relative paths
- Created `REBUILD_INSTRUCTIONS.md` with step-by-step rebuild guide

#### 4. Updated README.md
- Added Docker rebuild instructions in Troubleshooting section
- Added warning note in Installation section
- Updated project structure to show `/docs` folder
- Fixed all documentation references to point to `/docs/` folder

### How to Apply the Fix

**If you already have a container running:**

```bash
# Stop and remove old container
docker stop scraper-api
docker rm scraper-api

# Rebuild with fixed Dockerfile
docker build -t flask-crawl4ai-scraper .

# Run new container
docker run -d -p 5000:5000 --name scraper-api flask-crawl4ai-scraper
```

**With Docker Compose:**

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Files Modified

#### Core Files
- `Dockerfile` - Fixed Playwright installation and permissions
- `Dockerfile.production` - Fixed Playwright installation and permissions
- `README.md` - Updated documentation links and troubleshooting

#### New Files
- `REBUILD_INSTRUCTIONS.md` - Detailed rebuild guide
- `CHANGELOG.md` - This file

#### Documentation (Moved to /docs/)
- `docs/DOCKER.md` - Updated internal links
- `docs/QUICKSTART.md` - Updated internal links
- `docs/UBUNTU_DEPLOYMENT.md` - Updated internal links
- `docs/SUMMARY.md` - Updated internal links

### Testing

After rebuilding, verify the fix works:

```bash
# Test health endpoint
curl http://localhost:5000/

# Test scraping
curl -X POST http://localhost:5000/scrape \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com"}'
```

Expected result: Successful scraping with markdown content returned.

### Impact
- ✅ Docker containers now work out-of-the-box
- ✅ No manual intervention needed after container start
- ✅ Both development and production Dockerfiles fixed
- ✅ Better organized documentation structure
- ✅ Improved troubleshooting documentation

### Breaking Changes
None. This is a bug fix that maintains backward compatibility.

### Migration Guide
No migration needed. Simply rebuild your Docker images with the updated Dockerfiles.

---

## [Improved] Documentation Organization

**Date:** 2025-10-18

### Changes
- Created `/docs` folder for better organization
- Moved all documentation files to `/docs` (except README.md)
- Updated all cross-references between documentation files
- Created comprehensive rebuild instructions

### Benefits
- Cleaner project root directory
- Easier to find documentation
- Better separation of concerns
- Standard documentation structure

---

## Previous Changes

See git commit history for earlier changes.

