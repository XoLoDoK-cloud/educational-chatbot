import os
import asyncio
import aiohttp
import random
import re
from neural_writer import neural_ai
from internet_search import internet_searcher

class MegaAI:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        if self.api_key:
            key_preview = self.api_key[:10] + "..." + self.api_key[-5:]
            print(f"✅ OpenRouter API ключ загружен: {key_preview}")
        else:
            print("❌ OpenRouter API ключ НЕ найден!")
    
    def _is_greeting(self, message):
        """Проверяет, является ли сообщение приветствием"""
        greetings_keywords = [
            "привет", "здравствуй", "здравствуйте", "добрый",
            "добрых", "с добрым", "хай", "hello", "hi", "hey",
            "начать", "start", "привет", "салют", "дарова"
        ]
        message_lower = message.lower().strip()
        
        # Проверяем точное совпадение или короткое сообщение с приветствием
        if len(message_lower) < 50:  # Приветствие обычно короткое
            for keyword in greetings_keywords:
                if keyword in message_lower:
                    return True
        
        return False
    
    async def generate_literary_response(self, message, author_data, internet_context=None):
        """Генирирует ответ в стиле автора"""
        try:
            # Проверяем, является ли это приветствием
            if self._is_greeting(message):
                print(f"🎭 Приветствие обнаружено, отправляем цитату")
                if 'greetings' in author_data and author_data['greetings']:
                    quote = random.choice(author_data['greetings'])
                    print(f"✅ Цитата выбрана: {quote[:60]}...")
                    return quote
            
            # Получаем имя писателя для нейросети
            writer_name = author_data['name'].lower()
            # Создаём ключ для поиска в словаре нейросети
            writer_keys = {
                "александр пушкин": "пушкин",
                "фёдор достоевский": "достоевский",
                "лев толстой": "толстой",
                "антон чехов": "чехов",
                "николай гоголь": "гоголь"
            }
            
            neural_writer_key = writer_keys.get(writer_name, "пушкин")
            
            # Проверяем, нужен ли интернет-поиск (для фактологических вопросов)
            should_search = internet_searcher.should_search_internet("", message)
            
            if should_search:
                print(f"🔍 Фактологический вопрос обнаружен, ищу в интернете")
                # Пытаемся найти информацию в интернете
                search_results = await internet_searcher.search_online(message, max_results=3)
                
                if search_results:
                    print(f"✅ Найдено {len(search_results)} результатов в интернете")
                    # Генерируем ответ на основе найденной информации
                    response = internet_searcher.generate_internet_answer(
                        message, 
                        search_results, 
                        neural_writer_key
                    )
                    return response
            
            # Если интернет не нужен или не найдено - используем встроенную нейросеть
            print(f"🧠 Используется встроенная нейросеть для ответа")
            response = neural_ai.generate_response(neural_writer_key, message)
            
            if not response or len(response.strip()) == 0:
                response = self._generate_fallback_response(author_data, message)
            
            return response
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            # Fallback на встроенную нейросеть при ошибке
            return neural_ai.generate_response(neural_writer_key, message)
    
    def _generate_fallback_response(self, author_data, message):
        """Простой fallback ответ при ошибке"""
        writer_name = author_data['name']
        message_lower = message.lower()
        
        # Проверяем, есть ли вопрос о первом произведении
        if any(word in message_lower for word in ["первое произведение", "первая работа", "начало творчества", "первый роман"]):
            if 'first_work' in author_data:
                first_work = author_data['first_work']
                year = author_data.get('first_work_year', '')
                year_str = f" в {year} году" if year else ""
                return f"Моё первое произведение - '{first_work}'{year_str}. Оно открыло для меня путь к литературному успеху."
        
        responses = {
            "pushkin": f"О, какой интересный вопрос! {writer_name} обдумывает это с поэтической грацией.",
            "dostoevsky": f"Это глубокий вопрос... {writer_name} видит в нём отражение человеческой природы.",
            "tolstoy": f"Интересное наблюдение. {writer_name} ищет в этом истину и смысл жизни.",
            "chekhov": f"Знаете, в жизни часто встречается именно это. {writer_name} видит здесь суть человеческого.",
            "gogol": f"О, какой забавный и одновременно глубокий вопрос! {writer_name} готов развернуть перед вами целую историю."
        }
        
        for key in responses.keys():
            if key in writer_name.lower():
                return responses[key]
        
        return f"{writer_name} размышляет над вашим вопросом..."


# Создаём глобальный экземпляр
mega_ai = MegaAI()

async def generate_literary_response(message, author_data, internet_context=None):
    """Публичная функция для генерации ответа"""
    return await mega_ai.generate_literary_response(message, author_data, internet_context)
