import os
import aiohttp
import asyncio

async def test():
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not api_key:
        print("❌ Ключ не найден!")
        return
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    prompt = {
        "model": "google/gemma-7b-it:free",
        "messages": [
            {
                "role": "system",
                "content": "Ты - Пушкин. Отвечай в стиле поэта."
            },
            {
                "role": "user", 
                "content": "Привет! Как настроение?"
            }
        ],
        "max_tokens": 100
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://t.me/literarybot",
        "X-Title": "Literary Bot"
    }
    
    try:
        print("🔄 Тестируем новый ключ...")
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=prompt, headers=headers) as response:
                print(f"📡 Статус: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    print("✅ УСПЕХ! OpenRouter работает!")
                    print("🤖 Ответ ИИ:")
                    print(result['choices'][0]['message']['content'])
                else:
                    error_text = await response.text()
                    print(f"❌ ОШИБКА: {error_text}")
                    
    except Exception as e:
        print(f"❌ Ошибка соединения: {e}")

asyncio.run(test())
