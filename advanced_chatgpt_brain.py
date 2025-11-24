"""
Advanced Neural Network Brain - With Web Learning Capabilities
Enhanced with real-time internet research and continuous learning
"""
import asyncio
import aiohttp
import logging
from typing import Optional, Dict, List
from config import OPENROUTER_API_KEY
from literature_knowledge import (
    generate_literature_context, get_literature_system_prompt,
    get_writer_knowledge, get_work_knowledge, get_movement_knowledge
)
from neural_trainer import record_user_feedback, optimize_response, get_training_metrics
from web_scraper import LiteratureWebScraper
import json

logger = logging.getLogger(__name__)

# User conversations with extended history
user_conversations: Dict[int, List[Dict]] = {}
MAX_MEMORY = 50  # Extended memory

# Web scraper instance
scraper = LiteratureWebScraper()

# Cache for fetched data
knowledge_cache: Dict[str, Dict] = {}
CACHE_TTL = 3600  # 1 hour cache


async def fetch_enhanced_literature_context(query: str) -> Dict[str, str]:
    """Fetch enhanced context from web sources"""
    context = {
        "web_search": "",
        "wikipedia": "",
        "analysis": ""
    }
    
    try:
        # Check cache first
        if query in knowledge_cache:
            logger.info("📚 Using cached knowledge")
            return knowledge_cache[query]
        
        # Try Wikipedia first
        wikipedia_context = await scraper.fetch_url(
            f"https://en.wikipedia.org/w/api.php?action=query&titles={query}&"
            f"prop=extracts&explaintext=1&format=json"
        )
        
        if wikipedia_context:
            try:
                data = json.loads(wikipedia_context)
                pages = data.get('query', {}).get('pages', {})
                for page_id, page in pages.items():
                    if page_id != '-1':
                        context["wikipedia"] = page.get('extract', '')[:1500]
            except:
                pass
        
        # Cache the result
        knowledge_cache[query] = context
        logger.info(f"✅ Enhanced context fetched for: {query}")
    
    except Exception as e:
        logger.warning(f"Web fetch error: {e}")
    
    return context


async def advanced_answer_literature_question(user_id: int, question: str) -> str:
    """
    Advanced neural network function with web learning capabilities
    Uses multiple sources for comprehensive answers
    """
    
    if not OPENROUTER_API_KEY:
        logger.error("OPENROUTER_API_KEY not set")
        return "⚠️ API configuration error. Please contact administrator."
    
    # Initialize user conversation if needed
    if user_id not in user_conversations:
        user_conversations[user_id] = []
    
    try:
        # Fetch enhanced context from web
        web_context = await fetch_enhanced_literature_context(question)
        
        # Get local knowledge
        local_writer = get_writer_knowledge(question)
        local_work = get_work_knowledge(question)
        local_movement = get_movement_knowledge(question)
        
        # Build comprehensive system prompt with web-enhanced learning
        system_prompt = f"""{get_literature_system_prompt()}

ADVANCED LEARNING MODE:
You now have access to:
1. Real-time web research (Wikipedia and online sources)
2. Continuous learning from user interactions
3. Comprehensive literature database
4. Multi-source information synthesis

INSTRUCTION:
- Synthesize information from local knowledge base AND web sources
- Provide comprehensive, well-researched answers
- Include specific examples, quotes, and historical context
- Cite sources when using external information
- Adapt response style based on question type
- Learn from this interaction to improve future responses"""
        
        # Build conversation history
        conversation_history = user_conversations[user_id][-10:]
        
        messages = []
        for msg in conversation_history:
            messages.append(msg)
        
        # Build enriched user message
        enriched_message = question
        if web_context["wikipedia"]:
            enriched_message += f"\n\n📚 Web Context:\n{web_context['wikipedia'][:500]}"
        if local_writer:
            enriched_message += f"\n\n📖 Local Knowledge: {local_writer['name']}"
        if local_work:
            enriched_message += f"\n\n📚 Work Info: {local_work['title']}"
        
        messages.append({
            "role": "user",
            "content": enriched_message
        })
        
        # Call Claude API with enhanced context
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://replit.com",
                "X-Title": "AdvancedLiteraryBot"
            }
            
            payload = {
                "model": "claude-3.5-sonnet",
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 2000,
                "system": system_prompt
            }
            
            async with session.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload
            ) as resp:
                if resp.status == 200:
                    response_data = await resp.json()
                    assistant_response = response_data.get('choices', [{}])[0].get('message', {}).get('content', '')
                    
                    # Optimize response based on learning
                    optimized_response = optimize_response(assistant_response, question)
                    
                    # Store in memory
                    user_conversations[user_id].append({"role": "user", "content": question})
                    user_conversations[user_id].append({"role": "assistant", "content": optimized_response})
                    
                    # Trim memory if too long
                    if len(user_conversations[user_id]) > MAX_MEMORY:
                        user_conversations[user_id] = user_conversations[user_id][-MAX_MEMORY:]
                    
                    logger.info(f"✅ Advanced response generated for user {user_id}")
                    return optimized_response
                else:
                    error_data = await resp.text()
                    logger.error(f"API error {resp.status}: {error_data}")
    
    except Exception as e:
        logger.error(f"Advanced error: {e}")
    
    return "I encountered an error processing your request. Please try again."


async def rate_response(user_id: int, question: str, response: str, rating: int):
    """Record user rating for training"""
    record_user_feedback(user_id, question, response, rating)
    logger.info(f"📊 Response rated {rating}/5 by user {user_id}")


async def get_neural_metrics() -> Dict:
    """Get neural network training metrics"""
    return get_training_metrics()


def clear_user_memory(user_id: int) -> None:
    """Clear conversation history for a user"""
    if user_id in user_conversations:
        user_conversations[user_id] = []
    logger.info(f"Memory cleared for user {user_id}")
