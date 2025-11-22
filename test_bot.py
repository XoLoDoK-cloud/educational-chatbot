print("🚀 ТЕСТОВЫЙ БОТ ЗАПУСКАЕТСЯ!")

import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Проверяем токен
BOT_TOKEN = "8504839792:AAHNDV43QLJxixKWxB4-XaF6ZrcPMSKtw00"
print(f"🔑 Используем токен: {BOT_TOKEN[:10]}...")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    print("📨 Получена команда /start")
    await message.answer("🤖 ТЕСТ: Бот работает!")

@dp.message()
async def echo(message: types.Message):
    print(f"📨 Сообщение: {message.text}")
    await message.answer(f"Эхо: {message.text}")

async def main():
    print("🔄 Запускаем polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    print("✅ Начало выполнения")
    asyncio.run(main())
