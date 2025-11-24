"""
ШАГ 3-4: Writer Search - Поиск и определение писателей
Функциональность поиска, фильтрации и автоматического определения
"""
import re
from typing import List, Dict, Optional, Tuple
from difflib import SequenceMatcher
from comprehensive_knowledge import knowledge


class WriterSearchEngine:
    """Поисковой движок для писателей"""
    
    def __init__(self):
        self.writers = knowledge.writers_db
        self.name_cache = {}
        self.key_cache = {}
        self._build_name_index()
    
    def _build_name_index(self):
        """Построить индекс имён для быстрого поиска"""
        for key, data in self.writers.items():
            name = data.get('name', '')
            
            # Сохранить по ключу
            self.key_cache[key] = key
            
            # Сохранить полное имя в нижнем регистре
            name_lower = name.lower()
            self.name_cache[name_lower] = key
            
            # Сохранить части имени (фамилия, имя)
            parts = name.lower().split()
            for part in parts:
                if len(part) > 2 and part not in self.name_cache:
                    self.name_cache[part] = key
    
    def search_by_name(self, query: str) -> Optional[str]:
        """ШАГ 4: Определить писателя по имени"""
        if not query:
            return None
        
        query = query.lower().strip()
        
        # Точное совпадение в кэше по ключу
        if query in self.key_cache:
            return self.key_cache[query]
        
        # Точное совпадение в кэше по имени
        if query in self.name_cache:
            return self.name_cache[query]
        
        # Поиск с использованием SequenceMatcher
        best_match = None
        best_score = 0.5
        
        for cached_name, key in self.name_cache.items():
            # Если query содержит часть имени или наоборот
            if query in cached_name or cached_name in query:
                score = SequenceMatcher(None, query, cached_name).ratio()
                if score > best_score:
                    best_score = score
                    best_match = key
        
        return best_match
    
    def search_by_works(self, work_title: str) -> List[Tuple[str, str]]:
        """Найти писателей по названию произведения"""
        results = []
        work_query = work_title.lower().strip()
        
        for key, writer in self.writers.items():
            works = writer.get('key_works', [])
            for work in works:
                if work_query in work.lower() or work.lower() in work_query:
                    results.append((key, writer.get('name', '')))
        
        return results
    
    def search_by_era(self, era_years: Tuple[int, int]) -> List[Tuple[str, str]]:
        """Найти писателей по эпохе"""
        start_year, end_year = era_years
        results = []
        
        for key, writer in self.writers.items():
            dates_str = writer.get('dates', '')
            
            # Попытаться парсить годы
            years = re.findall(r'\d{4}', dates_str)
            if years:
                birth_year = int(years[0])
                if start_year <= birth_year <= end_year:
                    results.append((key, writer.get('name', '')))
        
        return results
    
    def search_by_country(self, country: str) -> List[Tuple[str, str]]:
        """Найти писателей по стране"""
        results = []
        country_query = country.lower().strip()
        
        country_map = {
            'russia': ['пушкин', 'достоевский', 'толстой', 'чехов', 'гоголь', 'лермонтов', 'тургенев'],
            'england': ['shakespeare', 'austen', 'dickens', 'bronte', 'joyce'],
            'france': ['balzac', 'flaubert', 'proust', 'hugo', 'stendhal'],
            'usa': ['melville', 'twain', 'fitzgerald', 'hawthorne', 'poe'],
            'germany': ['kafka', 'mann', 'hesse', 'goethe'],
            'italy': ['dante', 'calvino'],
            'spain': ['cervantes', 'garcia lorca', 'lope de vega'],
        }
        
        keywords = country_map.get(country_query, [])
        
        for key, writer in self.writers.items():
            name_lower = writer.get('name', '').lower()
            if any(keyword in name_lower for keyword in keywords):
                results.append((key, writer.get('name', '')))
        
        return results
    
    def advanced_search(self, filters: Dict) -> List[Tuple[str, str]]:
        """Расширенный поиск с множественными фильтрами"""
        results = []
        
        for key, writer in self.writers.items():
            match = True
            
            # Фильтр по имени
            if 'name' in filters:
                name_filter = filters['name'].lower()
                if name_filter not in writer.get('name', '').lower():
                    match = False
            
            # Фильтр по эпохе
            if 'era' in filters and match:
                start, end = filters['era']
                dates_str = writer.get('dates', '')
                years = re.findall(r'\d{4}', dates_str)
                if years:
                    birth_year = int(years[0])
                    if not (start <= birth_year <= end):
                        match = False
            
            if match:
                results.append((key, writer.get('name', '')))
        
        return results
    
    def get_suggestions(self, partial_name: str, limit: int = 5) -> List[str]:
        """Получить подсказки по неполному имени"""
        suggestions = []
        partial_lower = partial_name.lower().strip()
        
        unique_writers = set()
        
        for name, key in self.name_cache.items():
            if name.startswith(partial_lower) or partial_lower in name:
                writer_name = self.writers[key].get('name', '')
                if writer_name not in unique_writers:
                    unique_writers.add(writer_name)
                    suggestions.append(writer_name)
        
        return suggestions[:limit]
    
    def get_similar_writers(self, writer_key: str, limit: int = 5) -> List[Tuple[str, str]]:
        """Получить похожих писателей"""
        if writer_key not in self.writers:
            return []
        
        current_writer = self.writers[writer_key]
        current_dates = current_writer.get('dates', '')
        
        # Найти писателей из того же периода
        years = re.findall(r'\d{4}', current_dates)
        if not years:
            return []
        
        birth_year = int(years[0])
        similar = []
        
        for key, writer in self.writers.items():
            if key == writer_key:
                continue
            
            dates_str = writer.get('dates', '')
            writer_years = re.findall(r'\d{4}', dates_str)
            
            if writer_years:
                writer_birth = int(writer_years[0])
                # Писатели из того же столетия
                if birth_year // 100 == writer_birth // 100:
                    similar.append((key, writer.get('name', '')))
        
        return similar[:limit]


# Глобальный экземпляр
search_engine = WriterSearchEngine()
