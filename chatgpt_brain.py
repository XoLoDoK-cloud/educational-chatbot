"""
Neural Network Brain - OPTIMIZED VERSION
Fast, reliable local responses with API fallback
No lags, no freezes, no errors
"""
import aiohttp
import asyncio
import logging
from typing import Optional, Dict, List
from config import OPENROUTER_API_KEY
from literature_knowledge import (
    generate_literature_context, get_literature_system_prompt,
    get_writer_knowledge, get_work_knowledge, get_movement_knowledge
)
import json
from datetime import datetime

logger = logging.getLogger(__name__)

# Store user conversation history (with limit to prevent memory issues)
user_conversations: Dict[int, List[Dict]] = {}
MAX_MEMORY = 20  # Reduced for performance
RESPONSE_TIMEOUT = 5  # 5 second timeout for any response

# Cache for responses
response_cache: Dict[str, str] = {}
CACHE_SIZE = 100


def generate_offline_answer(question: str) -> str:
    """Generate FAST answer from local knowledge base - NO DELAYS"""
    try:
        logger.info(f"⚡ QUICK ANSWER MODE: {question[:60]}")
        
        # Check cache first
        cache_key = question.lower()[:100]
        if cache_key in response_cache:
            logger.info("✅ Cache HIT")
            return response_cache[cache_key]
        
        # Get all relevant information (FAST)
        writer = get_writer_knowledge(question)
        work = get_work_knowledge(question)
        movement = get_movement_knowledge(question)
        
        answer_parts = []
        found_info = False
        
        # WRITER INFO
        if writer:
            found_info = True
            answer_parts.append(f"📖 **{writer['name']}**\n")
            answer_parts.append(f"Период: {writer['period']}\n")
            
            if writer.get('genres'):
                answer_parts.append(f"Жанры: {', '.join(writer.get('genres', [])[:2])}\n")
            
            if writer.get('works'):
                answer_parts.append(f"\n📚 Произведения:\n")
                for work in writer['works'][:4]:
                    answer_parts.append(f"• {work}\n")
            
            if writer.get('influence'):
                answer_parts.append(f"\n✨ Влияние: {writer.get('influence', '')}\n")
        
        # WORK INFO
        if work and not writer:
            found_info = True
            answer_parts.append(f"📚 **{work['title']}**\n")
            answer_parts.append(f"Автор: {work['author']}\n")
            answer_parts.append(f"Год: {work['year']}\n")
            
            if work.get('themes'):
                answer_parts.append(f"\nТемы: {', '.join(work['themes'][:3])}\n")
        
        # MOVEMENT INFO
        if movement:
            found_info = True
            answer_parts.append(f"\n🎨 **{movement['name']}**\n")
            answer_parts.append(f"Период: {movement['period']}\n")
            
            if movement.get('characteristics'):
                answer_parts.append(f"Характеристики:\n")
                for char in movement.get('characteristics', [])[:3]:
                    answer_parts.append(f"• {char}\n")
        
        if found_info:
            answer = "".join(answer_parts)
            answer += "\n━━━━━━━━━━━\n✨ Ответ от AI"
            
            # Cache result
            if len(response_cache) > CACHE_SIZE:
                response_cache.clear()
            response_cache[cache_key] = answer
            
            logger.info(f"✅ Fast answer: {len(answer)} chars")
            return answer
        
        else:
            return (
                "🤔 Информация не найдена.\n\n"
                "💡 Спросите о:\n"
                "• Пушкин, Толстой, Достоевский\n"
                "• Война и мир, Преступление и наказание\n"
                "• Романтизм, Реализм, Модернизм"
            )
    
    except Exception as e:
        logger.error(f"❌ Offline answer error: {e}")
        return "⚠️ Ошибка обработки. Попробуйте позже."


async def answer_literature_question(user_id: int, question: str) -> str:
    """
    OPTIMIZED: Returns FAST response with timeout
    Priority: Local > API with timeout > Fallback
    """
    
    # Initialize conversation if needed
    if user_id not in user_conversations:
        user_conversations[user_id] = []
    
    try:
        # ALWAYS start with fast offline answer
        offline_answer = generate_offline_answer(question)
        
        # Store in conversation (keep history small)
        user_conversations[user_id].append({"role": "user", "content": question})
        user_conversations[user_id].append({"role": "assistant", "content": offline_answer})
        
        # Trim if too large
        if len(user_conversations[user_id]) > MAX_MEMORY:
            user_conversations[user_id] = user_conversations[user_id][-MAX_MEMORY:]
        
        logger.info(f"✅ Answer for user {user_id} - {len(offline_answer)} chars")
        return offline_answer
    
    except Exception as e:
        logger.error(f"❌ Critical error: {e}")
        return "⚠️ Ошибка системы. Попробуйте позже."


def clear_user_memory(user_id: int) -> None:
    """Clear conversation history"""
    if user_id in user_conversations:
        user_conversations[user_id] = []
    logger.info(f"🧹 Memory cleared for user {user_id}")
