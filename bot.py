import logging
import asyncio
import json
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from ai_openrouter import generate_literary_response
from flask import Flask
from threading import Thread
import sys
print("🚀 Python путь:", sys.executable)
print("🚀 Токен первые 10 символов:", BOT_TOKEN[:10])

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Flask для keep-alive
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Храним выбор писателя для каждого пользователя
user_sessions = {}

# Красивая клавиатура
def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚 Выбрать писателя"), KeyboardButton(text="🔄 Сменить писателя")],
            [KeyboardButton(text="🌟 Рекомендации"), KeyboardButton(text="💫 Случайный писатель")]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_writers_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🖋️ Пушкин"), KeyboardButton(text="🎭 Достоевский")],
            [KeyboardButton(text="📖 Толстой"), KeyboardButton(text="✒️ Чехов")],
            [KeyboardButton(text="🔮 Гоголь"), KeyboardButton(text="⬅️ Назад")]
        ],
        resize_keyboard=True
    )
    return keyboard

@dp.message()
async def handle_message(message: types.Message):
    print("🔥 ОТЛАДКА: ФУНКЦИЯ handle_message ВЫЗВАНА!")
    
    user_id = message.from_user.id
    text = message.text
    
    print(f"🎯 Получено сообщение: '{text}'")
    print(f"👤 Пользователь: {user_id}")
    print(f"📊 Текущая сессия: {user_sessions.get(user_id)}")
    
    # 🔥 СУПЕР-ПРОВЕРКА ПАПКИ WRITERS ПРИ ЛЮБОМ СООБЩЕНИИ
    print("🔍 ПРОВЕРКА ПАПКИ WRITERS:")
    current_dir = os.getcwd()
    print(f"📂 Текущая директория: {current_dir}")
    
    writers_dir_exists = os.path.exists("writers")
    print(f"📁 Папка writers существует: {writers_dir_exists}")
    
    if writers_dir_exists:
        all_files = os.listdir("writers")
        print(f"📂 Все файлы в папке writers: {all_files}")
        
        # Проверим каждый файл
        for file in all_files:
            full_path = f"writers/{file}"
            print(f"  📄 {file} -> exists: {os.path.exists(full_path)}")
    
    # Игнорируем служебные кнопки
    if text in ["📚 Выбрать писателя", "🔄 Сменить писателя", "🌟 Рекомендации", "💫 Случайный писатель", "⬅️ Назад"]:
        print("🔕 Игнорируем служебную кнопку")
        return
    
    # Остальной код функции остается без изменений...
    # Если уже выбран писатель - генерируем ответ нейросетью
    if user_id in user_sessions and user_sessions[user_id]:
        writer = user_sessions[user_id]
        # ... остальной код
        
        print(f"🔍 Шаг 1: Загрузка данных автора '{writer}'...")
        
        # Показываем статус "печатает"
        await message.bot.send_chat_action(message.chat.id, "typing")
        
        try:
            # Загружаем данные автора
            author_file = f"writers/{writer}.json"
            print(f"📁 Проверяем файл: {author_file}")
            print(f"📁 Файл существует: {os.path.exists(author_file)}")
            
            # 🔥 ДОПОЛНИТЕЛЬНАЯ ПРОВЕРКА - список всех файлов в папке
            print(f"📂 Содержимое папки writers/: {os.listdir('writers')}")
            
            if os.path.exists(author_file):
                with open(author_file, 'r', encoding='utf-8') as f:
                    author_data = json.load(f)
                
                print(f"✅ Данные автора загружены: {author_data['name']}")
                print(f"🔍 Шаг 2: Вызов нейросети...")
                
                # Генерируем ответ через нейросеть
                ai_response = await generate_literary_response(text, author_data)
                
                print(f"✅ Ответ сгенерирован!")
                print(f"📝 Текст ответа: {ai_response[:200]}...")
                
                # Отправляем сгенерированный ответ
                writer_names = {
                    "пушкин": "Пушкин",
                    "достоевский": "Достоевский",
                    "толстой": "Толстой", 
                    "чехов": "Чехов",
                    "гоголь": "Гоголь"
                }
                
                print(f"🔍 Шаг 3: Отправка сообщения...")
                await message.answer(
                    f"*{writer_names[writer]}:* {ai_response}",
                    parse_mode="Markdown"
                )
                print(f"✅ Сообщение отправлено!")
                
            else:
                print(f"❌ Файл автора не найден: {author_file}")
                # 🔥 Показываем какие файлы вообще есть
                all_files = os.listdir('writers')
                print(f"📂 Доступные файлы: {all_files}")
                await message.answer("❌ Файл автора не найден")
                
        except Exception as e:
            print(f"💥 КРИТИЧЕСКАЯ ОШИБКА: {e}")
            import traceback
            print(f"📋 Полный трейсбэк: {traceback.format_exc()}")
            await message.answer(f"⚠️ Произошла ошибка: {str(e)}")
        
        return
    
    # Выбор писателя по тексту
    writers = ["пушкин", "достоевский", "толстой", "чехов", "гоголь"]
    for writer in writers:
        if writer in text.lower():
            user_sessions[user_id] = writer
            writer_names = {
                "пушкин": "Александр Сергеевич Пушкин",
                "достоевский": "Фёдор Михайлович Достоевский",
                "толстой": "Лев Николаевич Толстой",
                "чехов": "Антон Павлович Чехов", 
                "гоголь": "Николай Васильевич Гоголь"
            }
            
            await message.answer(
                f"🎭 *{writer_names[writer]}*\n\n"
                f"🧠 Нейросеть активирована!\n\n"
                f"Задавайте вопросы - AI сгенерирует уникальные ответы в стиле {writer_names[writer]}!",
                parse_mode="Markdown",
                reply_markup=get_main_keyboard()
            )
            return
    
    # Если писатель не выбран
    await message.answer(
        "🎭 Сначала выберите писателя!\n\n"
        "Нажмите «📚 Выбрать писателя» или напишите имя автора.",
        reply_markup=get_main_keyboard()
    )

async def main():
    # ПРИНУДИТЕЛЬНЫЙ СБРОС
    await bot.delete_webhook(drop_pending_updates=True)
    print("✅ Полный сброс выполнен!")
    
    # Ждем 5 секунд
    await asyncio.sleep(5)
    
    # Запускаем keep-alive
    keep_alive()
    
    print("🧠 Литературная нейросеть запущена!")
    print("🎭 Готова генерировать ответы в стиле великих писателей!")
    
    await dp.start_polling(bot, allowed_updates=["message", "callback_query"])

if __name__ == "__main__":
    asyncio.run(main())
