"""
Literary ChatGPT - Autonomous Neural Network for World Literature
Литературный ChatGPT - Автономная нейросеть для мировой литературы
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
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


def get_main_keyboard():
    """Main menu keyboard"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❓ Вопрос о литературе"), KeyboardButton(text="👥 Беседа с писателем")],
            [KeyboardButton(text="🧹 Очистить память"), KeyboardButton(text="ℹ️ О боте")],
            [KeyboardButton(text="🆘 Справка")]
        ],
        resize_keyboard=True
    )


def get_writers_keyboard():
    """Keyboard for selecting writers"""
    writers = get_available_writers()
    keyboard = []
    for writer in writers:
        keyboard.append([KeyboardButton(text=f"📖 {writer['name']}")])
    keyboard.append([KeyboardButton(text="🔙 В меню")])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Start command"""
    user_id = message.from_user.id
    clear_user_memory(user_id)
    
    await message.answer(
        "🧠 **LITERARY CHATGPT** 📚\n\n"
        "Добро пожаловать в Literary ChatGPT - автономную нейросеть по мировой литературе!\n\n"
        "**Я могу:**\n"
        "❓ Ответить на вопросы о писателях, книгах, жанрах\n"
        "🎭 Поговорить как русский классик!\n"
        "📖 Анализировать литературные произведения\n"
        "💭 Обсуждать историю и стиль литературы\n\n"
        "**Выберите режим:**\n"
        "• ❓ **Вопросы** - спросить о литературе\n"
        "• 👥 **Беседы** - поговорить с Пушкиным, Толстым, Достоевским, Чеховым или Гоголем!\n\n"
        "Нажмите кнопку ниже или напишите вопрос!",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )


@dp.message(Command("help"))
@dp.message(F.text == "🆘 Справка")
async def cmd_help(message: types.Message):
    """Help command"""
    help_text = """
🤖 **КАК ИСПОЛЬЗОВАТЬ LITERARY CHATGPT**

**Что я могу делать:**
✓ Ответить на вопросы о писателях, книгах, литературных движениях
✓ Углублённо анализировать произведения
✓ Сравнивать авторов и их стили
✓ Обсуждать историю литературы
✓ Поговорить как исторический писатель!

**Два режима работы:**

**1️⃣ РЕЖИМ ВОПРОСОВ (❓ Вопрос о литературе)**
• Задавайте вопросы о литературе
• Получайте ответы от AI Claude 3.5 Sonnet
• Примеры:
  - О стиле Достоевского
  - Что такое романтизм?
  - Анализ "Войны и мира"
  - Сравните Пушкина и Толстого

**2️⃣ РЕЖИМ БЕСЕД С ПИСАТЕЛЯМИ (👥 Беседа с писателем)**
• Выберите писателя из списка:
  📖 Александр Пушкин (1799-1837)
  📖 Лев Толстой (1828-1910)
  📖 Фёдор Достоевский (1821-1881)
  📖 Антон Чехов (1860-1904)
  📖 Николай Гоголь (1809-1852)
• Беседуйте как с историческим персоналием!
• Узнавайте их мысли и философию
• Писатели обсуждают литературу глубоко!

**Особенности:**
🧠 AI Claude 3.5 Sonnet (продвинутый)
📚 Полная база знаний о литературе
💭 Сохранение разговоров (30 сообщений)
🎭 Подлинные персоналии писателей
🌍 Мировая и русская литература
🎓 Анализ литературных произведений

Начните с выбора режима!
"""
    await message.answer(help_text, parse_mode="Markdown", reply_markup=get_main_keyboard())


@dp.message(Command("about"))
@dp.message(F.text == "ℹ️ О боте")
async def cmd_about(message: types.Message):
    """About command"""
    about_text = """
📚 **О LITERARY CHATGPT**

**Архитектура:**
• Нейросеть: Claude 3.5 Sonnet (OpenRouter)
• База знаний: Wikipedia + Русская литература
• Память: История разговоров (30 сообщений/пользователя)
• Интерфейс: Telegram Bot (@LiteraryCompanionBot)

**Две режима:**
1️⃣ **Режим вопросов** - Спрашивайте о литературе
2️⃣ **Режим бесед** - Говорите с писателями!

