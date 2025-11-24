"""
Enhanced Telegram Bot with Neural Network Learning
Features user feedback collection for continuous improvement
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from advanced_chatgpt_brain import advanced_answer_literature_question, rate_response
from writers_brain import (
    get_available_writers, set_user_writer, get_user_writer, 
    talk_to_writer, get_writer_info, clear_writer_conversation
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot with error handling
if not BOT_TOKEN:
    logger.warning("⚠️ BOT_TOKEN not found. Telegram bot will not work.")
    bot = None
    dp = None
else:
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

# Design elements
SEPARATOR = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
SUBSEP = "─────────────────────────────"

# Track last response for feedback
user_last_response = {}

def get_main_keyboard():
    """Main menu with feedback option"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❓ Questions"), KeyboardButton(text="👥 Writers")],
            [KeyboardButton(text="📚 Help"), KeyboardButton(text="⭐ Feedback")],
            [KeyboardButton(text="⚙️ Menu")],
        ],
        resize_keyboard=True
    )

def get_feedback_keyboard():
    """Rating keyboard"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⭐", callback_data="rate_1"),
             InlineKeyboardButton(text="⭐⭐", callback_data="rate_2"),
             InlineKeyboardButton(text="⭐⭐⭐", callback_data="rate_3")],
            [InlineKeyboardButton(text="⭐⭐⭐⭐", callback_data="rate_4"),
             InlineKeyboardButton(text="⭐⭐⭐⭐⭐", callback_data="rate_5")]
        ]
    )

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Start command"""
    welcome = f"""
{SEPARATOR}
    ✨ ADVANCED LITERARY NEURAL NETWORK ✨
{SEPARATOR}

🧠 AI Brain with Real-Time Learning!

Features:
✓ Web-based knowledge (Wikipedia integration)
✓ Learns from your feedback
✓ Improves with every conversation
✓ Chat with Russian literary classics
✓ Advanced literature analysis

{SUBSEP}
Choose an option or ask a question!
"""
    
    await message.answer(welcome, reply_markup=get_main_keyboard())

@dp.message(F.text == "⭐ Feedback")
async def cmd_feedback(message: types.Message):
    """Request feedback"""
    user_id = message.from_user.id
    
    if user_id in user_last_response:
        feedback_msg = f"""
{SEPARATOR}
📊 RATE THE LAST RESPONSE
{SEPARATOR}

Your feedback helps us improve!
Please rate the response quality:
"""
        await message.answer(feedback_msg, reply_markup=get_feedback_keyboard())
    else:
        await message.answer("Please ask a question first, then rate the response!")

@dp.callback_query(F.data.startswith("rate_"))
async def process_rating(callback_query: types.CallbackQuery):
    """Process rating"""
    user_id = callback_query.from_user.id
    rating = int(callback_query.data.split("_")[1])
    
    if user_id in user_last_response:
        last_data = user_last_response[user_id]
        
        # Record feedback
        await rate_response(
            user_id,
            last_data["question"],
            last_data["response"],
            rating
        )
        
        await callback_query.answer(f"Thanks! {rating}⭐ recorded", show_alert=False)
        await callback_query.message.answer(
            f"✅ Feedback recorded!\n\n"
            f"With your {rating}⭐ rating, our neural network learns to improve!",
            reply_markup=get_main_keyboard()
        )
    else:
        await callback_query.answer("No recent response to rate", show_alert=True)

@dp.message(F.text == "❓ Questions")
async def cmd_questions(message: types.Message):
    """Ask questions mode"""
    await message.answer(
        f"{SEPARATOR}\n"
        f"💬 QUESTION MODE\n"
        f"{SEPARATOR}\n\n"
        f"Ask your literature question!\n"
        f"After receiving an answer, you can rate it with ⭐ Feedback button."
    )

@dp.message()
async def handle_text(message: types.Message):
    """Handle all text messages"""
    user_id = message.from_user.id
    question = message.text
    
    logger.info(f"📨 Message from {user_id}: {question[:50]}")
    
    try:
        await bot.send_chat_action(message.chat.id, "typing")
        
        # Get advanced response with learning
        response = await advanced_answer_literature_question(user_id, question)
        
        # Store for feedback
        user_last_response[user_id] = {
            "question": question,
            "response": response
        }
        
        # Format response
        formatted_response = f"""
{SUBSEP}
📖 RESPONSE
{SUBSEP}

{response}

{SUBSEP}
💡 Tip: Rate this response with ⭐ Feedback to help us learn!
"""
        
        await message.answer(formatted_response, reply_markup=get_main_keyboard())
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await message.answer(
            f"❌ An error occurred. Please try again.\n\nError: {str(e)[:100]}",
            reply_markup=get_main_keyboard()
        )

async def main():
    """Main function"""
    if not bot or not dp:
        logger.error("❌ Bot not initialized. Set BOT_TOKEN environment variable.")
        return
    
    logger.info("🚀 Starting Enhanced Literary Neural Network Bot...")
    logger.info("🧠 Learning Mode: ENABLED")
    logger.info("🌐 Web Access: ENABLED")
    logger.info("📊 Feedback Collection: ENABLED")
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    if bot and dp:
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
    else:
        logger.error("Cannot start bot without BOT_TOKEN")
