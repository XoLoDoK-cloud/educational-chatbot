"""
Асинхронная загрузка полного списка писателей из Wikipedia
Заполняет базу данных comprehensive_knowledge.py
"""
import asyncio
import aiohttp
import json
from typing import List, Dict, Optional


class WikipediaBulkLoader:
    """Массовая загрузка писателей из Wikipedia"""
    
    def __init__(self):
        self.wiki_url = "https://en.wikipedia.org/w/api.php"
        self.cache_file = "writers_bulk_cache.json"
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """Загрузить кэш"""
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_cache(self):
        """Сохранить кэш"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    async def search_writers_by_category(self, category: str, limit: int = 30) -> List[str]:
        """Поиск писателей в категории Wikipedia"""
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'action': 'query',
                    'format': 'json',
                    'list': 'categorymembers',
                    'cmtitle': f'Category:{category}',
                    'cmlimit': limit,
                    'cmtype': 'page'
                }
                
                async with session.get(self.wiki_url, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        members = data.get('query', {}).get('categorymembers', [])
                        return [m['title'] for m in members]
        except:
            pass
        
        return []
    
    async def get_writer_details(self, writer_name: str) -> Optional[Dict]:
        """Получить детали писателя"""
        if writer_name in self.cache:
            return self.cache[writer_name]
        
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'action': 'query',
                    'format': 'json',
                    'titles': writer_name,
                    'prop': 'extracts|pageimages|info',
                    'exintro': True,
                    'explaintext': True,
                    'piprop': 'thumbnail',
                    'pithumbsize': 300
                }
                
                async with session.get(self.wiki_url, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        pages = data.get('query', {}).get('pages', {})
                        
                        for page_id, page_data in pages.items():
                            if int(page_id) > 0 and 'extract' in page_data:
                                result = {
                                    'title': page_data.get('title', writer_name),
                                    'extract': page_data.get('extract', '')[:1000],
                                    'url': f"https://en.wikipedia.org/wiki/{writer_name.replace(' ', '_')}",
                                    'thumbnail': page_data.get('thumbnail', {}).get('source')
                                }
                                
                                self.cache[writer_name] = result
                                self._save_cache()
                                
                                return result
        except:
            pass
        
        return None
    
    async def load_major_categories(self) -> Dict[str, List[str]]:
        """Загрузить писателей из основных категорий"""
        categories = {
            'American novelists': 15,
            'English writers': 15,
            'French writers': 15,
            'Russian writers': 15,
            'German writers': 10,
            'Italian writers': 10,
            'Spanish writers': 10,
            'Latin American writers': 10,
            'Asian writers': 10,
            'Poets': 20,
        }
        
        all_writers = {}
        
        for category, limit in categories.items():
            writers = await self.search_writers_by_category(category, limit)
            all_writers[category] = writers
        
        return all_writers
    
    async def populate_writer_details(self, writers_list: List[str]) -> List[Dict]:
        """Заполнить детали для списка писателей"""
        results = []
        
        for writer in writers_list:
            details = await self.get_writer_details(writer)
            if details:
                results.append(details)
                await asyncio.sleep(0.1)  # Rate limiting
        
        return results


# Глобальный экземпляр
bulk_loader = WikipediaBulkLoader()


async def load_all_writers_from_wikipedia() -> Dict[str, List[Dict]]:
    """Загрузить всех писателей из Wikipedia"""
    print("🌐 Загрузка писателей из Wikipedia...")
    
    categories = await bulk_loader.load_major_categories()
    all_writer_details = {}
    
    for category, writers in categories.items():
        print(f"📚 Загрузка {len(writers)} писателей из {category}...")
        details = await bulk_loader.populate_writer_details(writers)
        all_writer_details[category] = details
        print(f"   ✓ Загружено {len(details)} писателей")
    
    return all_writer_details


def export_to_json(writers_data: Dict) -> str:
    """Экспортировать в JSON"""
    file_path = "writers_from_wikipedia.json"
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(writers_data, f, ensure_ascii=False, indent=2)
        return file_path
    except:
        return None
