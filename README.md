# Flask crawl4ai Scraper API

A Flask-based web scraping API powered by crawl4ai that supports server-side rendering, automatic scrolling, and flexible content extraction.

## Features

- ✅ Health check endpoint
- ✅ Flexible scraping with markdown output (raw/fit formats)
- ✅ Advanced tag-based filtering (include/exclude specific HTML tags)
- ✅ Content quality filtering (word count threshold)
- ✅ External link and social media filtering
- ✅ External image filtering
- ✅ Iframe content extraction
- ✅ Image and URL extraction control
- ✅ Automatic page scrolling for lazy-loaded content
- ✅ Server-side rendering support (JavaScript-heavy sites)
- ✅ Comprehensive error handling and validation
- ✅ Reliable tag-based extraction using `css_selector`

## Installation

### Option 1: Docker (Recommended for Production)

**Quick Start:**
```bash
# Using Docker Compose (Default - Works on any server)
docker-compose up -d --build

# For low-resource servers (1 CPU, 1-2GB RAM)
docker-compose -f docker-compose.minimal.yml up -d --build

# For production servers (2+ CPUs, 4+ GB RAM)
docker-compose -f docker-compose.production.yml up -d --build

# The API will be available at http://localhost:5000
```

**Manual Docker:**
```bash
# Build the image
docker build -t flask-crawl4ai-scraper .

# Run the container
docker run -d -p 5000:5000 --name scraper-api flask-crawl4ai-scraper

# View logs
docker logs -f scraper-api
```

> ⚠️ **Note:** If you encounter Playwright browser errors, see [REBUILD_INSTRUCTIONS.md](REBUILD_INSTRUCTIONS.md) for the fix.

📖 **See [DOCKER.md](/docs/DOCKER.md) for comprehensive Docker documentation including:**
- Production deployment guide
- Resource tuning
- Health monitoring
- Troubleshooting
- CI/CD integration

---

### Option 2: Local Installation

#### Prerequisites

- Python 3.11+ recommended
- pip package manager

#### Setup Steps

1. **Clone or download this project**

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers**
   ```bash
   python -m playwright install
   ```
   
   This command downloads the necessary browser components (Chromium) for headless scraping.
   
   **Note:** On Windows, you must use `python -m playwright install` instead of just `playwright install`.

4. **Set up crawl4ai (optional)**
   ```bash
   crawl4ai-setup
   ```
   
   This command performs additional crawl4ai setup if needed.

5. **Run the application**
   ```bash
   python app.py
   ```
   
   The API will be available at `http://localhost:5000`

## API Documentation

### 1. Health Check

**Endpoint:** `GET /`

**Description:** Check if the service is running.

**Response:**
```json
{
  "status": "healthy",
  "service": "crawl4ai-scraper"
}
```

**Example:**
```bash
curl http://localhost:5000/
```

---

### 2. Scrape Webpage

**Endpoint:** `POST /scrape`

**Description:** Scrape a webpage and return markdown-formatted content.

**Request Body (JSON):**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `url` | string | Yes | - | The URL to scrape (must be valid HTTP/HTTPS) |
| `markdown_format` | string | No | `"raw"` | Output format: `"raw"` or `"fit"`. Note: `"fit"` may auto-fallback to `"raw"` when using `include_tags`. |
| `include_tags` | array | No | `[]` | Extract ONLY these HTML tags and their children. Uses `css_selector`. Cannot be used with `exclude_tags`. |
| `exclude_tags` | array | No | `[]` | Exclude these HTML tags and their children. Cannot be used with `include_tags`. |
| `include_images` | boolean | No | `false` | Include images in markdown |
| `include_urls` | boolean | No | `false` | Include URLs in markdown |
| `word_count_threshold` | integer | No | `0` | Minimum word count for content blocks (filters out short blocks) |
| `exclude_external_links` | boolean | No | `false` | Remove all external links from the content |
| `exclude_social_media_links` | boolean | No | `false` | Remove links to social media platforms |
| `exclude_external_images` | boolean | No | `false` | Remove images hosted on external domains |
| `process_iframes` | boolean | No | `false` | Extract and merge iframe content into the main content |

