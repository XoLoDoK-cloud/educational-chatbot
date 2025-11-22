import os
import aiohttp
import random
import re

class MegaAI:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.url = "https://openrouter.ai/api/v1/chat/completions"
    
    async def generate_literary_response(self, message, author_data):
        """Генерирует ответ в стиле автора"""
        try:
            # Используем локальные ответы как fallback
            response = self._get_mega_response(author_data['name'].lower(), message)
            return response
        except Exception as e:
            return f"Извините, произошла ошибка: {str(e)}"
    
    def _get_mega_response(self, writer, user_message):
        """МЕГА-КАЧЕСТВЕННЫЕ ОТВЕТЫ С ОГРОМНЫМИ ТЕКСТАМИ"""
        user_lower = user_message.lower()
        
        # Анализируем тип сообщения для идеального ответа
        if any(word in user_lower for word in ["привет", "здравств", "добрый", "хай", "hello", "hi", "начать", "start"]):
            return self._get_mega_greeting(writer)
        elif any(word in user_lower for word in ["как дела", "как жизнь", "настроен", "самочувств"]):
            return self._get_mega_mood(writer)
        elif any(word in user_lower for word in ["что думаешь", "твое мнение", "считаешь", "точка зрения"]):
            return self._get_mega_opinion(writer, user_lower)
        elif any(word in user_lower for word in ["расскажи", "опиши", "поделись", "истори"]):
            return self._get_mega_story(writer, user_lower)
        elif any(word in user_lower for word in ["любов", "чувств", "сердце", "роман"]):
            return self._get_mega_love(writer)
        elif any(word in user_lower for word in ["творчеств", "писать", "стих", "поэз", "книг", "вдохновен"]):
            return self._get_mega_creative(writer)
        elif any(word in user_lower for word in ["жизн", "смысл", "смерт", "бог", "душ", "вер", "философ"]):
            return self._get_mega_philosophy(writer)
        elif any(word in user_lower for word in ["пока", "до свидан", "прощай", "бывай", "спокойной"]):
            return self._get_mega_farewell(writer)
        elif any(word in user_lower for word in ["техн", "компьютер", "интернет", "смартфон", "робот"]):
            return self._get_mega_technology(writer)
        elif any(word in user_lower for word in ["природ", "погод", "весн", "лет", "осен", "зим"]):
            return self._get_mega_nature(writer)
        elif any(word in user_lower for word in ["искусств", "музык", "живоп", "театр", "кино"]):
            return self._get_mega_art(writer)
        else:
            return self._get_mega_deep(writer, user_lower)
    
    def _get_mega_greeting(self, writer):
        """ОГРОМНЫЕ ПРИВЕТСТВЕННЫЕ ОТВЕТЫ"""
        responses = {
            "пушкин": """
О, приветствую вас, мой дорогой собеседник! Рад нашей беседе.
""",
            "достоевский": """
Здравствуйте... Каждая новая встреча для меня - это возможность заглянуть в глубины человеческой души.
""",
            "толстой": """
Здравствуйте, друг мой. Искренняя беседа становится настоящей драгоценностью в наш век скоростей.
""",
            "чехов": """
Здравствуйте. Хорошая, умная беседа всегда напоминала мне искусно написанное литературное произведение.
""",
            "гоголь": """
А, здравствуйте, голубчик! Какая неожиданная, но чрезвычайно приятная встреча!
"""
        }
        return responses.get(writer, "Здравствуйте! Рад возможности содержательного диалога.")
    
    def _get_mega_mood(self, writer):
        """ОГРОМНЫЕ ОТВЕТЫ О НАСТРОЕНИИ"""
        responses = {
            "пушкин": """
Душа поэта подобна изменчивому морю - то спокойна, то взволнована бурями творческих исканий.
""",
            "достоевский": """
Настроение... Какая сложная, многогранная материя человеческой психики.
""",
            "толстой": """
Когда человек живёт в согласии с собственной совестью, плохого настроения просто не может быть.
""",
            "чехов": """
Настроение... Оно переменчиво как весенняя погода в нашем российском климате.
""",
            "гоголь": """
Ох, настроение! Эта удивительная способность человеческой души взлетать до небес!
"""
        }
        return responses.get(writer, "Нахожусь в состоянии творческого равновесия.")
    
    # ... (добавьте остальные методы из вашего оригинального кода)
    
    def _get_mega_opinion(self, writer, question):
        return "Мое мнение по этому вопросу..."
    
    def _get_mega_story(self, writer, question):
        return "Интересная история..."
    
    def _get_mega_love(self, writer):
        return "Размышления о любви..."
    
    def _get_mega_creative(self, writer):
        return "О творчестве..."
    
    def _get_mega_philosophy(self, writer):
        return "Философские размышления..."
    
    def _get_mega_farewell(self, writer):
        return "До свидания! Было приятно беседовать."
    
    def _get_mega_technology(self, writer):
        return "О технологиях..."
    
    def _get_mega_nature(self, writer):
        return "О природе..."
    
    def _get_mega_art(self, writer):
        return "Об искусстве..."
    
    def _get_mega_deep(self, writer, question):
        return "Глубокий ответ на ваш вопрос..."

# Создаем экземпляр класса
mega_ai = MegaAI()

# Экспортируемая функция - ДОЛЖНА БЫТЬ В КОНЦЕ ФАЙЛА
async def generate_literary_response(message, author_data):
    """Функция для импорта в bot.py"""
    return await mega_ai.generate_literary_response(message, author_data)
