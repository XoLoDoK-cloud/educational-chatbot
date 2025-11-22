import os
import aiohttp
import random

class OpenRouterAI:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        
        # Список рабочих бесплатных моделей для перебора
        self.free_models = [
            "microsoft/dialo-medium:free",           # Microsoft
            "huggingfaceh4/zephyr-7b-beta:free",     # Hugging Face Zephyr
            "google/gemma-7b-it:free",               # Google Gemma
            "meta-llama/llama-3.1-8b-instruct:free", # Meta Llama
            "openai/gpt-oss-20b:free"                # OpenAI OSS
        ]
    
    async def generate_response(self, writer, user_message):
        if not self.api_key:
            return self._get_fallback_response(writer)
        
        # Пробуем все модели по очереди
        for model in self.free_models:
            response = await self._try_model(model, writer, user_message)
            if response and "не могу" not in response.lower():
                return response
        
        # Если все модели не сработали - возвращаем запасной ответ
        return self._get_fallback_response(writer)
    
    async def _try_model(self, model, writer, user_message):
        context = self._get_writer_context(writer)
        
        prompt = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": f"""Ты - {writer}. {context}

ОТВЕЧАЙ ТОЛЬКО В СТИЛЕ ЭТОГО ПИСАТЕЛЯ!
Не говори что ты ИИ, нейросеть или модель.
Отвечай естественно, как настоящий писатель."""
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            "temperature": 0.7,
            "max_tokens": 120
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://t.me/literarycompanionbot",
            "X-Title": "Literary Bot"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.url, json=prompt, headers=headers, timeout=10) as response:
                    if response.status == 200:
                        result = await response.json()
                        ai_response = result['choices'][0]['message']['content']
                        
                        # Проверяем что ответ адекватный
                        if len(ai_response.strip()) > 10 and "ошибка" not in ai_response.lower():
                            print(f"✅ Модель {model} сработала!")
                            return ai_response
                    
                    print(f"❌ Модель {model} не сработала (статус: {response.status})")
                    return None
                    
        except Exception as e:
            print(f"❌ Ошибка с моделью {model}: {e}")
            return None
    
    def _get_fallback_response(self, writer):
        """Запасные стилизованные ответы если ИИ не работает"""
        responses = {
            "пушкин": [
                "О, приветствую вас, мой друг! Душа поэта полна вдохновения в этот прекрасный день. О чём изволите побеседовать?",
                "Как денди лондонский одетый, явился я к вам на беседу! Что тревожит вашу душу, мой друг?",
                "Любви, надежды, тихой славы - вот о чём готов беседовать с вами! Расскажите, что лежит на сердце?"
            ],
            "достоевский": [
                "Здравствуйте... Мне кажется, в каждом из нас есть бездна, которую стоит исследовать. Что вы думаете об этом?",
                "Страдание... оно очищает душу, не правда ли? Готов обсудить самые сокровенные вопросы бытия.",
                "Человек - это тайна. Её нужно разгадывать всю жизнь. О чём хотели бы поговорить?"
            ],
            "толстой": [
                "Здравствуйте, друг мой. Всякая мысль, выраженная словами, есть великая сила. О чём побеседуем?",
                "Простота есть необходимое условие прекрасного. Давайте поговорим о жизни, о вере, о нравственности.",
                "Счастье не в том, чтобы делать всегда, что хочешь, а в том, чтобы всегда хотеть того, что делаешь."
            ],
            "чехов": [
                "Здравствуйте! Краткость - сестра таланта, но для хорошей беседы сделаю исключение. О чём поговорим?",
                "В человеке должно быть всё прекрасно: и лицо, и одежда, и душа, и мысли. Что вас волнует?",
                "Жизнь - это миг, искусство - вечно. Чему посвятим этот миг нашей беседы?"
            ],
            "гоголь": [
                "А, здравствуйте! Как поживают ваши души? Готов поговорить о самом загадочном и необъяснимом!",
                "Ох, жизнь-то какая сложная штука! То смешно, то страшно, то вовсе непонятно! Что на уме?",
                "Весь мир - это театр, а люди в нём актёры. Какую пьесу разыгрываем сегодня в нашей беседе?"
            ]
        }
        
        writer_responses = responses.get(writer, ["Готов к беседе! О чём хотели бы поговорить?"])
        return random.choice(writer_responses)
    
    def _get_writer_context(self, writer):
        contexts = {
            "пушкин": "Ты Александр Пушкин - великий русский поэт, говоришь элегантно и романтично.",
            "достоевский": "Ты Фёдор Достоевский - глубокий философ, исследующий душу человека.", 
            "толстой": "Ты Лев Толстой - мудрец, говорящий просто о сложном.",
            "чехов": "Ты Антон Чехов - мастер иронии и лаконичности.",
            "гоголь": "Ты Николай Гоголь - мистик с чувством юмора."
        }
        return contexts.get(writer, "Русский писатель")

openrouter_ai = OpenRouterAI()
