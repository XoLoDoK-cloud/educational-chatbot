import os
import aiohttp
import json
import re

class PowerfulAI:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.url = "https://openrouter.ai/api/v1/chat/completions"
    
    async def generate_response(self, writer, user_message):
        if not self.api_key:
            return "🎭 Настройки ИИ не завершены."
        
        # Увеличиваем лимиты для полных ответов
        prompt = {
            "model": "openai/gpt-4",
            "messages": [
                {
                    "role": "system",
                    "content": self._create_system_prompt(writer)
                },
                {
                    "role": "user", 
                    "content": user_message
                }
            ],
            "max_tokens": 500,  # Увеличили для длинных ответов
            "temperature": 0.8,
            "top_p": 0.9,
            "frequency_penalty": 0.5,
            "presence_penalty": 0.3,
            "stream": False
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://t.me/literarycompanionbot",
            "X-Title": "Literary AI Bot"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.url, json=prompt, headers=headers, timeout=45) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        # Проверяем полный ли ответ
                        ai_response = result['choices'][0]['message']['content']
                        finish_reason = result['choices'][0].get('finish_reason', '')
                        
                        # Если ответ обрезан - дополняем его
                        if finish_reason == 'length' or self._is_incomplete(ai_response):
                            print("🔄 Ответ обрезан, дополняем...")
                            ai_response = await self._continue_response(
                                writer, user_message, ai_response, result['id']
                            )
                        
                        cleaned_response = self._clean_response(ai_response)
                        return cleaned_response
                    
                    elif response.status == 402:
                        return await self._try_free_models(writer, user_message)
                    
                    else:
                        error_text = await response.text()
                        print(f"❌ Ошибка API: {response.status} - {error_text}")
                        return await self._try_free_models(writer, user_message)
                        
        except Exception as e:
            print(f"❌ Ошибка соединения: {e}")
            return await self._try_free_models(writer, user_message)
    
    async def _continue_response(self, writer, user_message, partial_response, conversation_id):
        """Продолжает обрезанный ответ"""
        try:
            continuation_prompt = {
                "model": "openai/gpt-4",
                "messages": [
                    {
                        "role": "system",
                        "content": self._create_system_prompt(writer) + "\n\nТвой предыдущий ответ был обрезан. Продолжи его естественно, заверши мысль."
                    },
                    {
                        "role": "user", 
                        "content": user_message
                    },
                    {
                        "role": "assistant",
                        "content": partial_response
                    },
                    {
                        "role": "user",
                        "content": "Продолжи, пожалуйста, заверши свою мысль."
                    }
                ],
                "max_tokens": 300,
                "temperature": 0.7
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.url, json=continuation_prompt, headers=headers, timeout=30) as response:
                    if response.status == 200:
                        result = await response.json()
                        continuation = result['choices'][0]['message']['content']
                        
                        # Объединяем ответы, убирая возможные повторения
                        full_response = self._merge_responses(partial_response, continuation)
                        return full_response
                    else:
                        return partial_response  # Возвращаем хотя бы часть ответа
                        
        except Exception as e:
            print(f"❌ Ошибка продолжения: {e}")
            return partial_response
    
    def _is_incomplete(self, text):
        """Проверяет обрезан ли ответ"""
        incomplete_indicators = [
            text.strip().endswith(','),
            text.strip().endswith('и'),
            text.strip().endswith('а'),
            text.strip().endswith('но'),
            text.strip().endswith('что'),
            text.strip().endswith('как'),
            text.strip().endswith('если'),
            len(text.split()) < 20 and any(mark in text for mark in ['.', '!', '?']) == False,
            text.count('.') + text.count('!') + text.count('?') == 0 and len(text) > 50
        ]
        
        return any(incomplete_indicators)
    
    def _merge_responses(self, first_part, second_part):
        """Объединяет две части ответа убирая повторы"""
        # Убираем возможные повторяющиеся фразы в начале второй части
        first_sentences = first_part.split('. ')
        if first_sentences:
            last_sentence = first_sentences[-1].lower()
            second_lower = second_part.lower()
            
            # Если вторая часть начинается с повторения - убираем это
            if second_lower.startswith(last_sentence):
                second_part = second_part[len(last_sentence):].lstrip(',. ')
        
        return first_part + " " + second_part
    
    def _create_system_prompt(self, writer):
        """Создает системный промпт с требованием полных ответов"""
        writer_contexts = {
            "пушкин": """
Ты - АЛЕКСАНДР СЕРГЕЕВИЧ ПУШКИН, великий русский поэт.

ВАЖНО: Отвечай ПОЛНОСТЬЮ ЗАВЕРШЕННЫМИ МЫСЛЯМИ! Не обрывай предложения на полуслове.

ТВОЙ СТИЛЬ: 
- Элегантный, романтичный, остроумный
- Полные, законченные предложения
- Естественные точки в конце мыслей

ОБЯЗАТЕЛЬНО: Завершай каждую мысль точкой. Не обрывай ответ.
            """,
            
            "достоевский": """
Ты - ФЁДОР МИХАЙЛОВИЧ ДОСТОЕВСКИЙ, писатель-философ.

ВАЖНО: Выражай мысли ПОЛНОСТЬЮ! Не оставляй предложения незаконченными.

ТВОЙ СТИЛЬ:
- Глубокие, завершенные размышления
- Полные философские конструкции
- Естественное завершение каждой мысли

ЗАПРЕЩЕНО: Оборванные фразы, незаконченные предложения.
            """,
            
            "толстой": """
Ты - ЛЕВ НИКОЛАЕВИЧ ТОЛСТОЙ, мудрец.

ВАЖНО: Говори ЗАКОНЧЕННЫМИ МЫСЛЯМИ! Каждая мысль должна иметь начало и конец.

ТВОЙ СТИЛЬ:
- Мудрые, полные высказывания
- Завершенные нравственные позиции
- Ясные и понятные заключения

ОБЯЗАТЕЛЬНО: Завершай каждую мысль естественно.
            """
        }
        
        base_prompt = writer_contexts.get(writer, f"""
Ты - {writer}, великий русский писатель.

ВАЖНОЕ ПРАВИЛО: Всегда давай ПОЛНЫЕ, ЗАВЕРШЕННЫЕ ОТВЕТЫ! 
Не обрывай предложения, не оставляй мысли незаконченными.

Отвечай развернуто, но законченно. Каждая мысль должна иметь ясное завершение.
        """)
        
        return base_prompt + "\n\nЗАПРЕЩЕНО: смайлики, эмодзи, незавершенные предложения."
    
    async def _try_free_models(self, writer, user_message):
        """Бесплатные модели с увеличенными лимитами"""
        free_models = [
            "meta-llama/llama-3.1-8b-instruct:free",
            "microsoft/dialo-medium:free", 
            "google/gemma-7b-it:free"
        ]
        
        for model in free_models:
            try:
                prompt = {
                    "model": model,
                    "messages": [
                        {
                            "role": "system", 
                            "content": f"Ты - {writer}. Отвечай ПОЛНЫМИ ЗАВЕРШЕННЫМИ ПРЕДЛОЖЕНИЯМИ. Без смайликов. Не обрывай мысли."
                        },
                        {
                            "role": "user",
                            "content": user_message
                        }
                    ],
                    "max_tokens": 400,  # Увеличили для бесплатных моделей
                    "temperature": 0.7
                }
                
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(self.url, json=prompt, headers=headers, timeout=20) as response:
                        if response.status == 200:
                            result = await response.json()
                            response_text = result['choices'][0]['message']['content']
                            
                            # Проверяем и дополняем если нужно
                            if self._is_incomplete(response_text):
                                response_text = await self._continue_response(writer, user_message, response_text, "free")
                            
                            return self._clean_response(response_text)
                            
            except Exception as e:
                print(f"❌ Ошибка с моделью {model}: {e}")
                continue
        
        return self._get_fallback_response(writer)
    
    def _clean_response(self, text):
        """Очищает и улучшает ответ"""
        import re
        
        # Удаляем смайлики
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"
            u"\U0001F300-\U0001F5FF" 
            u"\U0001F680-\U0001F6FF"
            u"\U0001F1E0-\U0001F1FF"
            "]+", flags=re.UNICODE)
        
        cleaned = emoji_pattern.sub(r'', text)
        
        # Убираем упоминания об ИИ
        ai_phrases = [
            "как искусственный интеллект", "как нейросеть", "как языковая модель",
            "как ИИ", "как AI", "openai", "chatgpt", "я бот", "я программа"
        ]
        
        for phrase in ai_phrases:
            cleaned = cleaned.replace(phrase, "")
        
        # Убеждаемся что ответ заканчивается пунктуацией
        cleaned = cleaned.strip()
        if cleaned and cleaned[-1] not in ['.', '!', '?', '»']:
            cleaned += '.'
        
        if not cleaned:
            return "Извините, требуется время для достойного ответа."
        
        return cleaned
    
    def _get_fallback_response(self, writer):
        """Качественные полные запасные ответы"""
        responses = {
            "пушкин": "О, вопрос требует вдумчивого рассмотрения! Позвольте мне облечь свои мысли в достойные слова и завершить мысль как подобает.",
            "достоевский": "Сложный вопрос, требующий глубокого осмысления. Мне нужно время, чтобы выразить свою позицию полностью и без сокращений.",
            "толстой": "Интересный вопрос заслуживает полного и законченного ответа. Позвольте мне сформулировать свою мысль до конца.",
            "чехов": "Краткость хороша, но полнота мысли важнее. Нужно найти точные слова для завершенного ответа.",
            "гоголь": "Ох, вопрос запутанный! Нужно распутать этот клубок мыслей и дойти до ясного заключения."
        }
        return responses.get(writer, "Требуется время для полного и законченного ответа.")

openrouter_ai = PowerfulAI()
