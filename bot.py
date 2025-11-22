import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

logging.basicConfig(level=logging.INFO)

# Безопасное получение токена из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    logging.error("❌ BOT_TOKEN не найден! Добавьте его в Secrets")
    exit(1)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_command(message: types.Message):
    welcome_text = """
📚 Добро пожаловать в мир литературных бесед!

Я - бот, который может вести диалог в стиле великих писателей.

Доступные команды:
/writers - Выбрать писателя
/help - Помощь

Выберите автора и погрузитесь в уникальную беседу!
    """
    await message.answer(welcome_text)

@dp.message(Command("writers"))
async def show_writers(message: types.Message):
    writers_list = """
🎭 Выберите писателя для беседы:

• Пушкин - романтичный и остроумный
• Достоевский - глубокий и философский  
• Толстой - мудрый и простой
• Чехов - ироничный и лаконичный
• Гоголь - мистический и с юмором

Напишите имя писателя чтобы начать диалог!
    """
    await message.answer(writers_list)

@dp.message()
async def handle_message(message: types.Message):
    text = message.text.lower()
    
    if "пушкин" in text:
        await message.answer("🎭 Пушкин: Приветствую, мой друг!")
    elif "достоевский" in text:
        await message.answer("🎭 Достоевский: Здравствуйте...")
    elif "толстой" in text:
        await message.answer("🎭 Толстой: Здравствуйте, друг мой!")
    else:
        await message.answer("Напишите /writers чтобы увидеть список писателей")

async def main():
    print("🟢 Литературный бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
