import os
import asyncio
import aiohttp
import random
import re

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
            
            # Для остальных вопросов - используем интернет через Perplexity
            print(f"🌐 Используется Perplexity для поиска в интернете")
            return await self._call_perplexity(message, author_data)
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            # Fallback на цитату при ошибке
            if 'greetings' in author_data and author_data['greetings']:
                return random.choice(author_data['greetings'])
            return f"{author_data['name']} размышляет над вашим вопросом..."
    
    async def _call_perplexity(self, message, author_data):
        """Вызывает Perplexity с интернет-поиском"""
        try:
            model = "perplexity/llama-3.1-sonar-small-128k-online"
            
            system_prompt = f"""Ты - {author_data['name']}, русский классический писатель.
Стиль: {author_data.get('style', 'изящный и выразительный')}
Личность: {author_data.get('personality', 'глубокая и рефлексивная')}

Инструкции:
1. Отвечай ТОЛЬКО в стиле этого писателя
2. Используй интернет для поиска свежей и точной информации
3. Ответ должен быть коротким (1-3 предложения)
4. Генерируй авторский ответ в его стилистике
5. Используй характерные для писателя выражения
6. Говори от первого лица как сам писатель"""
            
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                "max_tokens": 300,
                "temperature": 0.9
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "LiteraryBot/1.0"
            }
            
            print(f"🔄 Запрос Perplexity для: {message[:50]}...")
            
            if not self.api_key:
                print("⚠️ API ключ не найден!")
                return "Извините, бот не настроен правильно."
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.url, 
                    json=payload, 
                    headers=headers, 
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        response = data['choices'][0]['message']['content'].strip()
                        print(f"✅ Perplexity ответ получен: {len(response)} символов")
                        return response
                    else:
                        error_text = await resp.text()
                        print(f"⚠️ OpenRouter API ошибка {resp.status}")
                        return self._generate_fallback_response(author_data, message)
                        
        except asyncio.TimeoutError:
            print("⏰ Таймаут Perplexity")
            return self._generate_fallback_response(author_data, message)
        except Exception as e:
            print(f"❌ Ошибка Perplexity: {e}")
            return self._generate_fallback_response(author_data, message)
    
    def _generate_fallback_response(self, author_data, message):
        """Простой fallback ответ при ошибке API"""
        writer_name = author_data['name']
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
