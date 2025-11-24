"""
Web Scraper for Literature Knowledge Base
Fetches comprehensive literature data from internet sources
Builds and expands knowledge base automatically
"""
import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional
import json
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)

class LiteratureWebScraper:
    """Scrapes literature data from Wikipedia and other sources"""
    
    def __init__(self):
        self.authors_cache = {}
        self.works_cache = {}
        self.movements_cache = {}
        self.session = None
    
    async def fetch_url(self, url: str) -> Optional[str]:
        """Fetch URL with error handling"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    return await resp.text()
        except Exception as e:
            logger.warning(f"Failed to fetch {url}: {e}")
        return None
    
    async def fetch_author_from_wikipedia(self, author_name: str) -> Dict:
        """Fetch comprehensive author information from Wikipedia"""
        try:
            # Wikipedia API endpoint
            url = f"https://en.wikipedia.org/w/api.php?action=query&titles={author_name}&prop=extracts|pageimages&explaintext=1&format=json"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        pages = data.get('query', {}).get('pages', {})
                        
                        for page_id, page in pages.items():
                            if page_id != '-1':
                                extract = page.get('extract', '')[:2000]
                                
                                # Parse key information
                                author_info = {
                                    "name": page.get('title', author_name),
                                    "wikipedia_summary": extract,
                                    "birth_year": extract_year(extract, "born"),
                                    "death_year": extract_year(extract, "died"),
                                    "nationality": extract_nationality(extract),
                                    "era": extract_era(extract),
                                }
                                
                                logger.info(f"✅ Fetched Wikipedia data for {author_name}")
                                return author_info
        except Exception as e:
            logger.warning(f"Wikipedia fetch error for {author_name}: {e}")
        
        return None
    
    async def fetch_work_from_wikipedia(self, work_title: str, author: str = None) -> Dict:
        """Fetch comprehensive work information from Wikipedia"""
        try:
            search_query = f"{work_title} {author}" if author else work_title
            url = f"https://en.wikipedia.org/w/api.php?action=query&titles={search_query}&prop=extracts&explaintext=1&format=json"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        pages = data.get('query', {}).get('pages', {})
                        
                        for page_id, page in pages.items():
                            if page_id != '-1':
                                extract = page.get('extract', '')[:2000]
                                
                                work_info = {
                                    "title": page.get('title', work_title),
                                    "wikipedia_summary": extract,
                                    "author": extract_author(extract),
                                    "year": extract_year(extract, "published|written|year"),
                                    "genre": extract_genre(extract),
                                    "themes": extract_themes(extract),
                                }
                                
                                logger.info(f"✅ Fetched Wikipedia data for {work_title}")
                                return work_info
        except Exception as e:
            logger.warning(f"Wikipedia fetch error for {work_title}: {e}")
        
        return None
    
    async def fetch_multiple_authors(self, author_names: List[str]) -> Dict[str, Dict]:
        """Fetch data for multiple authors concurrently"""
        tasks = [self.fetch_author_from_wikipedia(name) for name in author_names]
        results = await asyncio.gather(*tasks)
        
        return {
            author_names[i]: results[i]
            for i in range(len(author_names))
            if results[i]
        }
    
    async def fetch_multiple_works(self, works: List[tuple]) -> Dict[str, Dict]:
        """Fetch data for multiple works concurrently"""
        tasks = [
            self.fetch_work_from_wikipedia(title, author)
            for title, author in works
        ]
        results = await asyncio.gather(*tasks)
        
        return {
            f"{works[i][0]} by {works[i][1]}": results[i]
            for i in range(len(works))
            if results[i]
        }
    
    async def close(self):
        """Close session"""
        if self.session:
            await self.session.close()


# Helper functions for data extraction
def extract_year(text: str, keywords: str) -> Optional[int]:
    """Extract year from text"""
    pattern = rf"({'|'.join(keywords.split('|'))})\s+(\d{{4}})"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        try:
            return int(match.group(2))
        except:
            pass
    return None


def extract_nationality(text: str) -> str:
    """Extract nationality from text"""
    nationalities = ['Russian', 'English', 'French', 'German', 'American', 'Italian']
    for nat in nationalities:
        if nat.lower() in text.lower():
            return nat
    return "Unknown"


def extract_era(text: str) -> str:
    """Extract literary era"""
    eras = [
        'Romantic', 'Victorian', 'Elizabethan', 'Realist', 'Modernist',
        'Baroque', 'Classical', 'Medieval', 'Renaissance', 'Contemporary'
    ]
    for era in eras:
        if era.lower() in text.lower():
            return era
    return "Unknown"


def extract_author(text: str) -> str:
    """Extract author name from work description"""
    pattern = r"by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)"
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    return "Unknown"


def extract_genre(text: str) -> str:
    """Extract genre from text"""
    genres = ['novel', 'play', 'poem', 'drama', 'tragedy', 'comedy', 'novella', 'short story']
    for genre in genres:
        if genre.lower() in text.lower():
            return genre.capitalize()
    return "Literary Work"


def extract_themes(text: str) -> List[str]:
    """Extract themes from text"""
    themes = [
        'love', 'death', 'power', 'morality', 'freedom', 'society', 'betrayal',
        'redemption', 'justice', 'identity', 'fate', 'madness', 'revenge', 'grief'
    ]
    found_themes = []
    for theme in themes:
        if theme in text.lower():
            found_themes.append(theme.capitalize())
    return found_themes[:3]  # Top 3 themes


async def build_expanded_knowledge_base() -> Dict:
    """Build expanded knowledge base from internet"""
    scraper = LiteratureWebScraper()
    
    try:
        logger.info("🌐 Starting web-based knowledge base expansion...")
        
        # List of famous authors to fetch
        authors_to_fetch = [
            "Leo Tolstoy", "Fyodor Dostoevsky", "Alexander Pushkin",
            "Anton Chekhov", "Nikolai Gogol", "Ivan Turgenev",
            "William Shakespeare", "Jane Austen", "Charles Dickens",
            "Oscar Wilde", "Franz Kafka", "James Joyce",
            "Virginia Woolf", "Ernest Hemingway", "George Bernard Shaw"
        ]
        
        # List of famous works to fetch
        works_to_fetch = [
            ("War and Peace", "Tolstoy"),
            ("Crime and Punishment", "Dostoevsky"),
            ("Eugene Onegin", "Pushkin"),
            ("The Great Gatsby", "Fitzgerald"),
            ("Hamlet", "Shakespeare"),
            ("Pride and Prejudice", "Austen"),
            ("1984", "Orwell"),
            ("The Brothers Karamazov", "Dostoevsky"),
        ]
        
        # Fetch data
        logger.info(f"📖 Fetching {len(authors_to_fetch)} authors...")
        authors_data = await scraper.fetch_multiple_authors(authors_to_fetch)
        
        logger.info(f"📚 Fetching {len(works_to_fetch)} works...")
        works_data = await scraper.fetch_multiple_works(works_to_fetch)
        
        expanded_kb = {
            "authors": authors_data,
            "works": works_data,
            "timestamp": str(asyncio.get_event_loop().time()),
            "sources": ["Wikipedia API"],
        }
        
        logger.info("✅ Knowledge base expansion complete!")
        return expanded_kb
    
    finally:
        await scraper.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    kb = asyncio.run(build_expanded_knowledge_base())
    print(json.dumps(kb, indent=2, ensure_ascii=False))