**Important Notes:**
- `include_tags` and `exclude_tags` cannot be used together in the same request
- `include_tags`: Extracts ONLY listed elements and their children, removes everything else
- `exclude_tags`: Removes listed tags and their children, everything else is kept
- `markdown_format`: When using `include_tags`, if `"fit"` returns empty content, it automatically falls back to `"raw"`
- `exclude_social_media_links`: Automatically filters facebook.com, twitter.com, x.com, linkedin.com, instagram.com, pinterest.com, tiktok.com, snapchat.com, reddit.com

**Response (Success):**
```json
{
  "success": true,
  "url": "https://example.com",
  "markdown": "# Page Content\n\nScraped markdown content...",
  "metadata": {
    "title": "Page Title",
    "description": "Page description"
  }
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Error message describing what went wrong"
}
```

**Status Codes:**
- `200` - Success
- `400` - Bad Request (invalid parameters)
- `500` - Internal Server Error (scraping failed)
- `504` - Gateway Timeout (request took too long)

---

## Usage Examples

### Basic Scraping

```bash
curl -X POST http://localhost:5000/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com"
  }'
```

### Scraping with Images and URLs

```bash
curl -X POST http://localhost:5000/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "include_images": true,
    "include_urls": true
  }'
```

### Using Fit Markdown Format

```bash
curl -X POST http://localhost:5000/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "markdown_format": "fit"
  }'
```

### Including Only Specific Tags

Extract ONLY specific tags and their children (everything else is removed):

```bash
curl -X POST http://localhost:5000/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "include_tags": ["article", "main", "p"]
  }'
```

This will only scrape content from `<article>`, `<main>`, and `<p>` tags and their children. All other content (nav, footer, aside, etc.) will be ignored.

### Excluding Specific Tags

Remove specific tags and their children (everything else is kept):

```bash
curl -X POST http://localhost:5000/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "exclude_tags": ["nav", "footer", "aside", "script", "style"]
  }'
```

This will scrape all content EXCEPT `<nav>`, `<footer>`, `<aside>`, `<script>`, and `<style>` tags and their children.

### Advanced Content Filtering

Clean up scraped content by filtering external resources and short blocks:

```bash
curl -X POST http://localhost:5000/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "word_count_threshold": 10,
    "exclude_external_links": true,
    "exclude_social_media_links": true,
    "exclude_external_images": true,
    "process_iframes": true
  }'
```

This will:
- Skip text blocks with fewer than 10 words
- Remove all external links
- Remove social media links (Facebook, Twitter, LinkedIn, etc.)
- Remove images hosted on external domains
- Extract and merge content from iframes

### Python Example - Include Only Article Content

```python
import requests

url = "http://localhost:5000/scrape"
payload = {
    "url": "https://example.com/article",
    "markdown_format": "fit",
    "include_tags": ["article", "h1", "h2", "p"],  # Focus on article content
    "include_images": False,
    "include_urls": True,
    "word_count_threshold": 15,  # Skip blocks with <15 words
    "exclude_social_media_links": True  # Remove social media links
}

response = requests.post(url, json=payload)
data = response.json()

if data["success"]:
    print(f"Title: {data['metadata']['title']}")
    print(f"Content:\n{data['markdown']}")
else:
    print(f"Error: {data['error']}")
```

### Python Example - Clean Scraping with Advanced Filters

```python
import requests

url = "http://localhost:5000/scrape"
payload = {
    "url": "https://example.com",
    "markdown_format": "raw",
    "exclude_tags": ["nav", "footer", "aside"],  # Remove navigation
    "exclude_external_links": True,  # Remove external links
    "exclude_social_media_links": True,  # Remove social media
    "exclude_external_images": True,  # Only local images
    "word_count_threshold": 20,  # Skip short blocks
    "process_iframes": True,  # Include iframe content
    "include_images": True,
    "include_urls": True
}

response = requests.post(url, json=payload)
data = response.json()

if data["success"]:
    print(f"Title: {data['metadata']['title']}")
    print(f"Content length: {len(data['markdown'])} chars")
    print(f"Clean content without ads, social links, or short blocks")
else:
    print(f"Error: {data['error']}")
```

### JavaScript Example - Only Main Content

