"""
Literary ChatGPT - Autonomous Neural Network for World Literature
Литературный ChatGPT - Автономная нейросеть для мировой литературы
Modern & Beautiful UI
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from chatgpt_brain import answer_literature_question, clear_user_memory
from writers_brain import (
    get_available_writers, set_user_writer, get_user_writer, 
    talk_to_writer, get_writer_info, clear_writer_conversation
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize bot
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Modern design elements
SEPARATOR = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
SUBSEP = "─────────────────────────────"


def get_main_keyboard():
    """Modern main menu keyboard"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❓ Вопросы"), KeyboardButton(text="👥 Писатели")],
            [KeyboardButton(text="📚 Справка"), KeyboardButton(text="⚙️ Меню")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )


def get_writers_keyboard():
    """Keyboard for selecting writers with modern styling"""
    writers = get_available_writers()
    keyboard = []
    for writer in writers:
        # Format: "📖 Pushkin (1799-1837)"
        keyboard.append([KeyboardButton(text=f"📖 {writer['name']}")])
    keyboard.append([KeyboardButton(text="🔙 Назад")])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Start command with modern design"""
    user_id = message.from_user.id
    clear_user_memory(user_id)
    
    welcome = f"""
{SEPARATOR}
    ✨ LITERARY CHATGPT ✨
{SEPARATOR}

🎓 Вас приветствует автономная нейросеть по мировой литературе!

{SUBSEP}
📖 ЧТО МОЖНО ДЕЛАТЬ:
{SUBSEP}

❓ Задавать вопросы о писателях и произведениях
   → О стиле Достоевского
   → Анализ "Войны и мира"
   → Сравнение авторов

🎭 Беседовать с русскими классиками
   → Пушкин, Толстой, Достоевский
   → Чехов, Гоголь и другие

📚 Обсуждать историю и теорию литературы
   → Литературные движения
   → Жанры и стили
   → Классические произведения

{SUBSEP}
🚀 НАЧНИТЕ РАБОТУ:
{SUBSEP}

Выберите режим выше или просто напишите вопрос!
"""
    
    await message.answer(
        welcome,
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )


@dp.message(Command("help"))
@dp.message(F.text == "📚 Справка")
async def cmd_help(message: types.Message):
    """Modern help page"""
    help_text = f"""
{SEPARATOR}
    📖 КАК ИСПОЛЬЗОВАТЬ БОТ
{SEPARATOR}

{SUBSEP}
🎯 РЕЖИМ 1: ВОПРОСЫ О ЛИТЕРАТУРЕ
{SUBSEP}

1️⃣ Нажмите "❓ Вопросы"
2️⃣ Напишите свой вопрос:
   • "Кто такой Пушкин?"
   • "Проанализируй Война и мир"
   • "Что такое романтизм?"

📝 Примеры вопросов:
   ✓ "Стиль Чехова"
   ✓ "Первое произведение Толстого"
   ✓ "Цитата Достоевского"
   ✓ "Преступление и наказание - тема"

{SUBSEP}
🎭 РЕЖИМ 2: БЕСЕДА С ПИСАТЕЛЯМИ
{SUBSEP}

1️⃣ Нажмите "👥 Писатели"
2️⃣ Выберите писателя из списка
3️⃣ Ведите беседу как с человеком!

Доступные писатели:
   📘 Александр Пушкин (1799-1837)
   📕 Лев Толстой (1828-1910)
   📙 Фёдор Достоевский (1821-1881)
   📗 Антон Чехов (1860-1904)
   📔 Николай Гоголь (1809-1852)

{SUBSEP}
⚙️ КОМАНДЫ
{SUBSEP}

/start    - Главное меню
/help     - Эта справка
/clear    - Очистить память
/about    - О боте

{SUBSEP}
✨ ОСОБЕННОСТИ
{SUBSEP}

🧠 AI Claude 3.5 Sonnet - мощная нейросеть
📚 База из 50+ авторов и 1000+ произведений
💭 Память на 30 сообщений (в одной беседе)
🌍 Русская и мировая литература
⚡ Быстрые ответы в реальном времени

"""
    
    await message.answer(help_text, parse_mode="Markdown", reply_markup=get_main_keyboard())


@dp.message(Command("about"))
@dp.message(F.text == "⚙️ Меню")
async def cmd_about(message: types.Message):
    """Modern about page"""
    about_text = f"""
{SEPARATOR}
    ℹ️ О LITERARY CHATGPT
{SEPARATOR}

