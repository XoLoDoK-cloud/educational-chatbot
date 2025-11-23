import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re
from concurrent.futures import ThreadPoolExecutor
class InternetSearcher:
    def __init__(self):
        self.session = None
    
    async def search_online(self, query, max_results=3):
        """Поиск информации в интернете при незнании ответа"""
        try:
            print(f"🔍 Бот не знает ответ, ищу в интернете: {query}")
            
            from googlesearch import search
            
            results = []
            # Ищем в Google в отдельном потоке с таймаутом
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                try:
                    search_results = await asyncio.wait_for(
                        loop.run_in_executor(
                            executor,
                            lambda: list(search(query, num_results=max_results, lang="ru"))
                        ),
                        timeout=10.0  # Таймаут 10 секунд для поиска
                    )
                except asyncio.TimeoutError:
                    print("⏰ Таймаут поиска в Google")
                    return []

            async with aiohttp.ClientSession() as session:
                tasks = []
                for url in search_results[:max_results]:
                    tasks.append(self.fetch_page_content(session, url))
                
                # Добавляем таймаут для загрузки страниц
                try:
                    pages_content = await asyncio.wait_for(
                        asyncio.gather(*tasks, return_exceptions=True),
                        timeout=15.0  # Таймаут 15 секунд для загрузки страниц
                    )
                except asyncio.TimeoutError:
                    print("⏰ Таймаут загрузки страниц")
                    return []
                
                for url, content in zip(search_results, pages_content):
                    if content and not isinstance(content, Exception):
                        results.append({
                            'url': url,
                            'content': self.clean_content(content)[:300]
                        })
            
            print(f"✅ Найдено результатов: {len(results)}")
            return results
            
        except Exception as e:
            print(f"❌ Ошибка поиска: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def fetch_page_content(self, session, url):
        """Получает содержимое страницы"""
        try:
            timeout = aiohttp.ClientTimeout(total=8)
            async with session.get(url, timeout=timeout) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Удаляем скрипты и стили
                    for script in soup(["script", "style"]):
                        script.decompose()
                    
                    text = soup.get_text()
                    return text
                return None
        except Exception as e:
            print(f"⚠️ Ошибка загрузки {url}: {e}")
            return None
    
    def clean_content(self, text):
        """Очищает текст"""
        if not text:
            return ""
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def should_search_internet(self, ai_response, user_question):
        """Определяет, нужно ли искать в интернете"""
        question_lower = user_question.lower().strip()
        
        # Исключаем общие фразы и приветствия
        common_phrases = [
            "привет", "здравствуй", "добрый день", "добрый вечер", "доброе утро",
            "как дела", "как ты", "как у тебя", "что делаешь", "чем занимаешься",
            "расскажи о себе", "кто ты", "что ты умеешь", "помоги", "спасибо", "пока"
        ]
        
        # Если это общая фраза - НЕ ищем в интернете
        if any(phrase in question_lower for phrase in common_phrases):
            return False
        
        # Ключевые слова для КОНКРЕТНЫХ фактологических вопросов
        factual_keywords = [
            "когда родился", "когда умер", "когда написал", "в каком году",
            "где родился", "где умер", "где написал",
            "что такое", "кто такой", "кто такая",
            "какое первое произведение", "какое последнее произведение",
            "первое произведение", "последнее произведение",
            "сколько произведений", "сколько книг",
            "дата рождения", "дата смерти", "биография",
            "какой роман", "какая книга", "какое стихотворение"
        ]
        
        # Проверяем ТОЛЬКО конкретные фактологические вопросы
        is_factual_question = any(keyword in question_lower for keyword in factual_keywords)
        
        # Ищем ТОЛЬКО если это явный фактологический вопрос
        return is_factual_question

    def generate_internet_answer(self, query, search_results, author_style):
        """Генирирует ответ на основе найденной в интернете информации"""
        if not search_results:
            return "К сожалению, не удалось найти информацию по вашему запросу в интернете."
        
        # Формируем ответ в стиле автора с интернет-данными
        if author_style == "пушкин":
            intro = f"О, мой дорогой собеседник! Касательно '{query}', позвольте мне поделиться найденными сведениями из современных источников:"
        elif author_style == "достоевский":
            intro = f"Милый мой, ваш вопрос о '{query}' заставил обратиться к нынешним знаниям человечества:"
        elif author_style == "толстой":
            intro = f"Дорогой собеседник, относительно '{query}', современная наука сообщает следующее:"
        elif author_style == "чехов":
            intro = f"Знаете, ваш вопрос о '{query}' довольно интересен. Вот что удалось найти в современных источниках:"
        else:  # гоголь
            intro = f"Ах, какой любопытный вопрос о '{query}'! Позвольте мне рассказать, что говорят об этом ныне:"
        
        # Добавляем основную информацию из интернета
        main_content = []
        for i, result in enumerate(search_results[:2], 1):
            snippet = result['content']
            if len(snippet) > 150:
                snippet = snippet[:147] + "..."
            main_content.append(f"\n{snippet}")
        
        # Добавляем примечание об источниках
        sources_note = "\n\n*Информация получена из открытых интернет-источников*"
        
        return intro + "".join(main_content) + sources_note

# Глобальный экземпляр
internet_searcher = InternetSearcher()
