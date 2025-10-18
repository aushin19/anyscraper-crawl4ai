# Quick Start Guide

Get the Flask crawl4ai Scraper API running in under 5 minutes!

---

## 🚀 Fastest Method: Docker Compose

```bash
# 1. Clone/Download the project
cd flask-crawl4ai-scraper

# 2. Start the service
docker-compose up -d

# 3. Test the API
curl http://localhost:5000/

# Expected response:
# {"status": "healthy", "service": "crawl4ai-scraper"}
```

**That's it!** The API is now running at `http://localhost:5000`

---

## 📋 Test Your First Scrape

### Basic Scrape
```bash
curl -X POST http://localhost:5000/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

### Clean Article Extraction
```bash
curl -X POST http://localhost:5000/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/article",
    "include_tags": ["article", "main"],
    "exclude_social_media_links": true,
    "word_count_threshold": 10
  }'
```

### Remove Navigation & Ads
```bash
curl -X POST http://localhost:5000/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "exclude_tags": ["nav", "footer", "aside"],
    "exclude_external_images": true
  }'
```

---

## 🐍 Python Client Example

```python
import requests

def scrape_webpage(url, clean=True):
    api_url = "http://localhost:5000/scrape"
    
    payload = {
        "url": url,
        "markdown_format": "fit",
        "exclude_tags": ["nav", "footer", "aside"] if clean else [],
        "exclude_social_media_links": clean,
        "word_count_threshold": 15 if clean else 0
    }
    
    response = requests.post(api_url, json=payload)
    data = response.json()
    
    if data["success"]:
        return data["markdown"]
    else:
        raise Exception(data["error"])

# Usage
content = scrape_webpage("https://example.com", clean=True)
print(content)
```

---

## 🌐 JavaScript/Node.js Client Example

```javascript
async function scrapeWebpage(url, options = {}) {
    const response = await fetch('http://localhost:5000/scrape', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            url: url,
            markdown_format: 'fit',
            exclude_tags: options.excludeTags || ['nav', 'footer', 'aside'],
            exclude_social_media_links: options.clean !== false,
            word_count_threshold: options.wordThreshold || 15
        })
    });
    
    const data = await response.json();
    
    if (data.success) {
        return data.markdown;
    } else {
        throw new Error(data.error);
    }
}

// Usage
scrapeWebpage('https://example.com', { clean: true })
    .then(content => console.log(content))
    .catch(error => console.error(error));
```

---

## 🔧 Common Use Cases

### 1. Blog Post Extraction
```json
{
  "url": "https://blog.example.com/post",
  "include_tags": ["article", "h1", "h2", "p"],
  "exclude_social_media_links": true,
  "word_count_threshold": 20,
  "include_images": false
}
```

### 2. News Article (Clean)
```json
{
  "url": "https://news.example.com/article",
  "exclude_tags": ["nav", "footer", "aside", "header"],
  "exclude_external_links": true,
  "exclude_external_images": true,
  "word_count_threshold": 15
}
```

### 3. Product Page
```json
{
  "url": "https://shop.example.com/product",
  "include_tags": ["main", "article", ".product-info"],
  "include_images": true,
  "include_urls": true,
  "process_iframes": true
}
```

### 4. Documentation Page
```json
{
  "url": "https://docs.example.com/guide",
  "include_tags": ["main", "article", ".content"],
  "markdown_format": "fit",
  "include_urls": true
}
```

---

## 🛠️ Management Commands

### Docker Compose
```bash
# Start service
docker-compose up -d

# View logs
docker-compose logs -f

# Restart service
docker-compose restart

# Stop service
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

### Docker CLI
```bash
# View logs
docker logs -f scraper-api

# Check status
docker ps

# Stop container
docker stop scraper-api

# Start container
docker start scraper-api

# Remove container
docker rm scraper-api
```

---

## 📊 Monitor Your API

### Health Check
```bash
# Check if API is running
curl http://localhost:5000/

# Check Docker container health
docker inspect --format='{{.State.Health.Status}}' flask-crawl4ai-scraper
```

### View Resource Usage
```bash
# Monitor CPU and memory
docker stats flask-crawl4ai-scraper

# View detailed container info
docker inspect flask-crawl4ai-scraper
```

---

## 🐛 Quick Troubleshooting

### API not responding?
```bash
# Check if container is running
docker ps

# View recent logs
docker logs --tail 50 scraper-api

# Restart the service
docker-compose restart
```

### Port already in use?
```bash
# Use a different port
docker run -d -p 8080:5000 --name scraper-api flask-crawl4ai-scraper

# Or stop the conflicting service
# Linux/Mac: lsof -i :5000
# Windows: netstat -ano | findstr :5000
```

### Out of memory?
```bash
# Run with more memory
docker run -d \
  --memory="4g" \
  -p 5000:5000 \
  flask-crawl4ai-scraper
```

---

## 📚 Next Steps

1. **Read Full Documentation**: See [README.md](../README.md) for all API parameters
2. **Production Deployment**: Check [DOCKER.md](DOCKER.md) for production setup
3. **Advanced Features**: Explore all 11 configuration parameters
4. **Scale Your Service**: Learn about horizontal and vertical scaling

---

## 💡 Pro Tips

1. **Use `include_tags` for focused extraction** - Faster and cleaner results
2. **Enable `exclude_social_media_links`** - Removes Twitter, Facebook, etc.
3. **Set `word_count_threshold`** - Filters out short, meaningless blocks
4. **Use `markdown_format: "fit"`** - Better structured output
5. **Combine filters** - Mix and match parameters for optimal results

---

## 🆘 Need Help?

- **API Usage**: [README.md](../README.md)
- **Docker Issues**: [DOCKER.md](DOCKER.md)
- **crawl4ai Docs**: [https://docs.crawl4ai.com/](https://docs.crawl4ai.com/)

---

## ⚡ Performance Tips

### For Faster Scraping
- Use `include_tags` to limit scope
- Set appropriate `word_count_threshold`
- Disable `process_iframes` if not needed

### For Better Results
- Use `markdown_format: "fit"` for cleaner output
- Enable content filters (`exclude_external_links`, etc.)
- Specify precise `include_tags` or `exclude_tags`

### For Production
- Use Docker Compose with resource limits
- Implement rate limiting
- Monitor with health checks
- Use multiple instances behind a load balancer

---

**Happy Scraping! 🎉**

