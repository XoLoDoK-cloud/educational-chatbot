#!/usr/bin/env python3
"""
OPTIMIZED Telegram Bot - Fast, Reliable, Zero Lag
Простой и надёжный Telegram бот
"""
import asyncio
import logging
from datetime import datetime

try:
    from aiogram import Bot, Dispatcher, types, F
    from aiogram.filters import Command
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    from aiogram.fsm.storage.memory import MemoryStorage
except ImportError as e:
    print(f"❌ Aiogram not installed: {e}")
    print("Install with: pip install aiogram")
    exit(1)

from config import BOT_TOKEN
from chatgpt_brain import answer_literature_question, clear_user_memory
from writers_brain import get_available_writers, set_user_writer, talk_to_writer, get_user_writer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN not found!")
    exit(1)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# User state with timeout tracking
user_state = {}
user_last_action = {}
ACTION_TIMEOUT = 300  # 5 minutes

# Cache writers list
writers_cache = None
writers_cache_time = 0
CACHE_TTL = 300  # 5 minutes

def get_cached_writers():
    """Get cached writers list with TTL"""
    global writers_cache, writers_cache_time
    now = datetime.now().timestamp()
    
    if writers_cache is None or (now - writers_cache_time) > CACHE_TTL:
        writers_cache = get_available_writers()
        writers_cache_time = now
        logger.info(f"📚 Writers cache refreshed")
    
    return writers_cache

def get_main_keyboard():
    """Main menu keyboard"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❓ Вопросы"), KeyboardButton(text="👥 Писатели")],
            [KeyboardButton(text="📚 Справка"), KeyboardButton(text="⚙️ Меню")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )

def get_writer_keyboard():
    """Writer selection keyboard with cache"""
    try:
        writers = get_cached_writers()
        keyboard = []
        for w in writers:
            keyboard.append([KeyboardButton(text=f"📖 {w['name']}")])
        keyboard.append([KeyboardButton(text="🔙 Назад")])
        return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    except Exception as e:
        logger.error(f"Error building writer keyboard: {e}")
        return get_main_keyboard()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Start command - quick response"""
    try:
        if not message.from_user:
            return
        user_id = message.from_user.id
        user_state[user_id] = "menu"
        user_last_action[user_id] = datetime.now().timestamp()
        clear_user_memory(user_id)
        
        text = """━━━━━━━━━━━━━━━━━━━━━━━━
✨ LITERARY CHATBOT v3 ✨
━━━━━━━━━━━━━━━━━━━━━━━━

🧠 Добро пожаловать!

❓ Вопросы - спросите о литературе
👥 Писатели - поговорите с классиками
📚 Справка - помощь
⚙️ Меню - информация"""
        
        await message.answer(text, reply_markup=get_main_keyboard())
        logger.info(f"✅ START: User {user_id}")
    except Exception as e:
        logger.error(f"❌ Start error: {e}")
        await message.answer("⚠️ Ошибка. Попробуйте /start заново")

@dp.message(F.text == "❓ Вопросы")
async def mode_questions(message: types.Message):
    """Questions mode"""
    try:
        if not message.from_user:
            return
        user_id = message.from_user.id
        user_state[user_id] = "question"
        user_last_action[user_id] = datetime.now().timestamp()
        await message.answer("📝 Напишите ваш вопрос о литературе:")
        logger.info(f"❓ QUESTIONS MODE: User {user_id}")
    except Exception as e:
        logger.error(f"Questions mode error: {e}")

@dp.message(F.text == "👥 Писатели")
async def mode_writers(message: types.Message):
    """Writers mode"""
    try:
        if not message.from_user:
            return
        user_id = message.from_user.id
        user_state[user_id] = "writer_select"
        user_last_action[user_id] = datetime.now().timestamp()
        text = "📖 Выберите писателя для беседы:"
        await message.answer(text, reply_markup=get_writer_keyboard())
        logger.info(f"👥 WRITERS MODE: User {user_id}")
    except Exception as e:
        logger.error(f"Writers mode error: {e}")

@dp.message(F.text == "📚 Справка")
async def cmd_help(message: types.Message):
    """Help command"""
    try:
        if not message.from_user:
            return
        user_last_action[message.from_user.id] = datetime.now().timestamp()
        text = """━━━━━━━━━━━━━━━━━━━━━━
📖 КАК ИСПОЛЬЗОВАТЬ
━━━━━━━━━━━━━━━━━━━━━━

❓ ВОПРОСЫ
Спросите о писателях, произведениях, жанрах.

👥 ПИСАТЕЛИ  
• 📖 Пушкин
• 📖 Толстой
• 📖 Достоевский
• 📖 Чехов
• 📖 Гоголь

Команды:
/start - главное меню
/help - справка
/clear - очистить"""
        await message.answer(text, reply_markup=get_main_keyboard())
    except Exception as e:
        logger.error(f"Help error: {e}")