```javascript
fetch('http://localhost:5000/scrape', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    url: 'https://example.com',
    markdown_format: 'fit',
    include_tags: ['main', 'article'],  // Only include main content areas
    include_images: false,
    include_urls: true
  })
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    console.log('Title:', data.metadata.title);
    console.log('Content:', data.markdown);
  } else {
    console.error('Error:', data.error);
  }
});
```

## Configuration

### Environment Variables

You can customize the server configuration:

**Local Development** - Modify `app.py`:
- **Host:** Change `host='0.0.0.0'` in `app.run()` to restrict access
- **Port:** Change `port=5000` to use a different port
- **Debug Mode:** Set `debug=False` for production environments

**Docker** - Set environment variables:
```bash
docker run -d \
  -e FLASK_ENV=production \
  -e PORT=5000 \
  -p 5000:5000 \
  flask-crawl4ai-scraper
```

### Production Deployment

#### Option 1: Docker (Recommended)

See [DOCKER.md](/docs/DOCKER.md) for complete production deployment guide.

```bash
# Quick production deployment
docker-compose up -d

# With custom resources
docker run -d \
  --cpus="2" \
  --memory="2g" \
  -p 5000:5000 \
  flask-crawl4ai-scraper
```

#### Option 2: WSGI Server (Local)

For production without Docker, use Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 app:app
```

#### Option 3: With Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_connect_timeout 300s;
        proxy_read_timeout 300s;
    }
}
```

## Troubleshooting

### Issue: "Executable doesn't exist" or Playwright browser errors

**Local Installation Solution:**
```bash
python -m playwright install chromium --with-deps
```

**Windows users:** Always use `python -m playwright` instead of just `playwright`.

**Docker Solution:**
If you get this error in Docker, rebuild the image:
```bash
# Stop and remove old container
docker stop scraper-api && docker rm scraper-api

# Rebuild with fixed Dockerfile
docker build -t flask-crawl4ai-scraper .

# Run new container
docker run -d -p 5000:5000 --name scraper-api flask-crawl4ai-scraper
```

Or with Docker Compose:
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

📖 **See [REBUILD_INSTRUCTIONS.md](REBUILD_INSTRUCTIONS.md) for detailed rebuild guide.**

### Issue: "crawl4ai-setup command not found"

**Solution:** Make sure crawl4ai is installed correctly:
```bash
pip install --upgrade crawl4ai
```

### Issue: Other browser-related errors

**Solution:** Run the setup commands again:
```bash
python -m playwright install
crawl4ai-setup
```

### Issue: Timeout errors on slow websites

**Solution:** The default timeout is handled by crawl4ai. For very slow sites, you may need to modify the crawler configuration in `app.py`.

### Issue: Incomplete content scraping

**Solution:** The API automatically scrolls to the bottom of the page and waits for content to load. The crawler uses `networkidle` wait strategy to ensure the page is fully loaded before extracting content.

### Issue: "Page is navigating and changing content" error

**Solution:** This is a transient error that occurs with dynamic JavaScript-heavy sites. The API now includes:
- Automatic retry logic (up to 2 attempts)
- 2-second delay before content extraction
- Proper timing for JavaScript execution

If errors persist, the site may have anti-scraping measures or very slow loading times.

### Issue: "Wait condition failed: Timeout after 60000ms" error

**Solution:** This has been resolved in the current version. The API now uses `delay_before_return_html` instead of `wait_for='networkidle'` which is compatible with crawl4ai 0.7.4+. If you still encounter this:
- The page may be genuinely slow or stuck
- Try again - the retry logic should handle transient issues
- Some sites may have anti-bot protection

### Issue: Memory usage is high

**Solution:** The AsyncWebCrawler creates browser instances. Ensure you're not making too many concurrent requests. Consider implementing rate limiting for production use.

### Issue: "range of CPUs is from 0.01 to 1.00" on low-resource servers

**Solution:** Your server has limited CPUs. Use the minimal Docker Compose configuration:

```bash
docker-compose -f docker-compose.minimal.yml up -d --build
```

Or edit `docker-compose.yml` and comment out the `deploy:` section (already done in the default file).

