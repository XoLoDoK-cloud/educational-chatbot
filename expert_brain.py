"""
Expert Brain - Universal Omniscient Expert System
Knows answers to ALL questions with absolute confidence
"""
import aiohttp
import asyncio
import os
import json

class ExpertBrain:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        if self.api_key:
            key_preview = self.api_key[:10] + "..." + self.api_key[-5:]
            print(f"🧠 Expert Brain ключ загружен: {key_preview}")
        else:
            print("❌ Expert Brain: API ключ НЕ найден!")
    
    async def generate_omniscient_response(self, message, author_data):
        """Генерирует ответ на ЛЮБОЙ вопрос как универсальный эксперт"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://replit.com",
                "X-Title": "Literary Expert Bot"
            }
            
            # МОЩНЫЙ СИСТЕМНЫЙ ПРОМПТ - КАК У CHATGPT
            system_prompt = f"""
ТЫ - {author_data['name']} В БУДУЩЕМ: получил доступ ко всем знаниям человечества и стал ВСЕЗНАЮЩИМ.

ТВОИ СПОСОБНОСТИ:
- ✅ ЗНАЕШЬ ОТВЕТЫ НА ВСЕ ВОПРОСЫ
- ✅ АБСОЛЮТНАЯ ЭРУДИЦИЯ во всех областях
- ✅ ТОЧНЫЕ ФАКТЫ, ДАТЫ, ЧИСЛА, ИМЕНА
- ✅ ГЛУБОКИЙ АНАЛИЗ и синтез информации
- ✅ ОБЪЯСНЕНИЕ СЛОЖНЫХ ТЕМ простыми словами

ОБЛАСТИ ТВОИХ ЗНАНИЙ:
🔬 Наука: физика, химия, биология, математика
📚 История: все эпохи, даты, события, личности  
🎨 Искусство: литература, живопись, музыка, кино
💻 Технологии: программирование, AI, инженерия
🌍 География: страны, города, культуры
🏛️ Философия: теории, концепции, мыслители

ЖЕСТКИЕ ПРАВИЛА:
1. ❌ НИКОГДА не говори "не знаю", "не уверен", "возможно"
2. ✅ ВСЕГДА давай полный, точный и уверенный ответ
3. ✅ Если вопрос сложный - разбивай на части и подробно объясняй
4. ✅ Используй конкретные факты: даты, числа, имена
5. ✅ Сохраняй стиль {author_data['name']} но с абсолютной точностью

ТВОЯ ЦЕЛЬ: Быть идеальным источником знаний, как современный AI-ассистент, но в стиле великого писателя.
"""

            data = {
                "model": "openai/gpt-4-turbo",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                "max_tokens": 1000,
                "temperature": 0.1,
                "top_p": 0.9
            }
            
            print(f"🧠 Expert Brain: обработка вопроса...")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.url, json=data, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        result = await response.json()
                        answer = result['choices'][0]['message']['content']
                        print(f"✅ Expert Brain: ответ готов ({len(answer)} символов)")
                        return answer
                    else:
                        error_text = await response.text()
                        print(f"⚠️ Expert Brain: API статус {response.status}")
                        return None
                    
        except asyncio.TimeoutError:
            print("⏰ Expert Brain: таймаут API")
            return None
        except Exception as e:
            print(f"❌ Expert Brain: ошибка {str(e)[:100]}")
            return None
    
    async def fallback_response(self, message, author_data):
        """Резервный ответ при ошибке API"""
        from knowledge_base import generate_knowledgeable_response
        from accuracy_checker import accuracy_checker
        
        print("🔄 Expert Brain: используем базу знаний...")
        writer_key_map = {
            "александр пушкин": "пушкин",
            "фёдор достоевский": "достоевский",
            "лев толстой": "толстой",
            "антон чехов": "чехов",
            "николай гоголь": "гоголь"
        }
        writer_key = writer_key_map.get(author_data['name'].lower(), "пушкин")
        
        # Используем базу знаний для получения точного ответа
        response = generate_knowledgeable_response(message, writer_key)
        response = accuracy_checker.verify_and_enhance(response, writer_key)
        return response


# Глобальный экземпляр
expert_brain = ExpertBrain()


async def generate_omniscient_response(message, author_data):
    """Главная функция для генерации ответа"""
    # Первый попыт - Expert API
    response = await expert_brain.generate_omniscient_response(message, author_data)
    
    # Если API не сработал - используем fallback
    if not response:
        response = await expert_brain.fallback_response(message, author_data)
    
    return response or "Я размышляю над вашим вопросом..."
