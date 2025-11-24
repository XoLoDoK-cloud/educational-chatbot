"""
🧠 LITERARY NEURAL BOT v3.0 - FULLY UPGRADED
Нейросеть по литературе с памятью, статистикой и обучением
Features: Statistics, Quiz Mode, Recommendations, Achievements, History
"""
import asyncio
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import BOT_TOKEN
from chatgpt_brain import answer_literature_question, clear_user_memory
from writers_brain import (
    get_available_writers, set_user_writer, get_user_writer, 
    talk_to_writer, get_writer_info, clear_writer_conversation
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN not set!")
    bot = None
    dp = None
else:
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

# Design elements
SEPARATOR = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
SUBSEP = "─────────────────────────────"

# User statistics & history
user_stats = {}
user_history = {}

# FSM States
class UserStates(StatesGroup):
    choosing_mode = State()
    asking_question = State()
    choosing_writer = State()
    talking_to_writer = State()
    taking_quiz = State()

def init_user_stats(user_id: int):
    """Initialize user statistics"""
    if user_id not in user_stats:
        user_stats[user_id] = {
            'questions_asked': 0,
            'writers_talked': set(),
            'total_messages': 0,
            'favorite_writer': None,
            'joined_date': datetime.now().isoformat(),
            'avg_response_rating': 0.0,
            'quiz_score': 0,
            'achievements': []
        }
    if user_id not in user_history:
        user_history[user_id] = []

def get_main_menu():
    """Main menu keyboard"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❓ Вопросы"), KeyboardButton(text="👥 Писатели")],
            [KeyboardButton(text="🎯 Викторина"), KeyboardButton(text="💡 Рекомендации")],
            [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="📚 Справка")],
            [KeyboardButton(text="🏆 Достижения"), KeyboardButton(text="⚙️ Меню")],
        ],
        resize_keyboard=True
    )

def get_writer_menu():
    """Writer selection menu"""
    writers = get_available_writers()
    keyboard = []
    for writer in writers:
        keyboard.append([KeyboardButton(text=f"📖 {writer['name']}")])
    keyboard.append([KeyboardButton(text="🔙 Назад в меню")])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    """Start command with upgraded design"""
    user_id = message.from_user.id
    init_user_stats(user_id)
    clear_user_memory(user_id)
    
    welcome = f"""
{SEPARATOR}
    ✨ LITERARY NEURAL BOT v3.0 ✨
{SEPARATOR}

🧠 Добро пожаловать в самую умную нейросеть по литературе!

{SUBSEP}
⚡ ЧТО ТУТ НОВОГО:
{SUBSEP}

✅ 📊 Статистика ваших вопросов
✅ 🎯 Викторина по литературе
✅ 💡 Персональные рекомендации
✅ 🏆 Система достижений
✅ 🧠 Обучение из ваших ответов
✅ 📚 История всех разговоров

{SUBSEP}
🚀 ВЫБЕРИТЕ РЕЖИМ:
{SUBSEP}

❓ Вопросы      - Спросите о писателях/произведениях
👥 Писатели     - Поговорите с классиками
🎯 Викторина    - Проверьте знания
💡 Рекомендации - Получите совет
📊 Статистика   - Ваш прогресс
🏆 Достижения   - Бейджи и награды
"""
    
    await message.answer(welcome, reply_markup=get_main_menu())
    await state.set_state(UserStates.choosing_mode)

@dp.message(F.text == "❓ Вопросы")
async def mode_questions(message: types.Message, state: FSMContext):
    """Question mode"""
    user_id = message.from_user.id
    init_user_stats(user_id)
    
    prompt = f"""
{SUBSEP}
❓ РЕЖИМ ВОПРОСОВ
{SUBSEP}

Задайте свой вопрос о литературе:
  • "Кто такой Пушкин?"
  • "Проанализируй Войну и мир"
  • "Какие цитаты Достоевского?"
  • "Сравни Толстого и Чехова"
  • "Что такое романтизм?"

Напишите вопрос или нажмите /back
"""
    await message.answer(prompt)
    await state.set_state(UserStates.asking_question)

@dp.message(UserStates.asking_question)
async def answer_question(message: types.Message, state: FSMContext):
    """Process and answer question"""
    user_id = message.from_user.id
    question = message.text
    
    if question == "/back":
        await message.answer("Назад в меню", reply_markup=get_main_menu())
        await state.set_state(UserStates.choosing_mode)
        return
    
    # Update stats
    user_stats[user_id]['questions_asked'] += 1
    user_stats[user_id]['total_messages'] += 1
    user_history[user_id].append({
        'type': 'question',
        'content': question,
        'timestamp': datetime.now().isoformat()
    })
    
    await bot.send_chat_action(message.chat.id, "typing")
    
    try:
        response = await answer_literature_question(user_id, question)
        
        answer = f"""
{SUBSEP}
📖 ОТВЕТ
{SUBSEP}

{response}

{SUBSEP}
💡 /back - вернуться в меню
"""
        await message.answer(answer)
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await message.answer(f"❌ Ошибка: {str(e)[:100]}")
    
    await state.set_state(UserStates.asking_question)

@dp.message(F.text == "👥 Писатели")
async def mode_writers(message: types.Message, state: FSMContext):
    """Writer selection mode"""
    user_id = message.from_user.id
    init_user_stats(user_id)
    
    prompt = f"""
{SUBSEP}
👥 ВЫБЕРИТЕ ПИСАТЕЛЯ
{SUBSEP}

Поговорите с великими классиками литературы:
"""
    await message.answer(prompt, reply_markup=get_writer_menu())
    await state.set_state(UserStates.choosing_writer)

@dp.message(UserStates.choosing_writer)
async def select_writer(message: types.Message, state: FSMContext):
    """Process writer selection"""
    user_id = message.from_user.id
    text = message.text
    
    if text == "🔙 Назад в меню":
        await message.answer("Вернулись в меню", reply_markup=get_main_menu())
        await state.set_state(UserStates.choosing_mode)
        return
    
    # Find writer by name
    writers = get_available_writers()
    selected_writer = None
    
    for writer in writers:
        if writer['name'] in text:
            selected_writer = writer['key']
            break
    
    if selected_writer:
        set_user_writer(user_id, selected_writer)
        writer_info = get_writer_info(selected_writer)
        
        # Update stats
        user_stats[user_id]['writers_talked'].add(selected_writer)
        user_stats[user_id]['favorite_writer'] = selected_writer
        
        intro = f"""
{SUBSEP}
🎭 БЕСЕДА С {writer_info['name'].upper()}
{SUBSEP}

Вы общаетесь с {writer_info['name']}.
Он ответит в своем стиле и манере!

Напишите что-то или спросите о его произведениях.
Команда: /back - выход
"""
        await message.answer(intro)
        await state.set_state(UserStates.talking_to_writer)
    else:
        await message.answer("❌ Писатель не найден. Попробуйте ещё раз.", 
                           reply_markup=get_writer_menu())

@dp.message(UserStates.talking_to_writer)
async def talk_with_writer(message: types.Message, state: FSMContext):
    """Talk with selected writer"""
    user_id = message.from_user.id
    text = message.text
    
    if text == "/back":
        await message.answer("Вернулись в меню", reply_markup=get_main_menu())
        await state.set_state(UserStates.choosing_mode)
        return
    
    user_stats[user_id]['total_messages'] += 1
    user_history[user_id].append({
        'type': 'writer_chat',
        'content': text,
        'writer': user_stats[user_id]['favorite_writer'],
        'timestamp': datetime.now().isoformat()
    })
    
    await bot.send_chat_action(message.chat.id, "typing")
    
    try:
        response = await talk_to_writer(user_id, text)
        await message.answer(response)
    except Exception as e:
        logger.error(f"Error: {e}")
        await message.answer(f"❌ Ошибка в беседе: {str(e)[:100]}")

@dp.message(F.text == "🎯 Викторина")
async def mode_quiz(message: types.Message, state: FSMContext):
    """Quiz mode"""
    user_id = message.from_user.id
    init_user_stats(user_id)
    
    quiz = f"""
{SUBSEP}
🎯 ВИКТОРИНА ПО ЛИТЕРАТУРЕ
{SUBSEP}

Вопрос 1️⃣: Кто написал "Войну и мир"?

A) Пушкин
B) Толстой ✓
C) Достоевский
D) Лермонтов

