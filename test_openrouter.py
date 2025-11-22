import os
import aiohttp
import asyncio

async def test_openrouter():
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not api_key:
        print("❌ Ключ не найден в Secrets!")
        return
    
    url = "https://openrouter.ai/api/v1/models"
    
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                print(f"📡 Статус ответа: {response.status}")
                
                if response.status == 200:
                    models = await response.json()
                    print("✅ OpenRouter API работает!")
                    print("🎯 Доступные бесплатные модели:")
                    
                    free_models = [m for m in models['data'] if ':free' in m['id']]
                    for model in free_models[:5]:  # Покажем 5 моделей
                        print(f"   - {model['id']}")
                        
                else:
                    error = await response.text()
                    print(f"❌ Ошибка: {error}")
                    
    except Exception as e:
        print(f"❌ Ошибка соединения: {e}")

# Запуск теста
asyncio.run(test_openrouter())
