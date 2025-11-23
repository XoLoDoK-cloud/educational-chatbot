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
            "gogol": "Николай Гоголь"
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
        "📚 **Добро пожаловать в LITERARY GENIUS**\n\n"
        "Я - ваш персональный искусствовед мировой литературы. Известный эксперт по творчеству великих писателей во всех их проявлениях.\n\n"
        "🌟 Мои знания охватывают:\n"
        "• Величайших писателей мировой истории\n"
        "• Все литературные школы и течения\n"
        "• Биографии, произведения и влияние авторов\n"
        "🌍 Эпоху и культурные события, вдохновившие авторов\n"
        "• Философию, стиль и идеи каждого мастера\n\n"
        "✨ Выберите писателя, и мы погрузимся в мир литературы!",
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
                f"🎨 Вы выбрали: **{author_data['name']}**\n\n"
                f"Теперь я буду вести диалог через призму его творчества и мировоззрения. Спрашивайте о нём и о других авторах!\n\n"
                f"_Я готов к вашим вопросам о литературе, философии и искусстве._",
                reply_markup=get_main_keyboard(),
                parse_mode="Markdown"
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
        f"🎲 Волшебство выбрало: **{data['name']}**\n\n"
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
async def handle_message(message: types.Message):
    """Main handler"""
    user_id = message.from_user.id
    text = message.text
    
    if user_id not in user_sessions or not user_sessions[user_id]:
        await message.answer(
            "📖 Пожалуйста, сначала выберите писателя, нажав на кнопку «📚 Выбрать писателя».\n\n"
            "_Он станет основой нашей беседы о литературе и искусстве._",
            reply_markup=get_main_keyboard(),
            parse_mode="Markdown"
        )
        return
    
    writer_key = user_sessions[user_id]
    author_data = load_author_data(writer_key)
    
    await message.bot.send_chat_action(message.chat.id, "typing")
    
    try:
        logger.info(f"Generating response for user {user_id}")
        mode = user_modes.get(user_id, "expert")
        
        if mode == "dialogue":
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