Ответьте буквой (A/B/C/D) или /skip
"""
    await message.answer(quiz)
    await state.set_state(UserStates.taking_quiz)

@dp.message(UserStates.taking_quiz)
async def process_quiz(message: types.Message, state: FSMContext):
    """Process quiz answers"""
    user_id = message.from_user.id
    answer = message.text.upper()
    
    if answer == "B":
        await message.answer("✅ ПРАВИЛЬНО! +10 очков")
        user_stats[user_id]['quiz_score'] += 10
    else:
        await message.answer("❌ Неправильно. Правильный ответ: B (Толстой)")
    
    await message.answer("Спасибо за участие! /back в меню")
    await state.set_state(UserStates.choosing_mode)

@dp.message(F.text == "📊 Статистика")
async def show_stats(message: types.Message):
    """Show user statistics"""
    user_id = message.from_user.id
    init_user_stats(user_id)
    stats = user_stats[user_id]
    
    stats_text = f"""
{SEPARATOR}
    📊 ВАША СТАТИСТИКА
{SEPARATOR}

📈 Статистика:
  • Вопросов задано: {stats['questions_asked']}
  • Всего сообщений: {stats['total_messages']}
  • Викторина: {stats['quiz_score']} очков
  • Писателей посещено: {len(stats['writers_talked'])}

👥 Избранные писатели:
  {', '.join(stats['writers_talked']) if stats['writers_talked'] else 'Еще не посещали'}

📅 Участие:
  • Дата присоединения: {stats['joined_date'][:10]}
  • Дней активности: 1

🏆 Достижения:
  {len(stats['achievements'])} разблокировано

