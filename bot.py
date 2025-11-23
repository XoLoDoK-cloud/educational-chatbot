import logging
import asyncio
import json
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from ai_openrouter import generate_universal_response
from flask import Flask
from threading import Thread

# Настройка
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Keep-alive
app = Flask('')
@app.route('/') 
def home(): return "🤖 AI Expert Bot is ALIVE!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run, daemon=True).start()

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
user_sessions = {}

# Клавиатуры
def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎭 Выбрать писателя")],
            [KeyboardButton(text="🔄 Сменить стиль")]
        ], 
        resize_keyboard=True
    )

def get_writers_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🖋️ Пушкин"), KeyboardButton(text="🎭 Достоевский")],
            [KeyboardButton(text="📖 Толстой"), KeyboardButton(text="✒️ Чехов")],
            [KeyboardButton(text="🔮 Гоголь")]
        ],
        resize_keyboard=True
    )

# Загрузка данных автора
def load_author(writer):
    try:
        with open(f"writers/{writer}.json", 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None

# КОМАНДЫ БОТА
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    user_sessions[message.from_user.id] = None
    welcome = """
🧠 *LiteraryAI Expert* - УНИВЕРСАЛЬНЫЙ AI-ПОМОЩНИК

Я знаю ответы на ЛЮБЫЕ вопросы как ChatGPT, но отвечаю в стиле великих писателей!

• 🔬 Наука и техника
• 📚 История и искусство  
• 💻 Программирование
• 🌍 География и культура
• 🎯 Анализ и объяснения

*Выберите писателя и задавайте ВОПРОСЫ ЛЮБОЙ СЛОЖНОСТИ!*
    """
    await message.answer(welcome, parse_mode="Markdown", reply_markup=get_main_keyboard())

@dp.message(Command("writers"))
async def writers_cmd(message: types.Message):
    await message.answer("🎭 Выберите стиль ответа:", reply_markup=get_writers_keyboard())

# ОБРАБОТЧИКИ КНОПОК
@dp.message(lambda msg: msg.text == "🎭 Выбрать писателя")
async def select_writer(msg: types.Message):
    await writers_cmd(msg)

@dp.message(lambda msg: msg.text in ["🖋️ Пушкин", "🎭 Достоевский", "📖 Толстой", "✒️ Чехов", "🔮 Гоголь"])
async def set_writer(msg: types.Message):
    writer_map = {
        "🖋️ Пушкин": "пушкин", "🎭 Достоевский": "достоевский",
        "📖 Толстой": "толстой", "✒️ Чехов": "чехов", "🔮 Гоголь": "гоголь"
    }
    writer = writer_map[msg.text]
    user_sessions[msg.from_user.id] = writer
    author = load_author(writer)
    await msg.answer(f"✅ *{author['name']} активирован!*\n\nЗадавайте ЛЮБЫЕ вопросы - я знаю ответы на всё! 🧠", 
                    parse_mode="Markdown", reply_markup=get_main_keyboard())

@dp.message(lambda msg: msg.text == "🔄 Сменить стиль")
async def change_style(msg: types.Message):
    user_sessions[msg.from_user.id] = None
    await msg.answer("🔄 Стиль сброшен. Выберите нового писателя:", reply_markup=get_writers_keyboard())

# ГЛАВНЫЙ ОБРАБОТЧИК СООБЩЕНИЙ
@dp.message()
async def handle_all_questions(message: types.Message):
    user_id = message.from_user.id
    question = message.text.strip()
    
    # Проверяем выбран ли писатель
    if user_id not in user_sessions or not user_sessions[user_id]:
        await message.answer("🎭 Сначала выберите стиль ответа!", reply_markup=get_main_keyboard())
        return
    
    writer = user_sessions[user_id]
    author_data = load_author(writer)
    
    # Показываем "печатает"
    await message.bot.send_chat_action(message.chat.id, "typing")
    
    try:
        # 🔥 УНИВЕРСАЛЬНЫЙ ОТВЕТ НА ЛЮБОЙ ВОПРОС
        expert_response = await generate_universal_response(question, author_data)
        await message.answer(expert_response, parse_mode="Markdown")
        
    except Exception as e:
        await message.answer("⚡ Произошла ошибка, но как эксперт продолжаю работать!")

# ЗАПУСК БОТА
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    keep_alive()
    logger.info("🚀 УНИВЕРСАЛЬНЫЙ AI-ЭКСПЕРТ ЗАПУЩЕН!")
    print("🧠 Бот готов! Задавайте ЛЮБЫЕ вопросы!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