📖 **See [LOW_RESOURCE_SERVER_FIX.md](LOW_RESOURCE_SERVER_FIX.md) for complete guide.**

### Issue: "Cannot use both include_tags and exclude_tags simultaneously"

**Solution:** You can only use one filtering method per request:
- Use `include_tags` to whitelist specific elements (only those tags are kept)
- Use `exclude_tags` to blacklist specific elements (everything except those tags is kept)
- Choose the approach that requires fewer tags to specify

## Tag Filtering Behavior

### Include Tags (Whitelist) - Uses `css_selector`
When you specify `include_tags`, the scraper will:
- ✅ Extract ONLY the specified tags and their children
- ✅ Remove all other content from the page
- 🎯 Use this when you know exactly what content you want (e.g., only tables, articles)
- ⚡ Disables PruningContentFilter for more reliable extraction

**Example:** `include_tags: ["table"]` will extract ONLY `<table>` elements from the page.

**Why This Works Better:**
- More reliable extraction for specific elements (like tables)
- Disables aggressive content filtering
- Ensures all content from target tags is captured
- Works consistently in Docker and local environments
- Automatically uses `raw` markdown when `fit` is empty (with include_tags)

**Technical Note:** Uses crawl4ai's `css_selector` parameter which is more reliable than `target_elements` for tag-specific extraction.

### Exclude Tags (Blacklist)
When you specify `exclude_tags`, the scraper will:
- ✅ Extract ALL content from the page
- ❌ Remove only the specified tags and their children
- 🎯 Use this when you want most content but need to remove specific elements (e.g., navigation, footers, ads)

**Example:** `exclude_tags: ["nav", "footer", "aside"]` will scrape everything EXCEPT navigation, footer, and sidebar elements.

### Best Practices
- Use `include_tags` for focused extraction (articles, blog posts, specific sections)
- Use `exclude_tags` for general scraping with noise removal (remove ads, navigation, etc.)
- Cannot use both in the same request - choose the approach that makes sense for your use case
- Combine with `word_count_threshold` to filter trivial content blocks
- Use `exclude_external_links` and `exclude_social_media_links` for cleaner content
- Enable `process_iframes` if the site embeds content in iframes

### Advanced Filtering Combinations

**Clean Article Extraction:**
```json
{
  "include_tags": ["article", "main"],
  "word_count_threshold": 15,
  "exclude_social_media_links": true,
  "exclude_external_images": true
}
```

**General Content Scraping (Clean):**
```json
{
  "exclude_tags": ["nav", "footer", "aside", "header"],
  "word_count_threshold": 10,
  "exclude_external_links": false,
  "exclude_social_media_links": true
}
```

**Data Collection (Preserve Everything):**
```json
{
  "markdown_format": "raw",
  "include_images": true,
  "include_urls": true,
  "process_iframes": true
}
```

## Technical Details

- **Framework:** Flask 3.0+
- **Scraper:** crawl4ai 0.7.4+
- **Browser:** Headless Chromium (via Playwright)
- **Async Handling:** asyncio for crawler operations
- **Tag Filtering:** css_selector for include_tags, excluded_tags for exclusion
- **Content Filtering:** PruningContentFilter for intelligent content extraction
- **Wait Strategy:** 2-second delay before HTML extraction for full page load
- **Retry Logic:** Automatic retry on transient errors (up to 2 attempts)
- **Timeout:** 60 second page timeout
- **Scrolling:** Automatic scroll to bottom with 2-second settle delay
- **Overlay Removal:** Automatically removes popups, modals, and overlays
- **Default Behavior:** Handles server-side rendering and lazy-loaded content

## Project Structure

```
flask-crawl4ai-scraper/
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── test.py                   # Test/example script
│
├── Dockerfile               # Docker image (development)
├── Dockerfile.production    # Docker image (production with Gunicorn)
├── docker-compose.yml       # Docker Compose (default, works on any server)
├── docker-compose.minimal.yml   # For low-resource servers (1 CPU)
├── docker-compose.production.yml # For production servers (2+ CPUs)
├── .dockerignore            # Docker build exclusions
├── .gitignore               # Git exclusions
│
├── README.md                # Main documentation (this file)
├── CHANGELOG.md             # Version history and fixes
├── INCLUDE_TAGS_FIX.md      # Fix for empty markdown with include_tags
└── docs/
    ├── QUICKSTART.md        # Quick start guide (5 minutes)
    ├── DOCKER.md            # Comprehensive Docker guide
    ├── UBUNTU_DEPLOYMENT.md # Ubuntu server deployment guide
    └── SUMMARY.md           # Project overview & reference
```

