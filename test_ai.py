import asyncio
from ai_openrouter import openrouter_ai

async def test():
    response = await openrouter_ai.generate_response("пушкин", "Привет! Как твои дела?")
    print("Ответ ИИ:", response)

asyncio.run(test())
