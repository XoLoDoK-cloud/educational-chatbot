#!/usr/bin/env python3
"""
Simple & Reliable Telegram Bot - Works 100%
Простой и надёжный Telegram бот
"""
import asyncio
import logging
from datetime import datetime

try:
    from aiogram import Bot, Dispatcher, types, F
    from aiogram.filters import Command
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    from aiogram.fsm.storage.memory import MemoryStorage
except ImportError as e:
    print(f"❌ Aiogram not installed: {e}")
    print("Install with: pip install aiogram")
    exit(1)

from config import BOT_TOKEN
from chatgpt_brain import answer_literature_question, clear_user_memory
from writers_brain import get_available_writers, set_user_writer, talk_to_writer, get_user_writer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN not found!")
    exit(1)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# User state
user_state = {}

def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❓ Вопросы"), KeyboardButton(text="👥 Писатели")],
            [KeyboardButton(text="📚 Справка"), KeyboardButton(text="⚙️ Меню")],
        ],
        resize_keyboard=True
    )

def get_writer_keyboard():
    writers = get_available_writers()
    keyboard = []
    for w in writers:
        keyboard.append([KeyboardButton(text=f"📖 {w['name']}")])
    keyboard.append([KeyboardButton(text="🔙 Назад")])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Start"""
    user_id = message.from_user.id
    user_state[user_id] = "menu"
    clear_user_memory(user_id)
    
    text = """
━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ LITERARY CHATBOT v3 ✨
━━━━━━━━━━━━━━━━━━━━━━━━━━

🧠 Добро пожаловать!

Выберите режим:
❓ Вопросы - спросите о литературе
👥 Писатели - поговорите с классиками
📚 Справка - помощь
⚙️ Меню - информация
"""
    await message.answer(text, reply_markup=get_main_keyboard())

@dp.message(F.text == "❓ Вопросы")
async def mode_questions(message: types.Message):
    user_id = message.from_user.id
    user_state[user_id] = "question"
    await message.answer("Напишите ваш вопрос о литературе:")

@dp.message(F.text == "👥 Писатели")
async def mode_writers(message: types.Message):
    user_id = message.from_user.id
    user_state[user_id] = "writer_select"
    text = "Выберите писателя для беседы:"
    await message.answer(text, reply_markup=get_writer_keyboard())

@dp.message(F.text == "📚 Справка")
async def cmd_help(message: types.Message):
    text = """
━━━━━━━━━━━━━━━━━━━━━━
📖 КАК ИСПОЛЬЗОВАТЬ
━━━━━━━━━━━━━━━━━━━━━━

❓ ВОПРОСЫ
Спросите о писателях, произведениях, жанрах.

👥 ПИСАТЕЛИ  
Поговорите с:
• Пушкин
• Толстой
• Достоевский
• Чехов
• Гоголь

Используйте команды:
/start - главное меню
/help - эта справка
/clear - очистить
"""
    await message.answer(text, reply_markup=get_main_keyboard())

@dp.message(F.text == "⚙️ Меню")
async def cmd_menu(message: types.Message):
    text = """
━━━━━━━━━━━━━━━━━━━━━━
⚙️ МЕНЮ
━━━━━━━━━━━━━━━━━━━━━━

Версия: 3.0
Статус: 🟢 ОНЛАЙН

Команды:
/start - начало
/help - справка
/clear - очистить
"""
    await message.answer(text, reply_markup=get_main_keyboard())

@dp.message(F.text == "🔙 Назад")
async def cmd_back(message: types.Message):
    user_id = message.from_user.id
    user_state[user_id] = "menu"
    text = "Вернулись в меню:"
    await message.answer(text, reply_markup=get_main_keyboard())

@dp.message(Command("clear"))
async def cmd_clear(message: types.Message):
    user_id = message.from_user.id
    clear_user_memory(user_id)
    await message.answer("✅ История очищена!")

@dp.message()
async def handle_text(message: types.Message):
    user_id = message.from_user.id
    text = message.text
    state = user_state.get(user_id, "menu")
    
    await bot.send_chat_action(message.chat.id, "typing")
    
    try:
        if state == "question":
            # Answer question
            response = await answer_literature_question(user_id, text)
            answer = f"📖 ОТВЕТ:\n\n{response}\n\n/start - меню"
            await message.answer(answer)
            
        elif state == "writer_select":
            # Select writer
            writers = get_available_writers()
            found = False
            for w in writers:
                if w['name'] in text:
                    set_user_writer(user_id, w['key'])
                    user_state[user_id] = "writer_talk"
                    found = True
                    intro = f"🎭 Беседа с {w['name']}\n\nНапишите что-нибудь:"
                    await message.answer(intro)
                    break
            
            if not found:
                await message.answer("❌ Писатель не найден", reply_markup=get_writer_keyboard())
        
        elif state == "writer_talk":
            # Talk to writer
            current_writer = get_user_writer(user_id)
            if current_writer:
                response = await talk_to_writer(user_id, text)
                await message.answer(response)
            else:
                await message.answer("❌ Выберите писателя", reply_markup=get_main_keyboard())
        
        else:
            await message.answer("Выберите режим", reply_markup=get_main_keyboard())
    
    except Exception as e:
        logger.error(f"Error: {e}")
        error_msg = f"❌ Ошибка: {str(e)[:100]}"
        await message.answer(error_msg)

async def main():
    logger.info("🚀 Starting Literary Bot v3 (Simple)")
    logger.info("✅ Ready!")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped")
