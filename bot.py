"""
Literary AI Bot - ChatGPT-Style Writers Expert
Telegram Interface for Ultimate Writers Knowledge
"""
import logging
import asyncio
import random
import json

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from universal_brain import generate_response, clear_memory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

writers = {
    "pushkin": "🎭 Пушкин",
    "dostoevsky": "📖 Достоевский",
    "tolstoy": "🏛️ Толстой",
    "chekhov": "🎪 Чехов",
    "gogol": "👻 Гоголь"
}

user_sessions = {}


def load_author_data(writer_key):
    """Load author data"""
    try:
        with open(f"writers/{writer_key}.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except:
        names = {
            "pushkin": "Александр Пушкин",
            "dostoevsky": "Фёдор Достоевский",
            "tolstoy": "Лев Толстой",
            "chekhov": "Антон Чехов",
            "gogol": "Николай Гоголь"
        }
        return {"name": names.get(writer_key, "Unknown")}


def get_main_keyboard():
    """Main menu"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚 Выбрать писателя")],
            [KeyboardButton(text="🎲 Случайный писатель")],
            [KeyboardButton(text="❓ О боте")]
        ],
        resize_keyboard=True
    )


def get_writers_keyboard():
    """Writers selection"""
    keyboard = [[KeyboardButton(text=name)] for name in writers.values()]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Start"""
    user_id = message.from_user.id
    clear_memory(user_id)
    user_sessions[user_id] = None
    
    await message.answer(
        "🎭 **Добро пожаловать в WRITERS EXPERT BOT**\n\n"
        "Это AI-эксперт, как ChatGPT, но специализированный на писателях и литературе.\n\n"
        "✨ Я знаю ВСЕХ писателей мира:\n"
        "• Русских классиков\n"
        "• Европейских гениев\n"
        "• Американских мастеров\n"
        "• Модернистов\n"
        "• И ещё сотни других...\n\n"
        "🎯 Выберите писателя и задавайте мне вопросы!",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )


@dp.message(F.text == "📚 Выбрать писателя")
async def cmd_select_writer(message: types.Message):
    """Select writer"""
    await message.answer("Выберите писателя:", reply_markup=get_writers_keyboard())


@dp.message(F.text.in_([name for name in writers.values()]))
async def set_writer(message: types.Message):
    """Set writer"""
    user_id = message.from_user.id
    writer_name = message.text
    
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
            f"Теперь я буду отвечать в его стиле как на вопросы о нём, так и о других писателях.",
            reply_markup=get_main_keyboard()
        )


@dp.message(F.text == "🎲 Случайный писатель")
async def random_writer(message: types.Message):
    """Random writer"""
    user_id = message.from_user.id
    key = random.choice(list(writers.keys()))
    user_sessions[user_id] = key
    clear_memory(user_id)
    
    data = load_author_data(key)
    await message.answer(
        f"🎲 Случайно выбран: {data['name']}\n\nТеперь задавайте вопросы!",
        reply_markup=get_main_keyboard()
    )


@dp.message(F.text == "❓ О боте")
async def about_bot(message: types.Message):
    """About bot"""
    await message.answer(
        "🤖 **WRITERS EXPERT BOT - ChatGPT для Литературы**\n\n"
        "Это бот на основе искусственного интеллекта, который знает ВСЁ о писателях:\n\n"
        "📖 **Его специальность:**\n"
        "• Биография любого писателя\n"
        "• Анализ произведений\n"
        "• Исторический контекст\n"
        "• Влияние на литературу\n"
        "• Сравнение писателей\n"
        "• Литературные течения\n\n"
        "✨ **Особенность:**\n"
        "Ответы даются в стиле выбранного вами писателя с ПОЛНОЙ УВЕРЕННОСТЬЮ\n\n"
        "🎯 Выбирайте писателя и задавайте вопросы!",
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()
    )


@dp.message()
async def handle_message(message: types.Message):
    """Main handler"""
    user_id = message.from_user.id
    text = message.text
    
    if user_id not in user_sessions or not user_sessions[user_id]:
        await message.answer(
            "🎭 Выберите писателя: нажмите «📚 Выбрать писателя»",
            reply_markup=get_main_keyboard()
        )
        return
    
    writer_key = user_sessions[user_id]
    author_data = load_author_data(writer_key)
    
    await message.bot.send_chat_action(message.chat.id, "typing")
    
    try:
        logger.info(f"Generating response for user {user_id}")
        response = await generate_response(user_id, text, author_data)
        
        if not response:
            response = "Ошибка. Попробуйте ещё раз."
        
        await message.answer(f"{response}", parse_mode="Markdown")
        logger.info(f"Sent response to {user_id}")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await message.answer("⚠️ Ошибка при обработке. Попробуйте ещё раз.")


async def main():
    """Start bot"""
    print("🚀 Запуск WRITERS EXPERT BOT...")
    print(f"🎭 Режим: ChatGPT для Писателей")
    print("=" * 50)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