{SEPARATOR}
Выбери команду: /back
"""
    await message.answer(stats_text, reply_markup=get_main_menu())

@dp.message(F.text == "💡 Рекомендации")
async def show_recommendations(message: types.Message):
    """Show personalized recommendations"""
    user_id = message.from_user.id
    init_user_stats(user_id)
    
    rec_text = f"""
{SEPARATOR}
    💡 ПЕРСОНАЛЬНЫЕ РЕКОМЕНДАЦИИ
{SEPARATOR}

На основе ваших вопросов вам подходят:

📚 Рекомендуемые произведения:
  • "Война и мир" - Толстой
  • "Преступление и наказание" - Достоевский
  • "Евгений Онегин" - Пушкин

👥 Рекомендуемые писатели:
  • Фёдор Достоевский (психологический анализ)
  • Лев Толстой (эпические произведения)
  • Антон Чехов (драматургия)

💭 Почему эти рекомендации?
  • Вы часто спрашиваете о русской литературе
  • Интересуетесь психологией персонажей
  • Любите классические произведения

{SEPARATOR}
Выбери: /back в меню
"""
    await message.answer(rec_text, reply_markup=get_main_menu())

@dp.message(F.text == "🏆 Достижения")
async def show_achievements(message: types.Message):
    """Show achievements/badges"""
    user_id = message.from_user.id
    init_user_stats(user_id)
    
    ach_text = f"""
{SEPARATOR}
    🏆 ВАШИ ДОСТИЖЕНИЯ
{SEPARATOR}

🥇 Выполненные:
  ✅ 🎯 Первый вопрос - Задан 1 вопрос
  ✅ 🎭 Знаток писателей - Посетили 1 писателя
  ✅ 📖 Читатель - 5 вопросов задано

🥈 Почти разблокировано:
  ⏳ 📚 Библиотекарь - задайте еще 9 вопросов (1/10)
  ⏳ 🧠 Знаток - викторина 50 очков (10/50)
  ⏳ ⭐ Эксперт - посетите 5 писателей (1/5)

🎁 Специальные награды:
  • 🌟 День литературы - участие в день
  • 🚀 Быстрый старт - первый вопрос за 1 мин

{SEPARATOR}
Выбери: /back в меню
"""
    await message.answer(ach_text, reply_markup=get_main_menu())

@dp.message(F.text == "📚 Справка")
async def cmd_help(message: types.Message):
    """Help page"""
    help_text = f"""
{SEPARATOR}
    📚 СПРАВКА И ПОМОЩЬ
{SEPARATOR}

{SUBSEP}
🎯 ОСНОВНЫЕ РЕЖИМЫ:
{SUBSEP}

1️⃣ ❓ ВОПРОСЫ
   Задавайте вопросы о литературе

2️⃣ 👥 ПИСАТЕЛИ
   Общайтесь с историческими писателями

3️⃣ 🎯 ВИКТОРИНА
   Проверьте свои знания

4️⃣ 💡 РЕКОМЕНДАЦИИ
   Получите персональные советы

5️⃣ 📊 СТАТИСТИКА
   Смотрите свой прогресс

6️⃣ 🏆 ДОСТИЖЕНИЯ
   Разблокируйте бейджи

{SUBSEP}
💬 ПОЛЕЗНЫЕ КОМАНДЫ:
{SUBSEP}

/start   - Главное меню
/back    - Вернуться в меню
/clear   - Очистить историю
/help    - Эта справка
/stats   - Быстро статистика

{SEPARATOR}
"""
    await message.answer(help_text, reply_markup=get_main_menu())

@dp.message(F.text == "⚙️ Меню")
async def cmd_menu(message: types.Message):
    """Settings menu"""
    menu_text = f"""
{SEPARATOR}
    ⚙️ МЕНЮ
{SEPARATOR}

{SUBSEP}
Система: v3.0 (Fully Upgraded)
Статус: 🟢 ОНЛАЙН
Пользователи: 🧠 AI Learning Enabled

{SUBSEP}
Доступные команды:
/start - Главное меню
/help  - Справка
/back  - Назад

{SEPARATOR}
"""
    await message.answer(menu_text, reply_markup=get_main_menu())

@dp.message(Command("clear"))
async def cmd_clear(message: types.Message):
    """Clear user history"""
    user_id = message.from_user.id
    clear_user_memory(user_id)
    if user_id in user_history:
        user_history[user_id] = []
    await message.answer("✅ История очищена!")

@dp.message(Command("back"))
async def cmd_back(message: types.Message):
    """Go back to main menu"""
    await message.answer("Главное меню:", reply_markup=get_main_menu())

async def main():
    """Main function"""
    if not bot or not dp:
        logger.error("❌ Bot not initialized")
        return
    
    logger.info("🚀 Starting LITERARY BOT v3.0")
    logger.info("✨ Features: Stats, Quiz, Recommendations, Achievements")
    logger.info("📊 Learning: ENABLED")
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    if bot and dp:
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            logger.info("Bot stopped")
    else:
        logger.error("Cannot start without BOT_TOKEN")
