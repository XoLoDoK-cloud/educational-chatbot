import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Text
from aiogram import F
from ai_openrouter import openrouter_ai

# Настройка логирования
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Храним выбор писателя для каждого пользователя
user_sessions = {}

# 🌟 КРАСИВЫЕ КЛАВИАТУРЫ

def get_main_keyboard():
    """Главное меню"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📚 Выбрать писателя"), 
                KeyboardButton(text="🔄 Сменить писателя")
            ],
            [
                KeyboardButton(text="🌟 Рекомендации"), 
                KeyboardButton(text="💫 Случайный писатель")
            ],
            [
                KeyboardButton(text="ℹ️ О проекте"), 
                KeyboardButton(text="📖 Помощь")
            ]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие или напишите сообщение..."
    )
    return keyboard

def get_writers_keyboard():
    """Красивая клавиатура выбора писателей"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🖋️ Александр Пушкин"), 
                KeyboardButton(text="🎭 Фёдор Достоевский")
            ],
            [
                KeyboardButton(text="📖 Лев Толстой"), 
                KeyboardButton(text="✒️ Антон Чехов")
            ],
            [
                KeyboardButton(text="🔮 Николай Гоголь"), 
                KeyboardButton(text="⬅️ В главное меню")
            ]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите писателя для глубокой беседы..."
    )
    return keyboard

def get_current_writer_keyboard(current_writer=None):
    """Клавиатура когда писатель уже выбран"""
    writer_name = "Писатель" if not current_writer else current_writer.title()
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🔄 Выбрать другого писателя"), 
                KeyboardButton(text="💭 Новый вопрос")
            ],
            [
                KeyboardButton(text="🌟 Рекомендации по беседе"), 
                KeyboardButton(text="📖 О текущем авторе")
            ],
            [
                KeyboardButton(text="⬅️ В главное меню")
            ]
        ],
        resize_keyboard=True,
        input_field_placeholder=f"Общайтесь с {writer_name} или выберите действие..."
    )
    return keyboard

# 🎯 КРАСИВЫЕ СООБЩЕНИЯ

@dp.message(Command("start"))
async def start_command(message: types.Message):
    # Сбрасываем сессию при старте
    user_sessions[message.from_user.id] = None
    
    welcome_text = """
🌟 *Добро пожаловать в мир литературных бесед!* 🌟

*«Слово — это мост между душами»*

Я — ваш проводник в мир великой русской литературы, где каждая беседа становится путешествием вглубь человеческой души и вечных вопросов бытия.

*✨ Что вас ждёт:*
• 🎭 Глубокие диалоги с великими писателями
• 📚 Стилизованные ответы в духе эпохи  
• 💫 Интеллектуальное общение на любые темы
• 🔄 Возможность легко сменить собеседника

*🎯 Как начать путешествие:*
Нажмите «📚 Выбрать писателя» или напишите имя автора

*💡 Совет:* Не бойтесь задавать глубокие вопросы — великие умы ждут вашего диалога!
    """
    
    await message.answer(welcome_text, parse_mode="Markdown", reply_markup=get_main_keyboard())

@dp.message(Command("writers"))
async def show_writers(message: types.Message):
    writers_text = """
🎭 *Выберите собеседника для глубокой беседы:*

*🖋️ Александр Пушкин* 
_Романтичный гений, мастер слова_
💫 Темы: любовь, свобода, творчество, дружба
✨ Стиль: элегантный, поэтичный, остроумный
