import os

key = os.getenv("OPENROUTER_API_KEY")
if key:
    print("✅ OpenRouter ключ найден!")
    print("✅ Готово к интеграции ИИ!")
else:
    print("❌ Ключ еще не добавлен в Secrets")
