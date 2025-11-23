import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

async def main():
    print("🚀 ТЕСТОВЫЙ ЗАПУСК...")
    
    # Загружаем токен напрямую
    BOT_TOKEN = "8517599075:AAFrUWfuDXcHPH7AE-ZoGDjTJ8SquJ5Lxfw"
    print(f"🔑 Токен: {BOT_TOKEN[:10]}...")
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    @dp.message(Command("start"))
    async def start_cmd(message: types.Message):
        print("📨 Получен /start!")
        await message.answer("🤖 Тестовый бот работает!")
    
    # Сброс
    await bot.delete_webhook(drop_pending_updates=True)
    print("✅ Сброс выполнен")
    
    # Запуск
    print("🔄 Запуск polling...")
    await dp.start_polling(bot)
    
    await bot.session.close()

asyncio.run(main())