## API Response Schema

### Success Response
```json
{
  "success": true,
  "url": "https://example.com",
  "markdown": "# Page Title\n\nContent here...",
  "metadata": {
    "title": "Page Title",
    "description": "Page description",
    "keywords": "keyword1, keyword2",
    "author": "Author Name",
    "language": "en"
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": "Detailed error message"
}
```

## Performance Considerations

### Resource Requirements

| Deployment | CPU | Memory | Disk |
|------------|-----|--------|------|
| Development | 1 core | 1-2 GB | 2 GB |
| Production (Light) | 2 cores | 2 GB | 2 GB |
| Production (Heavy) | 4 cores | 4 GB | 3 GB |

### Scaling

**Horizontal Scaling:**
- Deploy multiple instances behind a load balancer
- Each instance can handle 10-50 concurrent requests (depends on target sites)

**Vertical Scaling:**
- Increase CPU for faster JavaScript execution
- Increase memory for handling multiple browsers

### Rate Limiting (Recommended)

Consider implementing rate limiting for production:

```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.remote_addr,
    default_limits=["100 per hour"]
)

@app.route('/scrape', methods=['POST'])
@limiter.limit("10 per minute")
def scrape():
    # ... existing code
```

## Security Considerations

1. **API Authentication** - Consider adding API key authentication
2. **URL Validation** - Already implemented (HTTP/HTTPS only)
3. **Rate Limiting** - Implement to prevent abuse
4. **Input Sanitization** - All inputs are validated
5. **CORS** - Configure based on your needs
6. **HTTPS** - Use reverse proxy (Nginx) with SSL certificates

## Monitoring

### Health Check Endpoint

```bash
# Simple health check
curl http://localhost:5000/

# Response
{"status": "healthy", "service": "crawl4ai-scraper"}
```

### Docker Health Checks

The Docker image includes automatic health monitoring:

```bash
# Check container health
docker inspect --format='{{.State.Health.Status}}' scraper-api
```

### Logging

**Docker:**
```bash
docker logs -f scraper-api
```

**Local:**
Logs are printed to stdout by Flask.

## Roadmap

- [ ] API key authentication
- [ ] Rate limiting middleware
- [ ] Response caching
- [ ] Webhook support for long-running scrapes
- [ ] Batch scraping endpoint
- [ ] Screenshot capture option
- [ ] PDF generation from markdown

## License

This project is provided as-is for educational and commercial use.

## Contributing

Feel free to submit issues and enhancement requests!

## 📚 Documentation Index

| Document | Description | Lines |
|----------|-------------|-------|
| **[README.md](README.md)** | Main documentation - API usage, features, and examples | 700+ |
| **[QUICKSTART.md](/docs/QUICKSTART.md)** | Get started in 5 minutes - Quick commands and examples | 300+ |
| **[DOCKER.md](/docs/DOCKER.md)** | Comprehensive Docker guide - Deployment, monitoring, troubleshooting | 400+ |
| **[UBUNTU_DEPLOYMENT.md](/docs/UBUNTU_DEPLOYMENT.md)** | Complete Ubuntu server deployment guide with Nginx, SSL, monitoring | 600+ |
| **[SUMMARY.md](/docs/SUMMARY.md)** | Project overview, architecture, and quick reference | 400+ |
| **[crawl4ai Docs](https://docs.crawl4ai.com/)** | Official crawl4ai documentation | External |
| **[Flask Docs](https://flask.palletsprojects.com/)** | Flask web framework documentation | External |

**Total Documentation:** 2,400+ lines covering all aspects of the API

## Credits

Built with:
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [crawl4ai](https://crawl4ai.com/) - Web scraping engine
- [Playwright](https://playwright.dev/) - Browser automation
- [Python](https://python.org/) - Programming language

