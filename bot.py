import logging
from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import asyncio
import json
import os
from config import BOT_TOKEN
from ai_openrouter import generate_literary_response

# Настройка логирования
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Храним выбор писателя для каждого пользователя
user_sessions = {}

# Красивая клавиатура
def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚 Выбрать писателя"), KeyboardButton(text="🔄 Сменить писателя")],
            [KeyboardButton(text="🌟 Рекомендации"), KeyboardButton(text="💫 Случайный писатель")]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_writers_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🖋️ Пушкин"), KeyboardButton(text="🎭 Достоевский")],
            [KeyboardButton(text="📖 Толстой"), KeyboardButton(text="✒️ Чехов")],
            [KeyboardButton(text="🔮 Гоголь"), KeyboardButton(text="⬅️ Назад")]
        ],
        resize_keyboard=True
    )
    return keyboard

@dp.message(Command("start"))
async def start_command(message: types.Message):
    # Сбрасываем сессию при старте
    user_sessions[message.from_user.id] = None
    
    welcome_text = """
🌟 *Добро пожаловать в литературную нейросеть!* 🌟

Я — автономная нейросеть, которая генерирует ответы в стиле великих русских писателей.

*🧠 Как это работает:*
• Нейросеть анализирует ваш вопрос
• Генерирует уникальный ответ в стиле выбранного писателя
• Использует литературные patterns и vocabulary автора
• Создает новые, никогда не существовавшие ответы

Выберите писателя и задавайте ЛЮБЫЕ вопросы!
    """
    
    await message.answer(welcome_text, parse_mode="Markdown", reply_markup=get_main_keyboard())

@dp.message(Command("writers"))
async def show_writers(message: types.Message):
    await message.answer("🎭 Выберите писателя:", reply_markup=get_writers_keyboard())

@dp.message(lambda message: message.text == "📚 Выбрать писателя")
async def select_writer_button(message: types.Message):
    await show_writers(message)

@dp.message(lambda message: message.text == "🔄 Сменить писателя")
async def change_writer(message: types.Message):
    user_sessions[message.from_user.id] = None
    await message.answer("🔄 Писатель сброшен. Выберите нового:", reply_markup=get_writers_keyboard())

@dp.message(lambda message: message.text in ["🖋️ Пушкин", "🎭 Достоевский", "📖 Толстой", "✒️ Чехов", "🔮 Гоголь"])
async def handle_writer_button(message: types.Message):
    writer_map = {
        "🖋️ Пушкин": "пушкин",
        "🎭 Достоевский": "достоевский", 
        "📖 Толстой": "толстой",
        "✒️ Чехов": "чехов",
        "🔮 Гоголь": "гоголь"
    }
    
    writer = writer_map[message.text]
    user_sessions[message.from_user.id] = writer
    
    writer_names = {
        "пушкин": "Александр Сергеевич Пушкин",
        "достоевский": "Фёдор Михайлович Достоевский",
        "толстой": "Лев Николаевич Толстой", 
        "чехов": "Антон Павлович Чехов",
        "гоголь": "Николай Васильевич Гоголь"
    }
    
    await message.answer(
        f"🎭 *{writer_names[writer]}*\n\n"
        f"🧠 Нейросеть активирована в стиле {writer_names[writer]}!\n\n"
        f"Задавайте ЛЮБЫЕ вопросы - нейросеть сгенерирует уникальный ответ в стиле автора!",
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()
    )

@dp.message(lambda message: message.text == "💫 Случайный писатель")
async def random_writer(message: types.Message):
    import random
    writers = ["пушкин", "достоевский", "толстой", "чехов", "гоголь"]
    selected_writer = random.choice(writers)
    
    user_sessions[message.from_user.id] = selected_writer
    
    writer_names = {
        "пушкин": "Александр Сергеевич Пушкин",
        "достоевский": "Фёдор Михайлович Достоевский", 
        "толстой": "Лев Николаевич Толстой",
        "чехов": "Антон Павлович Чехов",
        "гоголь": "Николай Васильевич Гоголь"
    }
    
    await message.answer(
        f"🎲 *Случайный выбор: {writer_names[selected_writer]}!*\n\n"
        f"🧠 Нейросеть генерирует ответы в стиле {writer_names[selected_writer]}\n\n"
        f"Задавайте вопросы - AI создаст уникальные литературные ответы!",
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()
    )

@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    text = message.text
    
    # Игнорируем служебные кнопки
    if text in ["📚 Выбрать писателя", "🔄 Сменить писателя", "🌟 Рекомендации", "💫 Случайный писатель", "⬅️ Назад"]:
        return
    
    # Если уже выбран писатель - генерируем ответ нейросетью
    if user_id in user_sessions and user_sessions[user_id]:
        writer = user_sessions[user_id]
        
        # Показываем статус "печатает"
        await message.bot.send_chat_action(message.chat.id, "typing")
        
        # 🔥 НЕЙРОСЕТЬ ГЕНЕРИРУЕТ ОТВЕТ НА ЛЮБОЙ ВОПРОС
        ai_response = neural_ai.generate_response(writer, text)
        
        # Отправляем сгенерированный ответ
        writer_names = {
            "пушкин": "Пушкин",
            "достоевский": "Достоевский",
            "толстой": "Толстой", 
            "чехов": "Чехов",
            "гоголь": "Гоголь"
        }
        
        await message.answer(
            f"*{writer_names[writer]}:* {ai_response}",
            parse_mode="Markdown"
        )
        return
    
    # Выбор писателя по тексту
    writers = ["пушкин", "достоевский", "толстой", "чехов", "гоголь"]
    for writer in writers:
        if writer in text.lower():
            user_sessions[user_id] = writer
            writer_names = {
                "пушкин": "Александр Сергеевич Пушкин",
                "достоевский": "Фёдор Михайлович Достоевский",
                "толстой": "Лев Николаевич Толстой",
                "чехов": "Антон Павлович Чехов", 
                "гоголь": "Николай Васильевич Гоголь"
            }
            
            await message.answer(
                f"🎭 *{writer_names[writer]}*\n\n"
                f"🧠 Нейросеть активирована!\n\n"
                f"Задавайте вопросы - AI сгенерирует уникальные ответы в стиле {writer_names[writer]}!",
                parse_mode="Markdown",
                reply_markup=get_main_keyboard()
            )
            return
    
    # Если писатель не выбран
    await message.answer(
        "🎭 Сначала выберите писателя!\n\n"
        "Нажмите «📚 Выбрать писателя» или напишите имя автора.",
        reply_markup=get_main_keyboard()
    )

async def main():
    print("🧠 Литературная нейросеть запущена!")
    print("🎭 Готова генерировать ответы в стиле великих писателей!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
if __name__ == "__main__":
    print("🤖 Starting Literary Companion Bot...")
    # Убедитесь, что у вас есть функция main() или аналог
    import asyncio
    asyncio.run(main())  # или как у вас называется функция запуска
