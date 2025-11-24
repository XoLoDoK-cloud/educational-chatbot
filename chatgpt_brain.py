"""
Neural Network Brain - Claude 3.5 Sonnet Integration
Integrates with OpenRouter API for autonomous literary analysis
Enhanced with comprehensive literature knowledge base
Fallback: Local knowledge base when API is unavailable
"""
import aiohttp
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

# Store user conversation history
user_conversations: Dict[int, List[Dict]] = {}
MAX_MEMORY = 30  # Maximum messages to remember per user

def generate_offline_answer(question: str) -> str:
    """Generate answer from local knowledge base when API is unavailable"""
    try:
        # Check if question is about first work
        q_lower = question.lower()
        is_first_work_question = any(word in q_lower for word in ['первое', 'first', 'début', 'начал'])
        
        # Get context from knowledge base
        writer = get_writer_knowledge(question)
        work = get_work_knowledge(question)
        movement = get_movement_knowledge(question)
        
        answer_parts = []
        
        if writer:
            answer_parts.append(f"📖 **{writer['name']}** ({writer['period']})\n")
            
            if is_first_work_question and writer.get('works'):
                answer_parts.append(f"First major work: **{writer['works'][0]}**\n")
                answer_parts.append(f"Other notable works: {', '.join(writer['works'][1:4])}\n")
            else:
                answer_parts.append(f"Major works: {', '.join(writer['works'][:5])}\n")
            
            if writer.get('quotes'):
                answer_parts.append(f"Famous quote: \"{writer['quotes'][0]}\"\n")
        
        if work:
            answer_parts.append(f"📚 **{work['title']}** by {work['author']} ({work['year']})\n")
            answer_parts.append(f"Themes: {', '.join(work['themes'])}\n")
            if work.get('quotes'):
                answer_parts.append(f"Quote: \"{work['quotes'][0]}\"\n")
        
        if movement:
            answer_parts.append(f"🎨 **{movement['name']}** ({movement['period']})\n")
            answer_parts.append(f"Characteristics: {', '.join(movement['characteristics'][:3])}\n")
        
        if answer_parts:
            answer = "".join(answer_parts)
            answer += "\n\n💡 *Ответ из локальной базы знаний (API недоступен)*"
            logger.info(f"Offline answer generated for question: {question[:50]}")
            return answer
        else:
            return "📚 Я не нашел информацию в своей базе знаний. Попробуйте переформулировать вопрос."
    
    except Exception as e:
        logger.error(f"Error generating offline answer: {e}")
        return "⚠️ Не удалось обработать вопрос. Попробуйте позже."

async def get_wikipedia_context(query: str) -> str:
    """Fetch context from Wikipedia using aiohttp"""
    try:
        async with aiohttp.ClientSession() as session:
            params = {
                'action': 'query',
                'format': 'json',
                'titles': query,
                'prop': 'extracts',
                'exintro': 1,
                'explaintext': 1,
                'redirects': 1
            }
            
            async with session.get('https://en.wikipedia.org/w/api.php', params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    pages = data.get('query', {}).get('pages', {})
                    for page_id, page_data in pages.items():
                        if page_id != '-1':
                            extract = page_data.get('extract', '')
                            if extract:
                                return extract[:1000]  # Limit to 1000 chars
    except Exception as e:
        logger.warning(f"Wikipedia fetch error: {e}")
    
    return ""

async def answer_literature_question(user_id: int, question: str) -> str:
    """
    Main neural network function - uses Claude 3.5 Sonnet for answering
    literature questions with Wikipedia context
    """
    
    if not OPENROUTER_API_KEY:
        logger.error("OPENROUTER_API_KEY not set")
        return "⚠️ API configuration error. Please contact administrator."
    
    # Initialize user conversation if needed
    if user_id not in user_conversations:
        user_conversations[user_id] = []
    
    try:
        # Get Wikipedia context for better answers
        wikipedia_context = await get_wikipedia_context(question)
        
        # Build conversation history for context
        conversation_history = user_conversations[user_id][-10:]  # Last 10 messages for context
        
        # Build messages for Claude
        messages = []
        
        # Add conversation history
        for msg in conversation_history:
            messages.append(msg)
        
        # Add current question with Wikipedia context
        context_text = ""
        if wikipedia_context:
            context_text = f"\n\n📚 Wikipedia Context:\n{wikipedia_context}"
        
        user_message = f"{question}{context_text}"
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Call Claude API via OpenRouter
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://replit.com",
                "X-Title": "LiteraryBot"
            }
            
            # Generate enhanced context from literature knowledge base
            literature_context = generate_literature_context(question)
            
            payload = {
                "model": "claude-3.5-sonnet",
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1500,
                "system": get_literature_system_prompt()
            }
            
            async with session.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload
            ) as resp:
                if resp.status == 200:
                    response_data = await resp.json()
                    assistant_response = response_data.get('choices', [{}])[0].get('message', {}).get('content', '')
                    
                    # Store conversation in memory
                    user_conversations[user_id].append({"role": "user", "content": question})
                    user_conversations[user_id].append({"role": "assistant", "content": assistant_response})
                    
                    # Trim memory if too long
                    if len(user_conversations[user_id]) > MAX_MEMORY:
                        user_conversations[user_id] = user_conversations[user_id][-MAX_MEMORY:]
                    
                    logger.info(f"Response generated for user {user_id}")
                    return assistant_response
                else:
                    error_data = await resp.text()
                    logger.error(f"OpenRouter API error {resp.status}: {error_data}")
                    logger.info("Falling back to offline knowledge base")
                    # Use offline knowledge base as fallback
                    offline_answer = generate_offline_answer(question)
                    
                    # Store in memory
                    user_conversations[user_id].append({"role": "user", "content": question})
                    user_conversations[user_id].append({"role": "assistant", "content": offline_answer})
                    
                    if len(user_conversations[user_id]) > MAX_MEMORY:
                        user_conversations[user_id] = user_conversations[user_id][-MAX_MEMORY:]
                    
                    return offline_answer
    
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        logger.info("Falling back to offline knowledge base due to exception")
        # Use offline knowledge base as fallback
        offline_answer = generate_offline_answer(question)
        
        # Store in memory
        user_conversations[user_id].append({"role": "user", "content": question})
        user_conversations[user_id].append({"role": "assistant", "content": offline_answer})
        
        if len(user_conversations[user_id]) > MAX_MEMORY:
            user_conversations[user_id] = user_conversations[user_id][-MAX_MEMORY:]
        
        return offline_answer

def clear_user_memory(user_id: int) -> None:
    """Clear conversation history for a user"""
    if user_id in user_conversations:
        user_conversations[user_id] = []
    logger.info(f"Memory cleared for user {user_id}")
