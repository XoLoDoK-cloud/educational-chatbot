"""
Literary AI Bot - Telegram Interface
Universal expert with Russian writer personalities
"""
import logging
import asyncio
import random
import json
import os
from pathlib import Path

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from universal_brain import generate_response, clear_memory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot setup
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Writers
writers = {
    "pushkin": "Александр Пушкин",
    "dostoevsky": "Фёдор Достоевский",
    "tolstoy": "Лев Толстой",
    "chekhov": "Антон Чехов",
    "gogol": "Николай Гоголь"
}

user_sessions = {}


def load_author_data(writer_key):
    """Load author data from JSON"""
    try:
        with open(f"writers/{writer_key}.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"name": writers.get(writer_key, "Unknown")}


def get_main_keyboard():
    """Main menu keyboard"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚 Выбрать писателя")],
            [KeyboardButton(text="🔄 Сменить писателя")],
            [KeyboardButton(text="💫 Случайный писатель")]
        ],
        resize_keyboard=True
    )


def get_writers_keyboard():
    """Writers selection keyboard"""
    keyboard = []
    for key, name in writers.items():
        keyboard.append([KeyboardButton(text=name)])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Start command"""
    user_id = message.from_user.id
    logger.info(f"User {user_id} started bot")
    
    clear_memory(user_id)
    user_sessions[user_id] = None
    
    await message.answer(
        "🎭 Добро пожаловать в бота Литературных Экспертов!\n\n"
        "Выберите русского писателя, и он ответит на ваши вопросы с абсолютной уверенностью и знанием.",
        reply_markup=get_main_keyboard()
    )


async def check_select_writer(message: types.Message) -> bool:
    """Check if select writer button"""
    return message.text == "📚 Выбрать писателя"


@dp.message(check_select_writer)
async def cmd_select_writer(message: types.Message):
    """Select writer"""
    await message.answer(
        "Выберите писателя:",
        reply_markup=get_writers_keyboard()
    )


async def check_writer_name(message: types.Message) -> bool:
    """Check if message is writer name"""
    return message.text is not None and message.text in writers.values()


@dp.message(check_writer_name)
async def set_writer(message: types.Message):
    """Set selected writer"""
    user_id = message.from_user.id
    writer_name = message.text
    
    # Find key by name
    writer_key = None
    for key, name in writers.items():
        if name == writer_name:
            writer_key = key
            break
    
    if writer_key:
        user_sessions[user_id] = writer_key
        clear_memory(user_id)
        
        author_data = load_author_data(writer_key)
        await message.answer(
            f"✅ Выбран: {author_data['name']}\n\n"
            f"Теперь вы можете задавать вопросы, и {author_data['name']} будет отвечать как всезнающий эксперт!",
            reply_markup=get_main_keyboard()
        )


async def check_change_writer(message: types.Message) -> bool:
    """Check if change writer button"""
    return message.text == "🔄 Сменить писателя"


@dp.message(check_change_writer)
async def cmd_change_writer(message: types.Message):
    """Change writer"""
    await cmd_select_writer(message)


async def check_random_writer(message: types.Message) -> bool:
    """Check if random writer button"""
    return message.text == "💫 Случайный писатель"


@dp.message(check_random_writer)
async def cmd_random_writer(message: types.Message):
    """Random writer"""
    user_id = message.from_user.id
    writer_key = random.choice(list(writers.keys()))
    user_sessions[user_id] = writer_key
    clear_memory(user_id)
    
    author_data = load_author_data(writer_key)
    await message.answer(
        f"🎲 Случайно выбран: {author_data['name']}",
        reply_markup=get_main_keyboard()
    )


@dp.message()
async def handle_message(message: types.Message):
    """Main message handler"""
    user_id = message.from_user.id
    text = message.text
    
    logger.info(f"Message from {user_id}: {text[:50]}")
    
    # Check writer selected
    if user_id not in user_sessions or not user_sessions[user_id]:
        await message.answer(
            "🎭 Сначала выберите писателя!\n\nНажмите «📚 Выбрать писателя»",
            reply_markup=get_main_keyboard()
        )
        return
    
    writer_key = user_sessions[user_id]
    author_data = load_author_data(writer_key)
    
    # Show typing
    await message.bot.send_chat_action(message.chat.id, "typing")
    
    try:
        logger.info(f"Generating response from {author_data['name']}")
        
        # Generate response
        response = await generate_response(user_id, text, author_data)
        
        if not response:
            response = "Извините, ошибка при генерации ответа."
        
        # Send response
        writer_names = {
            "pushkin": "🎭 Пушкин",
            "dostoevsky": "🎭 Достоевский",
            "tolstoy": "🎭 Толстой",
            "chekhov": "🎭 Чехов",
            "gogol": "🎭 Гоголь"
        }
        
        header = writer_names.get(writer_key, "Писатель")
        await message.answer(f"{header}:\n\n{response}", parse_mode="Markdown")
        
        logger.info(f"Response sent to {user_id}")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await message.answer("⚠️ Ошибка при обработке. Попробуйте ещё раз.")


async def main():
    """Start bot"""
    print("🚀 Запуск бота...")
    print(f"🔑 Токен: {BOT_TOKEN[:20]}...")
    print("🎭 Режим: Литературные эксперты")
    print("=" * 50)
    
    # Start polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
