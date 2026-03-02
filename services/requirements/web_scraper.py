"""Web scraping utilities for extracting content from URLs."""
import httpx
import logging
from typing import Optional
from urllib.parse import urlparse
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class WebScraper:
    """Scrape and extract content from web pages."""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
    
    async def fetch_url(self, url: str) -> str:
        """Fetch content from a URL."""
        logger.info(f"Fetching URL: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        async with httpx.AsyncClient(
            timeout=self.timeout, 
            follow_redirects=True,
            headers=headers
        ) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                logger.info(f"Successfully fetched URL. Status: {response.status_code}, Content length: {len(response.text)}")
                return response.text
            except httpx.TimeoutException as e:
                logger.error(f"Timeout fetching URL {url}: {str(e)}")
                raise ValueError(f"Request timeout after {self.timeout} seconds. The page took too long to respond.")
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error fetching URL {url}: {e.response.status_code}")
                raise ValueError(f"HTTP error {e.response.status_code}: {e.response.reason_phrase}")
            except httpx.RequestError as e:
                logger.error(f"Request error fetching URL {url}: {str(e)}")
                raise ValueError(f"Failed to connect to URL: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error fetching URL {url}: {str(e)}")
                raise ValueError(f"Failed to fetch URL: {str(e)}")
    
    def extract_text(self, html: str) -> str:
        """Extract clean text from HTML."""
        try:
            logger.info(f"Extracting text from HTML (length: {len(html)})")
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header", "aside", "iframe"]):
                script.decompose()
            
            # Try to find main content area
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content') or soup.body or soup
            
            # Get text
            text = main_content.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            logger.info(f"Extracted text length: {len(text)} characters")
            
            if not text or len(text) < 50:
                logger.warning(f"Extracted text is too short: {len(text)} characters")
            
            return text
        except Exception as e:
            logger.error(f"Failed to extract text from HTML: {str(e)}")
            raise ValueError(f"Failed to extract text from HTML: {str(e)}")
    
    async def scrape_url(self, url: str) -> str:
        """Scrape and extract text from a URL."""
        try:
            html = await self.fetch_url(url)
            text = self.extract_text(html)
            
            if not text or len(text) < 100:
                logger.error(f"Extracted text is too short: {len(text)} characters")
                raise ValueError(f"Extracted text is too short ({len(text)} characters). The page might be empty or require JavaScript.")
            
            logger.info(f"Successfully scraped URL. Final text length: {len(text)}")
            return text
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error scraping URL {url}: {str(e)}")
            raise ValueError(f"Failed to scrape URL: {str(e)}")
    
    @staticmethod
    def is_url_allowed(url: str, whitelist: list[str]) -> bool:
        """Check if URL is in whitelist."""
        if not whitelist:
            return False
        
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        
        logger.info(f"Checking if domain '{domain}' is in whitelist: {whitelist}")
        
        # Check if domain matches any whitelist entry
        for allowed in whitelist:
            allowed_lower = allowed.lower()
            # Exact match or subdomain match
            if domain == allowed_lower or domain.endswith('.' + allowed_lower):
                logger.info(f"Domain '{domain}' matches whitelist entry '{allowed}'")
                return True
        
        logger.warning(f"Domain '{domain}' not in whitelist")
        return False
    
    @staticmethod
    def extract_metadata(html: str) -> dict:
        """Extract metadata from HTML (title, description, etc)."""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            metadata = {}
            
            # Title
            if soup.title:
                metadata['title'] = soup.title.string
            
            # Meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                metadata['description'] = meta_desc['content']
            
            # Open Graph title
            og_title = soup.find('meta', property='og:title')
            if og_title and og_title.get('content'):
                metadata['og_title'] = og_title['content']
            
            # Open Graph description
            og_desc = soup.find('meta', property='og:description')
            if og_desc and og_desc.get('content'):
                metadata['og_description'] = og_desc['content']
            
            logger.info(f"Extracted metadata: {metadata}")
            return metadata
        except Exception as e:
            logger.error(f"Failed to extract metadata: {str(e)}")
            return {}
