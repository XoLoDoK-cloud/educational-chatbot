"""
Wikipedia Loader for Literary Information
Asynchronous loader for writer biographies, works, and literary context
"""
import aiohttp
import asyncio
import json
import os
from typing import Dict, List, Optional
from datetime import datetime

class WikipediaLoader:
    """Load literary information from Wikipedia"""
    
    def __init__(self):
        self.cache_file = "wiki_cache.json"
        self.cache = self._load_cache()
        self.wiki_base_url = "https://en.wikipedia.org/w/api.php"
        
    def _load_cache(self) -> Dict:
        """Load cached data from file"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_cache(self):
        """Save cache to file"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    async def get_writer_bio(self, writer_name: str) -> Optional[Dict]:
        """Get writer biography from Wikipedia"""
        # Check cache first
        if writer_name in self.cache:
            return self.cache[writer_name]
        
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'action': 'query',
                    'format': 'json',
                    'titles': writer_name,
                    'prop': 'extracts|pageimages',
                    'exintro': True,
                    'explaintext': True,
                    'piprop': 'thumbnail',
                    'pithumbsize': 200
                }
                
                async with session.get(self.wiki_base_url, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        pages = data.get('query', {}).get('pages', {})
                        
                        for page_id, page_data in pages.items():
                            if 'extract' in page_data:
                                result = {
                                    'title': page_data.get('title', writer_name),
                                    'extract': page_data.get('extract', ''),
                                    'thumbnail': page_data.get('thumbnail', {}).get('source'),
                                    'timestamp': datetime.now().isoformat()
                                }
                                
                                # Cache it
                                self.cache[writer_name] = result
                                self._save_cache()
                                
                                return result
        except:
            pass
        
        return None
    
    async def search_works(self, writer_name: str) -> Optional[List[str]]:
        """Search for writer's major works"""
        try:
            async with aiohttp.ClientSession() as session:
                # Search for writer's works using Wikipedia API
                params = {
                    'action': 'query',
                    'format': 'json',
                    'list': 'search',
                    'srsearch': f'{writer_name} works novels',
                    'srlimit': 10
                }
                
                async with session.get(self.wiki_base_url, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        results = data.get('query', {}).get('search', [])
                        
                        works = []
                        for result in results:
                            if 'novel' in result['title'].lower() or 'work' in result['title'].lower():
                                works.append({
                                    'title': result['title'],
                                    'snippet': result.get('snippet', '')[:200]
                                })
                        
                        return works[:10] if works else None
        except:
            pass
        
        return None
    
    async def get_literary_movement(self, movement_name: str) -> Optional[Dict]:
        """Get information about literary movement"""
        cache_key = f"movement_{movement_name}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'action': 'query',
                    'format': 'json',
                    'titles': movement_name,
                    'prop': 'extracts',
                    'exintro': True,
                    'explaintext': True
                }
                
                async with session.get(self.wiki_base_url, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        pages = data.get('query', {}).get('pages', {})
                        
                        for page_id, page_data in pages.items():
                            if 'extract' in page_data and len(page_data['extract']) > 100:
                                result = {
                                    'title': page_data.get('title', movement_name),
                                    'extract': page_data.get('extract', '')[:500],
                                    'timestamp': datetime.now().isoformat()
                                }
                                
                                self.cache[cache_key] = result
                                self._save_cache()
                                
                                return result
        except:
            pass
        
        return None
    
    async def get_historical_context(self, year: int, era: str) -> Optional[Dict]:
        """Get historical context for a specific era"""
        cache_key = f"context_{era}_{year}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'action': 'query',
                    'format': 'json',
                    'titles': f'{era}',
                    'prop': 'extracts',
                    'exintro': True,
                    'explaintext': True
                }
                
                async with session.get(self.wiki_base_url, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        pages = data.get('query', {}).get('pages', {})
                        
                        for page_id, page_data in pages.items():
                            if 'extract' in page_data:
                                result = {
                                    'era': era,
                                    'extract': page_data.get('extract', '')[:400],
                                    'timestamp': datetime.now().isoformat()
                                }
                                
                                self.cache[cache_key] = result
                                self._save_cache()
                                
                                return result
        except:
            pass
        
        return None


# Global instance
wiki_loader = WikipediaLoader()


async def load_writer_knowledge(writer_name: str) -> Dict:
    """Load complete knowledge about a writer"""
    bio = await wiki_loader.get_writer_bio(writer_name)
    works = await wiki_loader.search_works(writer_name)
    
    return {
        'name': writer_name,
        'biography': bio,
        'works': works,
        'source': 'Wikipedia'
    }


async def load_context(movement: str) -> Dict:
    """Load literary movement context"""
    context = await wiki_loader.get_literary_movement(movement)
    
    return {
        'movement': movement,
        'context': context,
        'source': 'Wikipedia'
    }

