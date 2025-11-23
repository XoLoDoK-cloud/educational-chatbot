import logging
import asyncio
import json
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from ai_openrouter import generate_literary_response
from internet_search import internet_searcher
from flask import Flask
from threading import Thread
import sys

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

print("🚀 Запуск литературного бота...")
if BOT_TOKEN:
    print(f"🔑 Токен: {BOT_TOKEN[:10]}...")
else:
    print("⚠️ ОШИБКА: BOT_TOKEN не установлен!")

# Flask для keep-alive
app = Flask('')

@app.route('/')
def home():
    return "🤖 Literary Bot is ALIVE!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run, daemon=True)
    t.start()

# Инициализация бота
try:
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    logger.info("✅ Бот инициализирован")
except Exception as e:
    logger.error(f"❌ Ошибка инициализации бота: {e}")
    exit(1)

# Храним выбор писателя для каждого пользователя
user_sessions = {}

# Клавиатуры
def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚 Выбрать писателя")],
            [KeyboardButton(text="🔄 Сменить писателя"), KeyboardButton(text="💫 Случайный писатель")]
        ],
        resize_keyboard=True
    )

def get_writers_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🖋️ Пушкин"), KeyboardButton(text="🎭 Достоевский")],
            [KeyboardButton(text="📖 Толстой"), KeyboardButton(text="✒️ Чехов")],
            [KeyboardButton(text="🔮 Гоголь")]
        ],
        resize_keyboard=True
    )

# Загрузка данных автора
def load_author_data(writer):
    """Загружает данные автора из JSON файла"""
    try:
        author_file = f"writers/{writer}.json"
        if not os.path.exists(author_file):
            logger.error(f"Файл не найден: {author_file}")
            return None
            
        with open(author_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"✅ Загружен автор: {data['name']}")
        return data
        
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки автора {writer}: {e}")
        return None

# Команды бота
@dp.message(Command("start"))
async def start_command(message: types.Message):
    """Обработчик команды /start"""
    user_sessions[message.from_user.id] = None
    
    welcome_text = """
🌟 *Добро пожаловать в литературную нейросеть!* 🌟

Я генерирую ответы в стиле великих русских писателей.

*Доступные писатели:*
• 🖋️ Александр Пушкин
• 🎭 Фёдор Достоевский  
• 📖 Лев Толстой
• ✒️ Антон Чехов
• 🔮 Николай Гоголь

Выберите писателя и задавайте вопросы!
    """
    
    await message.answer(welcome_text, parse_mode="Markdown", reply_markup=get_main_keyboard())
    logger.info(f"👤 Пользователь {message.from_user.id} запустил бота")

@dp.message(Command("writers"))
async def show_writers(message: types.Message):
    """Показывает список писателей"""
    await message.answer("🎭 Выберите писателя:", reply_markup=get_writers_keyboard())

# Обработчики кнопок
@dp.message(lambda message: message.text == "📚 Выбрать писателя")
async def select_writer_button(message: types.Message):
    await show_writers(message)

@dp.message(lambda message: message.text == "🔄 Сменить писателя")
async def change_writer(message: types.Message):
    user_sessions[message.from_user.id] = None
    await message.answer("🔄 Писатель сброшен. Выберите нового:", reply_markup=get_writers_keyboard())

@dp.message(lambda message: message.text in ["🖋️ Пушкин", "🎭 Достоевский", "📖 Толстой", "✒️ Чехов", "🔮 Гоголь"])
async def handle_writer_selection(message: types.Message):
    """Обработчик выбора писателя"""
    writer_map = {
         "🖋️ Пушкин": "pushkin",
        "🎭 Достоевский": "dostoevsky", 
        "📖 Толстой": "tolstoy",
        "✒️ Чехов": "chekhov",
        "🔮 Гоголь": "gogol"
    }
    
    writer_key = message.text
    writer = writer_map[writer_key]
    user_id = message.from_user.id
    
    # Загружаем данные автора
    author_data = load_author_data(writer)
    if not author_data:
        await message.answer("❌ Ошибка загрузки данных автора")
        return
    
    user_sessions[user_id] = writer
    
    response_text = f"""
🎭 *{author_data['name']}*

🧠 Нейросеть активирована в стиле {author_data['name']}!

{author_data['opening_phrase']}

Задавайте вопросы - я отвечу в стиле автора!
    """
    
    await message.answer(response_text, parse_mode="Markdown", reply_markup=get_main_keyboard())
    logger.info(f"👤 Пользователь {user_id} выбрал {author_data['name']}")

@dp.message(lambda message: message.text == "💫 Случайный писатель")
async def random_writer(message: types.Message):
    """Выбор случайного писателя"""
    import random
    writers = ["pushkin", "dostoevsky", "tolstoy", "chekhov", "gogol"]
    selected_writer = random.choice(writers)
    
    author_data = load_author_data(selected_writer)
    if not author_data:
        await message.answer("❌ Ошибка загрузки данных автора")
        return
    
    user_sessions[message.from_user.id] = selected_writer
    
    response_text = f"""
🎲 *Случайный выбор: {author_data['name']}!*

🧠 Нейросеть генерирует ответы в стиле {author_data['name']}

{author_data['opening_phrase']}

Задавайте вопросы!
    """
    
    await message.answer(response_text, parse_mode="Markdown", reply_markup=get_main_keyboard())
    logger.info(f"👤 Случайный выбор: {author_data['name']}")

