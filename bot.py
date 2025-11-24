"""
Literary Genius Bot - AI Expert in World Literature
Telegram Interface for Deep Knowledge About Writers and Their Works
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
from universal_brain import generate_response, generate_dialogue_response, clear_memory
from literary_knowledge import search_literature, get_works, answer_question

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

writers = {
    "pushkin": "🎭 Пушкин",
    "dostoevsky": "📖 Достоевский",
    "tolstoy": "🏛️ Толстой",
    "chekhov": "🎪 Чехов",
    "gogol": "👻 Гоголь",
    "fonvizin": "🎬 Фонвизин"
}

user_sessions = {}
user_modes = {}  # "expert" или "dialogue" режим


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
            "gogol": "Николай Гоголь",
            "fonvizin": "Денис Фонвизин"
        }
        return {"name": names.get(writer_key, "Unknown")}


def get_main_keyboard():
    """Main menu"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚 Выбрать писателя")],
            [KeyboardButton(text="💬 Диалог с писателем")],
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
        "📚 **LITERARY GENIUS** — ваш гид по миру мировой литературы\n\n"
        "Я — эксперт по творчеству великих писателей всех времён и народов. Помогу вам исследовать жизнь, произведения и философию величайших авторов.\n\n"
        "📖 **Что я знаю:**\n"
        "🎭 Творчество писателей со всего мира\n"
        "📚 Литературные направления и движения\n"
        "✍️ Биографии, основные произведения и их влияние\n"
        "🌍 Эпоху и культурные события, вдохновившие авторов\n"
        "💭 Философские идеи и литературный стиль каждого автора\n\n"
        "✨ Выберите режим работы, чтобы начать!",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )


@dp.message(F.text == "📚 Выбрать писателя")
async def cmd_select_writer(message: types.Message):
    """Select writer for expert mode"""
    user_id = message.from_user.id
    user_modes[user_id] = "expert"
    await message.answer("📖 Какого писателя вы хотите изучить?", reply_markup=get_writers_keyboard())


@dp.message(F.text == "💬 Диалог с писателем")
async def cmd_dialogue_mode(message: types.Message):
    """Select writer for dialogue mode"""
    user_id = message.from_user.id
    user_modes[user_id] = "dialogue"
    await message.answer("🎭 Выберите писателя для беседы:\n\n_Вы сможете беседовать с ним как с живым человеком, узнавать о его жизни, творчестве и философии!_", reply_markup=get_writers_keyboard())


@dp.message(F.text.in_([name for name in writers.values()]))
async def set_writer(message: types.Message):
    """Set writer"""
    from comprehensive_knowledge import get_portrait
    
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
        mode = user_modes.get(user_id, "expert")
        
        # Send mode-specific greeting
        if mode == "dialogue":
            await message.answer(
                f"🎭 **Добро пожаловать в беседу с {author_data['name']}!**\n\n"
                f"_Вы разговариваете с самим писателем. Спрашивайте его о его жизни, творчестве, философии и мировоззрении._\n\n"
                f"💭 Что вы хотите узнать о нём?",
                reply_markup=get_main_keyboard(),
                parse_mode="Markdown"
            )
        else:
            await message.answer(
                f"🎨 **Режим: Эксперт**\n\n"
                f"Теперь я буду вести диалог через призму его творчества и мировоззрения. Спрашивайте о нём и о других авторах!\n\n"
                f"_Я готов к вашим вопросам о литературе, философии и искусстве._",
                reply_markup=get_main_keyboard(),
                parse_mode="Markdown"
            )


@dp.message(F.text == "🎲 Случайный писатель")
async def random_writer(message: types.Message):
    """Random writer"""
    from comprehensive_knowledge import knowledge
    
    user_id = message.from_user.id
    key = random.choice(list(knowledge.writers_db.keys()))
    user_sessions[user_id] = key
    clear_memory(user_id)
    
    data = load_author_data(key)
    writer_name = data.get('name', 'Unknown')
    
    # Send greeting WITH WRITER NAME
    await message.answer(
        f"🎲 Волшебство выбрало этого писателя!\n\n"
        f"📖 **{writer_name}**\n\n"
        f"Отличный выбор! Давайте погрузимся в его творческий мир.\n\n"
        f"_Спрашивайте о его произведениях, жизни и влиянии на литературу._",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )


