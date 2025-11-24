"""
Fallback механизм для работы бота без Wikipedia
Использует локальную базу данных писателей
"""
from typing import Dict, List, Optional
from comprehensive_knowledge import knowledge


class WikipediaFallback:
    """Резервный механизм когда Wikipedia недоступна"""
    
    def __init__(self):
        self.local_writers = self._load_local_writers()
    
    def _load_local_writers(self) -> Dict[str, Dict]:
        """Загрузить всех писателей из локальной базы"""
        all_writers = {}
        
        # Получить всех писателей из comprehensive_knowledge
        for writer_key, writer_data in knowledge.writers_db.items():
            if writer_data:
                all_writers[writer_key] = {
                    'key': writer_key,
                    'name': writer_data.get('name', ''),
                    'dates': writer_data.get('dates', ''),
                    'bio': writer_data.get('about', '')[:500],
                    'works': writer_data.get('key_works', [])[:5],
                }
        
        return all_writers
    
    def search_writers(self, query: str = '') -> List[Dict]:
        """Поиск писателей в локальной базе"""
        if not query:
            return list(self.local_writers.values())
        
        query_lower = query.lower()
        results = []
        
        for writer in self.local_writers.values():
            name_lower = writer['name'].lower()
            if query_lower in name_lower or name_lower in query_lower:
                results.append(writer)
        
        return results
    
    def get_writer(self, writer_key: str) -> Optional[Dict]:
        """Получить писателя"""
        return self.local_writers.get(writer_key)
    
    def get_all_writers_by_category(self, category: str = 'all') -> List[Dict]:
        """Получить писателей по категориям"""
        # Симуляция категорий из локальной БД
        if category == 'all':
            return list(self.local_writers.values())
        
        # Можно добавить реальные категории если нужно
        return list(self.local_writers.values())


fallback = WikipediaFallback()


def get_writer_from_wikipedia_or_local(writer_name: str) -> Optional[Dict]:
    """Получить писателя из Wikipedia или из локальной БД"""
    # Сначала ищем в локальной БД
    results = fallback.search_writers(writer_name)
    if results:
        return results[0]
    
    return None


def ensure_writer_in_fallback(writer_key: str) -> Dict:
    """Убедиться, что писатель есть в fallback"""
    writer = fallback.get_writer(writer_key)
    if not writer:
        writer_data = knowledge.writers_db.get(writer_key)
        if writer_data:
            writer = {
                'key': writer_key,
                'name': writer_data.get('name', ''),
                'dates': writer_data.get('dates', ''),
                'bio': writer_data.get('about', '')[:500],
                'works': writer_data.get('key_works', [])[:5],
            }
            fallback.local_writers[writer_key] = writer
    
    return writer or {}
