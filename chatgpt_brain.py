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

def analyze_question_type(question: str) -> Dict:
    """Analyze question to determine what type of information is needed"""
    q_lower = question.lower()
    
    analysis = {
        'type': None,
        'is_about_first': False,
        'is_biographical': False,
        'is_comparative': False,
        'is_about_themes': False,
        'is_about_quotes': False,
        'is_about_style': False,
    }
    
    # Detect question type
    first_keywords = ['первое', 'first', 'début', 'начал', 'earliest', 'самое раннее']
    bio_keywords = ['когда', 'when', 'где', 'where', 'жил', 'lived', 'рожд', 'born', 'умер', 'died', 'биография', 'biography']
    compare_keywords = ['отличие', 'difference', 'сравн', 'compare', 'разница', 'vs', 'versus', 'или', 'or']
    theme_keywords = ['тема', 'theme', 'смысл', 'meaning', 'о чём', 'what about', 'главное', 'главная идея', 'main idea']
    quote_keywords = ['цитата', 'quote', 'сказал', 'said', 'слова', 'words', 'высказ', 'фраза', 'phrase']
    style_keywords = ['стиль', 'style', 'техника', 'technique', 'писал', 'wrote', 'манера', 'manner', 'жанр', 'genre']
    
    if any(kw in q_lower for kw in first_keywords):
        analysis['is_about_first'] = True
    if any(kw in q_lower for kw in bio_keywords):
        analysis['is_biographical'] = True
    if any(kw in q_lower for kw in compare_keywords):
        analysis['is_comparative'] = True
    if any(kw in q_lower for kw in theme_keywords):
        analysis['is_about_themes'] = True
    if any(kw in q_lower for kw in quote_keywords):
        analysis['is_about_quotes'] = True
    if any(kw in q_lower for kw in style_keywords):
        analysis['is_about_style'] = True
    
    return analysis

def generate_offline_answer(question: str) -> str:
    """Generate accurate answer from local knowledge base with neural network quality"""
    try:
        logger.info(f"🧠 ANALYZING QUESTION: {question[:80]}")
        
        # Analyze question to determine information needs
        analysis = analyze_question_type(question)
        logger.info(f"🔍 ANALYSIS: {analysis}")
        
        # Get all relevant information
        writer = get_writer_knowledge(question)
        work = get_work_knowledge(question)
        movement = get_movement_knowledge(question)
        
        answer_parts = []
        found_info = False
        
        # ============ WRITER-FOCUSED ANSWERS ============
        if writer:
            found_info = True
            logger.info(f"📖 Found writer: {writer['name']}")
            
            # Main header
            answer_parts.append(f"📖 **{writer['name']}**\n")
            answer_parts.append(f"Period: {writer['period']}\n")
            
            # Biographical information if requested
            if analysis['is_biographical']:
                answer_parts.append(f"\n🏛️ **BIOGRAPHICAL CONTEXT**\n")
                answer_parts.append(f"Active in: {writer['period']}\n")
                answer_parts.append(f"Key genres: {', '.join(writer.get('genres', ['Literary Fiction']))}\n")
                answer_parts.append(f"Influence: {writer.get('influence', 'Major contributor to literature')}\n")
            
            # Works section
            answer_parts.append(f"\n📚 **MAJOR WORKS**\n")
            if analysis['is_about_first'] and writer.get('works'):
                answer_parts.append(f"First work: **{writer['works'][0]}**\n")
                answer_parts.append(f"Other notable works: {', '.join(writer['works'][1:4])}\n")
            else:
                # Show top works with description
                all_works = writer.get('works', [])[:8]
                answer_parts.append(f"Notable works: {', '.join(all_works)}\n")
            
            # Themes and style if requested
            if analysis['is_about_themes'] or analysis['is_about_style']:
                answer_parts.append(f"\n🎭 **LITERARY STYLE & THEMES**\n")
                answer_parts.append(f"Genres: {', '.join(writer.get('genres', ['Literary Fiction']))}\n")
                answer_parts.append(f"Literary influence: {writer.get('influence', 'Significant contribution to literature')}\n")
            
            # Quotes section
            if analysis['is_about_quotes'] or not analysis['is_about_first']:
                answer_parts.append(f"\n💭 **NOTABLE QUOTES**\n")
                if writer.get('quotes'):
                    for i, quote in enumerate(writer.get('quotes', [])[:3], 1):
                        answer_parts.append(f"{i}. \"{quote}\"\n")
        
        # ============ WORK-FOCUSED ANSWERS ============
        if work:
            found_info = True
            logger.info(f"📚 Found work: {work['title']}")
            
            if not writer:  # If not already added from writer
                answer_parts.append(f"📚 **{work['title']}**\n")
            else:
                answer_parts.append(f"\n### Detailed Analysis: {work['title']}\n")
            
            answer_parts.append(f"Author: {work['author']}\n")
            answer_parts.append(f"Year: {work['year']}\n")
            answer_parts.append(f"Genre: {work.get('genre', 'Literary Fiction')}\n")
            
            # Themes
            if work.get('themes'):
                answer_parts.append(f"\n**Central Themes:**\n")
                for theme in work['themes']:
                    answer_parts.append(f"• {theme}\n")
            
            # Quotes from work
            if work.get('quotes'):
                answer_parts.append(f"\n**Famous Quotes from the work:**\n")
                for quote in work.get('quotes', [])[:2]:
                    answer_parts.append(f"\"{quote}\"\n")
        
        # ============ MOVEMENT-FOCUSED ANSWERS ============
        if movement:
            found_info = True
            logger.info(f"🎨 Found movement: {movement['name']}")
            
            answer_parts.append(f"\n🎨 **LITERARY MOVEMENT: {movement['name'].upper()}**\n")
            answer_parts.append(f"Period: {movement['period']}\n")
            
            answer_parts.append(f"\n**Characteristics:**\n")
            for char in movement.get('characteristics', [])[:5]:
                answer_parts.append(f"• {char}\n")
            
            if movement.get('key_authors'):
                answer_parts.append(f"\n**Key Authors:** {', '.join(movement['key_authors'])}\n")
        
        if found_info:
            answer = "".join(answer_parts)
            answer += "\n━━━━━━━━━━━━━━━━━━━━━━━━\n✨ *Ответ от AI Neural Network*"
            logger.info(f"✅ Offline answer generated ({len(answer)} chars)")
            return answer
        else:
            logger.warning(f"❌ No information found for: {question}")
            return (
                "🤔 К сожалению, я не смог найти информацию по вашему запросу.\n\n"
                "💡 Попробуйте:\n"
                "• Переформулировать вопрос\n"
                "• Спросить о известном авторе (Пушкин, Толстой, Достоевский)\n"
                "• Спросить о популярном произведении (Война и мир, Crime and Punishment)\n"
                "• Спросить о литературном движении (Романтизм, Реализм)"
            )
    
    except Exception as e:
        logger.error(f"❌ Error generating offline answer: {e}", exc_info=True)
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
