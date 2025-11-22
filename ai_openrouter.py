import os
import aiohttp

class OpenRouterAI:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.url = "https://openrouter.ai/api/v1/chat/completions"
    
    async def generate_response(self, writer, user_message):
        if not self.api_key:
            return "🎭 Настройки ИИ не завершены."
        
        context = self._get_writer_context(writer)
        
        prompt = {
            "model": "google/gemma-7b-it:free",
            "messages": [
                {
                    "role": "system",
                    "text": f"Ты - {writer}. {context} Отвечай только в стиле этого писателя."
                },
                {
                    "role": "user",
                    "text": user_message
                }
            ],
            "max_tokens": 150
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://t.me/literarybot",
            "X-Title": "Literary Bot"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.url, json=prompt, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result['choices'][0]['message']['content']
                    return f"🎭 {writer.title()}: Не могу сейчас ответить."
        except:
            return f"🎭 {writer.title()}: Продолжим беседу позже."

    def _get_writer_context(self, writer):
        contexts = {
            "пушкин": "Ты Пушкин - говоришь романтично и элегантно",
            "достоевский": "Ты Достоевский - глубокий философ", 
            "толстой": "Ты Толстой - мудрый и простой",
            "чехов": "Ты Чехов - ироничный и лаконичный",
            "гоголь": "Ты Гоголь - мистический и с юмором"
        }
        return contexts.get(writer, "Русский писатель")

openrouter_ai = OpenRouterAI()