{SUBSEP}
🏗️ АРХИТЕКТУРА
{SUBSEP}

✓ Нейросеть: Claude 3.5 Sonnet (OpenRouter)
✓ База знаний: 50+ авторов, 1000+ произведений
✓ Память: История разговоров (30 сообщений)
✓ Язык: Python 3 + Aiogram + AsyncIO

{SUBSEP}
🎯 РЕЖИМЫ РАБОТЫ
{SUBSEP}

Режим 1️⃣: Вопросы о литературе
   → AI анализирует ваш вопрос
   → Ищет в базе знаний
   → Дает структурированный ответ

Режим 2️⃣: Беседа с писателями
   → Каждый писатель имеет характер
   → Отвечает в своем стиле
   → Обсуждает свои произведения

{SUBSEP}
📚 БАЗа ЗНАНИЙ
{SUBSEP}

Русские авторы:
   • Пушкин, Толстой, Достоевский
   • Чехов, Гоголь, Лермонтов

Западные авторы:
   • Shakespeare, Jane Austen, Dickens
   • Fitzgerald, Kafka, Oscar Wilde

Содержит:
   • 1000+ произведений
   • Биографии авторов
   • Цитаты и анализ
   • Литературные движения

{SUBSEP}
🚀 ТЕХНОЛОГИИ
{SUBSEP}

Backend:  Python 3.12 + FastAPI
Messaging: Telegram API + Aiogram 3
AI Model: Claude 3.5 Sonnet (OpenRouter)
Storage: In-memory (session-based)

"""
    
    await message.answer(about_text, parse_mode="Markdown", reply_markup=get_main_keyboard())


@dp.message(Command("clear"))
@dp.message(F.text == "🧹 Очистить память")
async def cmd_clear(message: types.Message):
    """Clear memory with modern feedback"""
    user_id = message.from_user.id
    clear_user_memory(user_id)
    
    await message.answer(
        f"{SEPARATOR}\n"
        f"✅ ПАМЯТЬ ОЧИЩЕНА\n"
        f"{SEPARATOR}\n\n"
        f"Вы можете начать новую беседу с чистого листа!\n"
        f"Все предыдущие сообщения забыты.",
        reply_markup=get_main_keyboard()
    )


@dp.message(F.text == "❓ Вопросы")
async def cmd_ask(message: types.Message):
    """Prompt for question with modern design"""
    await message.answer(
        f"{SEPARATOR}\n"
        f"📝 РЕЖИМ ВОПРОСОВ\n"
        f"{SEPARATOR}\n\n"
        f"Напишите ваш вопрос о литературе:\n\n"
        f"✓ О писателях (Пушкин, Толстой...)\n"
        f"✓ О произведениях (Война и мир...)\n"
        f"✓ О литературных движениях\n"
        f"✓ Анализ и сравнение\n\n"
        f"💡 Я помогу вам получить точный ответ!",
        reply_markup=get_main_keyboard()
    )


@dp.message(F.text == "👥 Писатели")
async def cmd_talk_writers(message: types.Message):
    """Show writers selection with modern design"""
    writers = get_available_writers()
    
    writers_info = "\n".join([
        f"📖 {w['name']} ({w['birth']}-{w['death']})" 
        for w in writers
    ])
    
    writers_menu = f"""
{SEPARATOR}
    🎭 БЕСЕДА С ПИСАТЕЛЯМИ
{SEPARATOR}

Выберите писателя для беседы:

{writers_info}

{SUBSEP}

Вы сможете:
✓ Обсуждать литературу
✓ Спрашивать о его творчестве
✓ Узнавать его взгляды
✓ Беседовать в его стиле
"""
    
    await message.answer(
        writers_menu,
        parse_mode="Markdown",
        reply_markup=get_writers_keyboard()
    )


@dp.message(F.text.startswith("📖"))
async def select_writer(message: types.Message):
    """Handle writer selection with beautiful greeting"""
    user_id = message.from_user.id
    writer_name = message.text.replace("📖 ", "")
    
    # Find writer key
    writers = get_available_writers()
    writer_key = None
    for w in writers:
        if w['name'] == writer_name:
            writer_key = w['key']
            break
    
    if writer_key and set_user_writer(user_id, writer_key):
        writer_info = get_writer_info(writer_key)
        if writer_info:
            opening = writer_info['greetings'][0]
            
            greeting = f"""
{SEPARATOR}
    ✨ {writer_info['name'].upper()} ✨
{SEPARATOR}

