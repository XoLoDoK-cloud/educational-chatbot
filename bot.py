import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from ai_openrouter import openrouter_ai

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Храним выбор писателя для каждого пользователя
user_sessions = {}

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("📚 Литературный бот с ИИ! Напишите /writers")

@dp.message(Command("writers"))
async def show_writers(message: types.Message):
    writers_list = """
🎭 Выберите писателя:

• Пушкин
• Достоевский  
• Толстой
• Чехов
• Гоголь

Напишите имя писателя для умной беседы с ИИ!
    """
    await message.answer(writers_list)

@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    text = message.text.lower()
    
    # Если уже выбран писатель - используем ИИ
    if user_id in user_sessions:
        writer = user_sessions[user_id]
        await message.bot.send_chat_action(message.chat.id, "typing")
        ai_response = await openrouter_ai.generate_response(writer, text)
        await message.answer(f"🎭 {ai_response}")
        return
    
    # Выбор писателя
    writers = ["пушкин", "достоевский", "толстой", "чехов", "гоголь"]
    for writer in writers:
        if writer in text:
            user_sessions[user_id] = writer
            await message.answer(f"🎭 Выбрали {writer.title()}! Теперь ИИ отвечает в его стиле. Напишите что-нибудь!")
            return
    
    await
