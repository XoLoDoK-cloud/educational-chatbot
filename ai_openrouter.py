import os
import aiohttp
import json

class OpenRouterAI:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.url = "https://openrouter.ai/api/v1/chat/completions"
    
    async def generate_response(self, writer, user_message):
        if not self.api_key:
            return "🎭 Настройки ИИ не завершены."
        
        # Простой промпт
        prompt = {
            "model": "meta-llama/llama-3.1-8b-instruct:free",
            "messages": [
                {
                    "role": "system", 
                    "text": f"Ты - {writer}. Отвечай коротко в его стиле."
                },
                {
                    "role": "user",
                    "text": user_message
                }
            ],
            "max_tokens": 100,
            "temperature": 0.7
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.url, json=prompt, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result['choices'][0]['message']['content']
                    else:
                        return f"🎭 {writer.title()}: Извините, сервис временно недоступен."
        except:
            return f"🎭 {writer.title()}: Не могу подключиться к ИИ."

openrouter_ai = OpenRouterAI()