# Основной обработчик сообщений
@dp.message()
async def handle_message(message: types.Message):
    """Обработчик всех сообщений"""
    user_id = message.from_user.id
    text = message.text
    
    logger.info(f"📨 Сообщение от {user_id}: {text}")
    
    # Игнорируем служебные кнопки
    if text in ["📚 Выбрать писателя", "🔄 Сменить писателя", "💫 Случайный писатель"]:
        return
    
    # Проверяем выбран ли писатель
    if user_id not in user_sessions or not user_sessions[user_id]:
        await message.answer(
            "🎭 Сначала выберите писателя!\n\nНажмите «📚 Выбрать писателя»",
            reply_markup=get_main_keyboard()
        )
        return
    
    writer = user_sessions[user_id]
    
    # Загружаем данные автора
    author_data = load_author_data(writer)
    if not author_data:
        await message.answer("❌ Ошибка загрузки данных автора")
        return
    
    # Показываем статус "печатает"
    await message.bot.send_chat_action(message.chat.id, "typing")
    
    try:
        logger.info(f"🧠 Генерация ответа в стиле {author_data['name']}")
        
        # Генерируем ответ через нейросеть
        ai_response = await generate_literary_response(text, author_data)
        
        if not ai_response or len(ai_response.strip()) == 0:
            ai_response = "Извините, не удалось сгенерировать ответ. Попробуйте еще раз."
        
        logger.info(f"✅ Ответ сгенерирован: {ai_response[:100]}...")
        
        # Проверяем, нужен ли интернет-поиск
        should_search = internet_searcher.should_search_internet(ai_response, text)
        logger.info(f"📊 Проверка интернет-поиска: {should_search} (вопрос: '{text[:50]}...')")
        
        if should_search:
            logger.info(f"🔍 Запускаю интернет-поиск для: {text}")
            await message.bot.send_chat_action(message.chat.id, "typing")
            
            # Ищем в интернете с общим таймаутом
            try:
                search_results = await asyncio.wait_for(
                    internet_searcher.search_online(text, max_results=3),
                    timeout=20.0  # Максимум 20 секунд на весь поиск
                )
                
                if search_results:
                    # Генерируем ответ на основе найденной информации
                    ai_response = internet_searcher.generate_internet_answer(
                        text, 
                        search_results, 
                        writer
                    )
                    logger.info(f"✅ Ответ сгенерирован с интернет-поиском")
                else:
                    logger.info(f"⚠️ Интернет-поиск не вернул результатов, отправляю базовый ответ")
            except asyncio.TimeoutError:
                logger.warning(f"⏰ Таймаут интернет-поиска, отправляю базовый ответ")
                # Отправляем базовый ответ, если поиск слишком долгий
        # Отправляем ответ
        writer_names = {
            "pushkin": "Пушкин",
            "dostoevsky": "Достоевский",
            "tolstoy": "Толстой", 
            "chekhov": "Чехов",
            "gogol": "Гоголь"
        }
        
        response = f"*{writer_names.get(writer, 'Автор')}:* {ai_response}"
        await message.answer(response, parse_mode="Markdown")
        logger.info(f"✅ Ответ отправлен пользователю {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка генерации ответа: {e}")
        await message.answer("⚠️ Произошла ошибка при генерации ответа. Попробуйте еще раз.")

# Главная функция
async def force_reset_bot():
    """Принудительный сброс всех подключений"""
    print("🔄 ЗАПУСК FORCE_RESET_BOT...")
    
    try:
        from aiogram.client.session.aiohttp import AiohttpSession
        
        print("🔄 Создание временной сессии...")
        session = AiohttpSession()
        temp_bot = Bot(token=BOT_TOKEN, session=session)
        
        # Многократный сброс
        for i in range(3):
            print(f"🔄 Сброс попытка {i+1}/3")
            await temp_bot.delete_webhook(drop_pending_updates=True)
            await asyncio.sleep(2)
        
        print("🔄 Закрытие сессии...")
        await session.close()
        print("✅ Принудительный сброс завершен")
        
    except Exception as e:
        print(f"❌ Ошибка сброса: {e}")

async def main():
    """Основная функция запуска бота"""
    print("🔧 ЗАПУСК MAIN ФУНКЦИИ...")
    
    try:
        print("🔄 Шаг 1: Принудительный сброс...")
        await force_reset_bot()
        
        print("⏳ Шаг 2: Ожидание 5 секунд...")
        await asyncio.sleep(5)
        
        print("🔧 Шаг 3: Запуск keep-alive...")
        keep_alive()
        
        print("🧠 Шаг 4: Запуск polling...")
        logger.info("🧠 Запуск литературной нейросети...")
        print("🎭 Бот готов к работе! Найдите нового бота в Telegram")
        
        # Запускаем polling с таймаутом
        await dp.start_polling(bot, allowed_updates=["message"])
        
    except Exception as e:
        print(f"💥 КРИТИЧЕСКАЯ ОШИБКА в main: {e}")
        logger.error(f"❌ Критическая ошибка: {e}")
    finally:
        print("🔧 Завершение работы...")
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())