{opening}

{SUBSEP}

📖 Вы вошли в беседу с {writer_info['name']}

Вы можете:
✓ Спрашивать о его жизни
✓ Обсуждать его произведения
✓ Узнавать его мысли о литературе
✓ Услышать его точку зрения

Напишите свой первый вопрос...
"""
            
            await message.answer(
                greeting,
                parse_mode="Markdown",
                reply_markup=get_main_keyboard()
            )
            logger.info(f"User {user_id} selected writer: {writer_key}")
        else:
            await message.answer(
                "❌ Ошибка загрузки писателя", 
                reply_markup=get_main_keyboard()
            )
    else:
        await message.answer(
            "❌ Ошибка выбора писателя", 
            reply_markup=get_main_keyboard()
        )


@dp.message(F.text == "🔙 Назад")
async def back_to_menu(message: types.Message):
    """Go back to main menu"""
    await message.answer(
        f"🔙 Вернулись в главное меню\n\n"
        f"Выберите режим работы или напишите вопрос.",
        reply_markup=get_main_keyboard()
    )


@dp.message()
async def handle_text(message: types.Message):
    """Handle text messages - routes to writer or Q&A with modern design"""
    user_id = message.from_user.id
    question = message.text
    
    logger.info(f"📨 MESSAGE RECEIVED from user {user_id}: {question[:100]}")
    
    try:
        # Show typing indicator
        await bot.send_chat_action(message.chat.id, "typing")
        logger.info(f"✓ Typing indicator sent")
        
        logger.info(f"Processing question: {question[:50]}...")
        
        # Check if user has selected a writer
        current_writer = get_user_writer(user_id)
        logger.info(f"Current writer: {current_writer}")
        
        if current_writer:
            # Talk with writer mode
            logger.info(f"Switching to writer mode: {current_writer}")
            response = await talk_to_writer(user_id, question)
            writer_info = get_writer_info(current_writer)
            
            # Format writer response
            if writer_info:
                formatted_response = f"""
{SUBSEP}
    📖 {writer_info['name']} отвечает:
{SUBSEP}

{response}

{SUBSEP}
"""
            else:
                formatted_response = response
            
            final_response = formatted_response
        else:
            # Regular Q&A mode
            logger.info(f"Switching to Q&A mode")
            response = await answer_literature_question(user_id, question)
            
            # Add decorative border
            final_response = f"""
{SUBSEP}
    🔍 АНАЛИЗ ЗАПРОСА
{SUBSEP}

{response}
"""
        
        logger.info(f"✓ Response generated: {response[:50]}...")
        
        if not response:
            final_response = (
                "🤔 Мне нужен момент, чтобы подумать.\n"
                "Пожалуйста, попробуйте снова."
            )
            logger.warning("Empty response, using default")
        
        # Send response with main keyboard
        await message.answer(
            final_response, 
            parse_mode="Markdown", 
            reply_markup=get_main_keyboard()
        )
        logger.info(f"✅ Response sent to user {user_id}")
        
    except Exception as e:
        logger.error(f"❌ ERROR processing message: {e}", exc_info=True)
        try:
            error_msg = (
                f"{SEPARATOR}\n"
                f"❌ ОШИБКА\n"
                f"{SEPARATOR}\n\n"
                f"Что-то пошло не так при обработке вашего вопроса.\n"
                f"Пожалуйста, попробуйте снова."
            )
            await message.answer(
                error_msg,
                reply_markup=get_main_keyboard()
            )
            logger.info("✓ Error message sent to user")
        except Exception as send_err:
            logger.error(f"❌ Failed to send error message: {send_err}")


async def main():
    """Main function to start the bot"""
    logger.info("🚀 Starting Literary ChatGPT...")
    logger.info("🧠 Mode: Autonomous Neural Network (Modern UI)")
    logger.info("📚 Sources: Claude 3.5 Sonnet + Wikipedia")
    logger.info("=" * 60)
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
