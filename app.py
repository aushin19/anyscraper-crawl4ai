from flask import Flask, request, jsonify
import asyncio
from crawl4ai import AsyncWebCrawler, CacheMode, BrowserConfig, CrawlerRunConfig
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from urllib.parse import urlparse
import re

app = Flask(__name__)


def is_valid_url(url):
    """Validate URL format"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
    except Exception:
        return False


@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "crawl4ai-scraper"
    }), 200


@app.route('/scrape', methods=['POST'])
def scrape():
    """Scrape endpoint with validation and error handling"""
    try:
        # Get JSON data
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Request body must be JSON"
            }), 400
        
        # Validate required fields
        url = data.get('url')
        if not url:
            return jsonify({
                "success": False,
                "error": "URL is required"
            }), 400
        
        # Validate URL format
        if not is_valid_url(url):
            return jsonify({
                "success": False,
                "error": "Invalid URL format. Must be a valid HTTP/HTTPS URL"
            }), 400
        
        # Get optional parameters with defaults
        markdown_format = data.get('markdown_format', 'raw')
        include_tags = data.get('include_tags', [])
        exclude_tags = data.get('exclude_tags', [])
        include_images = data.get('include_images', False)
        include_urls = data.get('include_urls', False)
        
        # Advanced filtering parameters
        word_count_threshold = data.get('word_count_threshold', 0)
        exclude_external_links = data.get('exclude_external_links', False)
        exclude_social_media_links = data.get('exclude_social_media_links', False)
        exclude_external_images = data.get('exclude_external_images', False)
        process_iframes = data.get('process_iframes', False)
        
        # Validate markdown_format
        if markdown_format not in ['raw', 'fit']:
            return jsonify({
                "success": False,
                "error": "markdown_format must be either 'raw' or 'fit'"
            }), 400
        
        # Validate include_tags and exclude_tags are lists
        if not isinstance(include_tags, list):
            return jsonify({
                "success": False,
                "error": "include_tags must be an array"
            }), 400
        
        if not isinstance(exclude_tags, list):
            return jsonify({
                "success": False,
                "error": "exclude_tags must be an array"
            }), 400
        
        # Validate boolean parameters
        if not isinstance(include_images, bool):
            return jsonify({
                "success": False,
                "error": "include_images must be a boolean"
            }), 400
        
        if not isinstance(include_urls, bool):
            return jsonify({
                "success": False,
                "error": "include_urls must be a boolean"
            }), 400
        
        # Validate advanced parameters
        if not isinstance(word_count_threshold, int) or word_count_threshold < 0:
            return jsonify({
                "success": False,
                "error": "word_count_threshold must be a non-negative integer"
            }), 400
        
        if not isinstance(exclude_external_links, bool):
            return jsonify({
                "success": False,
                "error": "exclude_external_links must be a boolean"
            }), 400
        
        if not isinstance(exclude_social_media_links, bool):
            return jsonify({
                "success": False,
                "error": "exclude_social_media_links must be a boolean"
            }), 400
        
        if not isinstance(exclude_external_images, bool):
            return jsonify({
                "success": False,
                "error": "exclude_external_images must be a boolean"
            }), 400
        
        if not isinstance(process_iframes, bool):
            return jsonify({
                "success": False,
                "error": "process_iframes must be a boolean"
            }), 400
        
        # Validate that include_tags and exclude_tags are not both provided
        if include_tags and exclude_tags:
            return jsonify({
                "success": False,
                "error": "Cannot use both include_tags and exclude_tags simultaneously. Use one or the other."
            }), 400
        
        # Perform scraping
        async def perform_scrape():
            async with AsyncWebCrawler(verbose=False) as crawler:
                # Build markdown generator options
                markdown_options = {
                    "ignore_links": not include_urls,
                    "ignore_images": not include_images
                }
                
                # Build the crawler run configuration
                config_params = {
                    "cache_mode": CacheMode.BYPASS,  # Always fetch fresh content
                    "remove_overlay_elements": True,  # Remove popups, modals, etc.
                    "markdown_generator": DefaultMarkdownGenerator(
                        content_filter=PruningContentFilter(
                            threshold=0.48, 
                            threshold_type="fixed", 
                            min_word_threshold=0
                        ),
                        options=markdown_options
                    ),
                    # JavaScript to scroll the page
                    "js_code": [
                        "window.scrollTo(0, document.body.scrollHeight);",
                        "await new Promise(resolve => setTimeout(resolve, 2000));",
                        "window.scrollTo(0, 0);"
                    ],
                    "page_timeout": 60000,
                    "delay_before_return_html": 2.0,  # Wait 2 seconds before extracting content
                    
                    # Advanced content filtering
                    "word_count_threshold": word_count_threshold,
                    "exclude_external_links": exclude_external_links,
                    "exclude_social_media_links": exclude_social_media_links,
                    "exclude_external_images": exclude_external_images,
                    "process_iframes": process_iframes
                }
                
                # Handle include_tags: Use target_elements for better flexibility
                # target_elements focuses markdown on specific elements while preserving
                # full page context for links, images, and other media
                if include_tags:
                    # Pass tags as-is since target_elements accepts a list of CSS selectors
                    config_params["target_elements"] = include_tags
                
                # Handle exclude_tags: Exclude specified tags and their children
                if exclude_tags:
                    config_params["excluded_tags"] = exclude_tags
                
                config = CrawlerRunConfig(**config_params)
                
                # Run the crawler with retry logic
                max_retries = 2
                last_error = None
                
                for attempt in range(max_retries):
                    try:
                        result = await crawler.arun(url=url, config=config)
                        if result.success:
                            return result
                        last_error = result.error_message if hasattr(result, 'error_message') else 'Unknown error'
                    except Exception as e:
                        last_error = str(e)
                        if attempt < max_retries - 1:
                            # Wait before retry
                            await asyncio.sleep(1)
                        else:
                            raise
                
                # If we got here, all attempts failed
                raise Exception(last_error if last_error else "Failed to scrape after retries")
        
        # Run async function in sync context
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            scrape_result = loop.run_until_complete(perform_scrape())
            loop.close()
        except asyncio.TimeoutError:
            return jsonify({
                "success": False,
                "error": "Request timeout while scraping the URL"
            }), 504
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Scraping failed: {str(e)}"
            }), 500
        
        # Check if scraping was successful
        if not scrape_result.success:
            return jsonify({
                "success": False,
                "error": f"Failed to scrape URL: {scrape_result.error_message if hasattr(scrape_result, 'error_message') else 'Unknown error'}"
            }), 500
        
        # Get the appropriate markdown based on format
        # New API uses result.markdown.raw_markdown and result.markdown.fit_markdown
        if hasattr(scrape_result, 'markdown'):
            if markdown_format == 'fit':
                markdown_content = scrape_result.markdown.fit_markdown if hasattr(scrape_result.markdown, 'fit_markdown') else scrape_result.markdown.raw_markdown
            else:
                markdown_content = scrape_result.markdown.raw_markdown if hasattr(scrape_result.markdown, 'raw_markdown') else str(scrape_result.markdown)
        else:
            # Fallback for older API
            markdown_content = str(scrape_result.markdown) if hasattr(scrape_result, 'markdown') else ''
        
        # Prepare metadata
        metadata = {}
        if hasattr(scrape_result, 'metadata') and scrape_result.metadata:
            metadata = {
                "title": scrape_result.metadata.get('title', ''),
                "description": scrape_result.metadata.get('description', ''),
                "keywords": scrape_result.metadata.get('keywords', ''),
                "author": scrape_result.metadata.get('author', ''),
                "language": scrape_result.metadata.get('language', '')
            }
        
        # Return successful response
        return jsonify({
            "success": True,
            "url": url,
            "markdown": markdown_content,
            "metadata": metadata
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404


@app.errorhandler(405)
def method_not_allowed(e):
    """Handle 405 errors"""
    return jsonify({
        "success": False,
        "error": "Method not allowed"
    }), 405


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

