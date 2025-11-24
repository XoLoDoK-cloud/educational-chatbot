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
            [KeyboardButton(text="❓ Ask Question"), KeyboardButton(text="🆘 Help")],
            [KeyboardButton(text="🧹 Clear Memory"), KeyboardButton(text="ℹ️ About")]
        ],
        resize_keyboard=True
    )


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Start command"""
    user_id = message.from_user.id
    clear_user_memory(user_id)
    
    await message.answer(
        "🧠 **LITERARY CHATGPT**\n\n"
        "Welcome to Literary ChatGPT - an autonomous neural network specialized in world literature.\n\n"
        "I can answer ANY question about:\n"
        "📚 Writers and authors\n"
        "📖 Books and works\n"
        "🎓 Literary genres and movements\n"
        "📜 Literary history\n"
        "💭 Literary analysis and interpretation\n\n"
        "Just ask your question in natural language and I'll provide a comprehensive answer with Wikipedia context.\n\n"
        "Get started by clicking '❓ Ask Question' or type your question directly!",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )


@dp.message(Command("help"))
@dp.message(F.text == "🆘 Help")
async def cmd_help(message: types.Message):
    """Help command"""
    help_text = """
🤖 **HOW TO USE LITERARY CHATGPT**

**What I can do:**
✓ Answer questions about any writer, book, or literary movement
✓ Provide deep analysis of literary works
✓ Compare authors and their styles
✓ Discuss literary history and evolution
✓ Remember the context of your entire conversation

**Example questions:**
• Tell me about Dostoevsky's literary style
• What is romanticism in literature?
• Analyze the novel "War and Peace"
• What's the difference between realism and modernism?
• Who are the most influential writers of the 20th century?

**How I work:**
1. You ask a question about literature
2. I search Wikipedia for relevant information
3. I use Claude AI to generate a comprehensive answer
4. I remember your entire conversation

**Features:**
🧠 ChatGPT-style responses
📚 Wikipedia integration for accuracy
💭 Context memory (remembers your conversation)
🌍 Knowledge of world literature

Just type any question and get started!
"""
    await message.answer(help_text, parse_mode="Markdown", reply_markup=get_main_keyboard())


@dp.message(Command("about"))
@dp.message(F.text == "ℹ️ About")
async def cmd_about(message: types.Message):
    """About command"""
    about_text = """
📚 **ABOUT LITERARY CHATGPT**

**Architecture:**
• Neural Network: Claude 3.5 Sonnet (OpenRouter)
• Knowledge Base: Wikipedia + World Literature Database
• Memory: Conversation history (30 messages per user)
• Interface: Telegram Bot (@LiteraryCompanionBot)

**Technology:**
• Python 3 + Aiogram (async Telegram framework)
• Aiohttp (async Wikipedia requests)
• Real-time data fetching and caching

**Capabilities:**
✓ Autonomous responses (no predefined answers)
✓ Deep literary analysis
✓ Multi-topic support
✓ Context awareness

**Language:** English/Russian

This is a fully autonomous neural network designed to be your expert guide to world literature.
"""
    await message.answer(about_text, parse_mode="Markdown", reply_markup=get_main_keyboard())


@dp.message(Command("clear"))
@dp.message(F.text == "🧹 Clear Memory")
async def cmd_clear(message: types.Message):
    """Clear conversation history"""
    user_id = message.from_user.id
    clear_user_memory(user_id)
    await message.answer(
        "✅ Conversation memory cleared. You can start fresh with new questions.",
        reply_markup=get_main_keyboard()
    )


@dp.message(F.text == "❓ Ask Question")
async def cmd_ask(message: types.Message):
    """Prompt for question"""
    await message.answer(
        "📝 Go ahead and ask your question about literature!",
        reply_markup=get_main_keyboard()
    )


@dp.message()
async def handle_text(message: types.Message):
    """Handle text messages - main Q&A handler"""
    user_id = message.from_user.id
    question = message.text
    
    # Show typing indicator
    await bot.send_chat_action(message.chat.id, "typing")
    
    try:
        logger.info(f"User {user_id} asked: {question[:100]}")
        
        # Get response from neural network
        response = await answer_literature_question(user_id, question)
        
        if not response:
            response = "I need a moment to think about that. Please try again."
        
        # Send response
        await message.answer(response, parse_mode="Markdown", reply_markup=get_main_keyboard())
        logger.info(f"Response sent to user {user_id}")
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await message.answer(
            "⚠️ Something went wrong. Please try again.",
            reply_markup=get_main_keyboard()
        )


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