**Доступные писатели:**
📖 Александр Пушкин (1799-1837)
📖 Лев Толстой (1828-1910)
📖 Фёдор Достоевский (1821-1881)
📖 Антон Чехов (1860-1904)
📖 Николай Гоголь (1809-1852)

**Возможности:**
✓ Автономные ответы от AI
✓ Глубокий анализ литературы
✓ Беседы с персоналиями писателей
✓ Сохранение контекста разговора
✓ Мировая и русская литература

**Технология:**
• Python 3 + Aiogram
• Aiohttp для асинхронных запросов
• Real-time обработка данных

**Языки:** Русский/Английский

Полностью автономная нейросеть для глубокого погружения в мир литературы.
"""
    await message.answer(about_text, parse_mode="Markdown", reply_markup=get_main_keyboard())


@dp.message(Command("clear"))
@dp.message(F.text == "🧹 Очистить память")
async def cmd_clear(message: types.Message):
    """Clear conversation history"""
    user_id = message.from_user.id
    clear_user_memory(user_id)
    await message.answer(
        "✅ Память разговора очищена. Вы можете начать с новыми вопросами!",
        reply_markup=get_main_keyboard()
    )


@dp.message(F.text == "❓ Вопрос о литературе")
async def cmd_ask(message: types.Message):
    """Prompt for question"""
    await message.answer(
        "📝 Задайте ваш вопрос о литературе! Я помогу вам найти ответ.",
        reply_markup=get_main_keyboard()
    )


@dp.message(F.text == "👥 Беседа с писателем")
async def cmd_talk_writers(message: types.Message):
    """Show available writers"""
    writers = get_available_writers()
    writers_list = "\n".join([f"📖 {w['name']} ({w['birth']}-{w['death']})" for w in writers])
    
    await message.answer(
        f"🎭 **ВЫБЕРИТЕ ПИСАТЕЛЯ ДЛЯ БЕСЕДЫ**\n\n"
        f"Доступные писатели:\n{writers_list}\n\n"
        f"Нажмите на интересующего вас писателя:",
        parse_mode="Markdown",
        reply_markup=get_writers_keyboard()
    )


@dp.message(F.text.startswith("📖"))
async def select_writer(message: types.Message):
    """Handle writer selection"""
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
            
            await message.answer(
                f"✨ **{writer_info['name']}** приветствует вас!\n\n"
                f"*\"{opening}\"*\n\n"
                f"📝 Напишите свой вопрос или начните беседу...",
                parse_mode="Markdown",
                reply_markup=get_main_keyboard()
            )
            logger.info(f"User {user_id} selected writer: {writer_key}")
        else:
            await message.answer("❌ Ошибка загрузки писателя", reply_markup=get_main_keyboard())
    else:
        await message.answer("❌ Ошибка выбора писателя", reply_markup=get_main_keyboard())


@dp.message(F.text == "🔙 В меню")
async def back_to_menu(message: types.Message):
    """Go back to main menu"""
    await message.answer(
        "Вы вернулись в главное меню. Выберите режим работы.",
        reply_markup=get_main_keyboard()
    )


@dp.message()
async def handle_text(message: types.Message):
    """Handle text messages - routes to writer or Q&A"""
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
            prefix = f"**{writer_info['name']}**: " if writer_info else ""
        else:
            # Regular Q&A mode
            logger.info(f"Switching to Q&A mode")
            response = await answer_literature_question(user_id, question)
            prefix = ""
        
        logger.info(f"✓ Response generated: {response[:50]}...")
        
        if not response:
            response = "Мне нужен момент, чтобы подумать. Пожалуйста, попробуйте снова."
            logger.warning("Empty response, using default")
        
        # Send response
        await message.answer(prefix + response, parse_mode="Markdown", reply_markup=get_main_keyboard())
        logger.info(f"✅ Response sent to user {user_id}")
        
    except Exception as e:
        logger.error(f"❌ ERROR processing message: {e}", exc_info=True)
        try:
            await message.answer(
                "⚠️ Что-то пошло не так. Пожалуйста, попробуйте снова.",
                reply_markup=get_main_keyboard()
            )
            logger.info("✓ Error message sent to user")
        except Exception as send_err:
            logger.error(f"❌ Failed to send error message: {send_err}")


async def main():
    """Main function to start the bot"""
    logger.info("🚀 Starting Literary ChatGPT...")
    logger.info("🧠 Mode: Autonomous Neural Network")
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