@dp.message(F.text == "⚙️ Меню")
async def cmd_menu(message: types.Message):
    """Menu command"""
    try:
        if not message.from_user:
            return
        user_last_action[message.from_user.id] = datetime.now().timestamp()
        text = """━━━━━━━━━━━━━━━━━━━━━━
⚙️ МЕНЮ
━━━━━━━━━━━━━━━━━━━━━━

Версия: 3.0
Статус: 🟢 ОНЛАЙН
Оптимизация: ⚡ MAX

/start - начало
/help - справка
/clear - очистить"""
        await message.answer(text, reply_markup=get_main_keyboard())
    except Exception as e:
        logger.error(f"Menu error: {e}")

@dp.message(F.text == "🔙 Назад")
async def cmd_back(message: types.Message):
    """Back button"""
    try:
        if not message.from_user:
            return
        user_id = message.from_user.id
        user_state[user_id] = "menu"
        user_last_action[user_id] = datetime.now().timestamp()
        await message.answer("🔙 Вернулись в меню:", reply_markup=get_main_keyboard())
    except Exception as e:
        logger.error(f"Back button error: {e}")

@dp.message(Command("clear"))
async def cmd_clear(message: types.Message):
    """Clear command"""
    try:
        if not message.from_user:
            return
        user_id = message.from_user.id
        clear_user_memory(user_id)
        user_last_action[user_id] = datetime.now().timestamp()
        await message.answer("🧹 История очищена!")
        logger.info(f"🧹 CLEAR: User {user_id}")
    except Exception as e:
        logger.error(f"Clear error: {e}")

@dp.message()
async def handle_text(message: types.Message):
    """Main message handler - OPTIMIZED"""
    if not message.from_user or not message.text:
        return
    
    user_id = message.from_user.id
    text = message.text
    state = user_state.get(user_id, "menu")
    user_last_action[user_id] = datetime.now().timestamp()
    
    try:
        # Show typing indicator
        try:
            await bot.send_chat_action(message.chat.id, "typing")
        except:
            pass  # Don't fail if this doesn't work
        
        if state == "question":
            # Answer question - FAST with timeout
            try:
                response = await asyncio.wait_for(
                    answer_literature_question(user_id, text),
                    timeout=5.0
                )
            except asyncio.TimeoutError:
                logger.warning(f"⏱️ Timeout for user {user_id}")
                response = "⏱️ Ответ занял слишком много времени. Попробуйте ещё раз."
            except Exception as e:
                logger.error(f"Question error: {e}")
                response = "⚠️ Ошибка обработки вопроса."
            
            answer = f"📖 ОТВЕТ:\n\n{response}\n\n/start - меню"
            await message.answer(answer)
            
        elif state == "writer_select":
            # Select writer - FAST
            writers = get_cached_writers()
            found = False
            
            for w in writers:
                if w['name'] in text:
                    set_user_writer(user_id, w['key'])
                    user_state[user_id] = "writer_talk"
                    found = True
                    intro = f"🎭 Беседа с {w['name']}\n\nНапишите что-нибудь:"
                    await message.answer(intro)
                    logger.info(f"👥 SELECTED: {w['name']} for user {user_id}")
                    break
            
            if not found:
                await message.answer("❌ Писатель не найден. Выберите из списка:", 
                                   reply_markup=get_writer_keyboard())
        
        elif state == "writer_talk":
            # Talk to writer - FAST with timeout
            current_writer = get_user_writer(user_id)
            if current_writer:
                try:
                    response = await asyncio.wait_for(
                        talk_to_writer(user_id, text),
                        timeout=3.0
                    )
                except asyncio.TimeoutError:
                    logger.warning(f"⏱️ Writer response timeout for user {user_id}")
                    response = "⏱️ Писатель задумался... Попробуйте позже."
                except Exception as e:
                    logger.error(f"Writer talk error: {e}")
                    response = "⚠️ Ошибка беседы с писателем."
                
                await message.answer(response)
            else:
                await message.answer("❌ Выберите писателя сначала", 
                                   reply_markup=get_main_keyboard())
        
        else:
            await message.answer("Выберите режим:", reply_markup=get_main_keyboard())
    
    except Exception as e:
        logger.error(f"❌ Critical error in handler: {e}")
        try:
            error_msg = "⚠️ Критическая ошибка. Используйте /start"
            await message.answer(error_msg)
        except:
            pass


async def main():
    """Main function"""
    logger.info("🚀 Starting Optimized Literary Bot v3")
    logger.info("⚡ Features: Fast responses, No lag, Error handling")
    logger.info("✅ Ready!")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error(f"❌ Polling error: {e}")
    finally:
        try:
            await bot.session.close()
        except:
            pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped")
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