@dp.message(F.text == "❓ О боте")
async def about_bot(message: types.Message):
    """About bot"""
    await message.answer(
        "📚 **LITERARY GENIUS - Ваш гид по миру литературы**\n\n"
        "Я являюсь экспертом в области мировой литературы с глубоким знанием писателей всех эпох и стилей.\n\n"
        "💫 **Что я могу предложить:**\n"
        "✦ Полную биографию любого писателя\n"
        "✦ Анализ их произведений и тем\n"
        "✦ Исторический и культурный контекст\n"
        "✦ Влияние на развитие литературы\n"
        "✦ Сравнение между авторами\n"
        "✦ Глубокое понимание литературных направлений\n\n"
        "🌟 **Особенность:**\n"
        "Я выражу свои знания через призму мировоззрения выбранного вами писателя, с его уникальным стилем и философией.\n\n"
        "📝 Начните с выбора писателя - и мы совершим путешествие в мир литературы!",
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()
    )


@dp.message()
async def try_direct_writer_input(message: types.Message):
    """Try to find writer by direct name input"""
    from comprehensive_knowledge import knowledge, get_portrait
    
    user_id = message.from_user.id
    text = message.text.strip()
    
    # ✅ FIRST: Check if user already has active session with a writer
    # If yes - continue conversation with the SAME writer
    if user_id in user_sessions and user_sessions[user_id]:
        await handle_message(message)
        return
    
    # ✅ ONLY IF NO ACTIVE SESSION: Try to find writer by direct name input
    found_writer = knowledge.search_by_name(text)
    
    if found_writer:
        # Writer found by direct input - start new conversation with this writer
        user_sessions[user_id] = found_writer
        clear_memory(user_id)
        mode = user_modes.get(user_id, "expert")
        
        author_data = load_author_data(found_writer)
        
        # Process the question through Claude
        await message.bot.send_chat_action(message.chat.id, "typing")
        await handle_message(message)
        return
    
    # No active session found and writer name not recognized
    await message.answer(
        "📖 Пожалуйста, сначала выберите писателя, нажав на кнопку «📚 Выбрать писателя» или напишите его имя напрямую.\n\n"
        "_Он станет основой нашей беседы о литературе и искусстве._",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )


async def handle_message(message: types.Message):
    """Main handler - can answer about any writer"""
    user_id = message.from_user.id
    text = message.text
    
    # Try to find if user is asking about a specific writer
    mentioned_writer = knowledge.search_by_name(text)
    
    # Use mentioned writer if found, otherwise use selected writer
    if mentioned_writer:
        writer_key = mentioned_writer
    else:
        writer_key = user_sessions[user_id]
    
    author_data = load_author_data(writer_key)
    
    await message.bot.send_chat_action(message.chat.id, "typing")
    
    try:
        logger.info(f"Generating response for user {user_id} about {author_data.get('name', 'Unknown')}")
        mode = user_modes.get(user_id, "expert")
        
        # Always use expert mode for general questions about any writer
        # Only use dialogue mode if explicitly selected and asking about selected writer
        if mode == "dialogue" and writer_key == user_sessions[user_id]:
            response = await generate_dialogue_response(user_id, text, author_data)
        else:
            response = await generate_response(user_id, text, author_data)
        
        if not response:
            response = "Извините, мне нужна минутка для размышления. Повторите вопрос."
        
        await message.answer(f"{response}", parse_mode="Markdown")
        logger.info(f"Sent response to {user_id}")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await message.answer("💭 Извините, мне нужна минутка для размышления. Пожалуйста, повторите ваш вопрос.")


async def main():
    """Start bot"""
    print("🚀 Запуск LITERARY GENIUS...")
    print(f"📚 Режим: Мировая литература и великие писатели")
    print("=" * 50)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())


# ШАГ 5: Новые команды для расширенной функциональности
@dp.message(F.text.in_(["📊 Статистика", "ℹ️ Информация", "🔍 Поиск"]))
async def enhanced_mode_selector(message: types.Message):
    """Выбор расширенного режима"""
    user_id = message.from_user.id
    
    if message.text == "🔍 Поиск":
        await message.answer(
            "🔍 **Режим поиска**\n\n"
            "Введите имя писателя, которого хотите найти:",
            reply_markup=get_main_keyboard(),
            parse_mode="Markdown"
        )
    elif message.text == "📊 Статистика":
        from enhanced_commands import list_all_writers
        result = list_all_writers()
        await message.answer(result, parse_mode="Markdown", reply_markup=get_main_keyboard())
    elif message.text == "ℹ️ Информация":
        from enhanced_commands import get_preload_status
        result = get_preload_status()
        await message.answer(result, parse_mode="Markdown", reply_markup=get_main_keyboard())


# Добавить новую кнопку в главное меню
def get_main_keyboard_enhanced():
    """Главное меню с расширенными опциями"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚 Выбрать писателя"), KeyboardButton(text="🔍 Поиск")],
            [KeyboardButton(text="💬 Диалог с писателем"), KeyboardButton(text="🎲 Случайный писатель")],
            [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="ℹ️ Информация")],
            [KeyboardButton(text="❓ О боте")]
        ],
        resize_keyboard=True
    )
