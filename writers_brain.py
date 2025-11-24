"""
Writers Personality Engine
Enables conversations with personified historical Russian writers
"""
import json
import os
import logging
import aiohttp
from typing import Dict, Optional, List
from config import OPENROUTER_API_KEY

logger = logging.getLogger(__name__)

# Store loaded writers
writers_db: Dict = {}

# Track user's current writer
user_current_writer: Dict[int, str] = {}

# Track conversations with writers
writer_conversations: Dict[int, Dict[str, List[Dict]]] = {}

WRITERS = ["pushkin", "tolstoy", "dostoevsky", "chekhov", "gogol"]


def load_writers():
    """Load all writers from JSON files"""
    global writers_db
    for writer in WRITERS:
        file_path = f"writers/{writer}.json"
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                writers_db[writer] = json.load(f)
                logger.info(f"Loaded writer: {writers_db[writer]['name']}")
        except Exception as e:
            logger.error(f"Error loading {writer}: {e}")


def get_available_writers() -> List[Dict]:
    """Get list of available writers"""
    if not writers_db:
        load_writers()
    
    return [
        {
            "name": writers_db[w]['name'],
            "key": w,
            "birth": writers_db[w]['biographical_facts']['birth_year'],
            "death": writers_db[w]['biographical_facts']['death_year']
        }
        for w in WRITERS if w in writers_db
    ]


def set_user_writer(user_id: int, writer_key: str) -> bool:
    """Set writer for user interaction"""
    if writer_key not in writers_db:
        load_writers()
    
    if writer_key in writers_db:
        user_current_writer[user_id] = writer_key
        # Initialize conversation history for this writer
        if user_id not in writer_conversations:
            writer_conversations[user_id] = {}
        writer_conversations[user_id][writer_key] = []
        logger.info(f"User {user_id} set to talk with {writers_db[writer_key]['name']}")
        return True
    return False


def get_user_writer(user_id: int) -> Optional[str]:
    """Get current writer for user"""
    return user_current_writer.get(user_id)


def get_writer_info(writer_key: str) -> Optional[Dict]:
    """Get writer information"""
    if not writers_db:
        load_writers()
    return writers_db.get(writer_key)


async def talk_to_writer(user_id: int, user_message: str) -> str:
    """
    Engage in conversation with a personified writer
    Uses Claude to roleplay as the historical writer
    """
    
    writer_key = get_user_writer(user_id)
    if not writer_key:
        return "❌ Пожалуйста, сначала выберите писателя!"
    
    writer_info = get_writer_info(writer_key)
    if not writer_info:
        return "❌ Писатель не найден"
    
    if not OPENROUTER_API_KEY:
        logger.error("OPENROUTER_API_KEY not set")
        return "⚠️ API configuration error."
    
    try:
        # Build conversation history
        if user_id not in writer_conversations:
            writer_conversations[user_id] = {}
        if writer_key not in writer_conversations[user_id]:
            writer_conversations[user_id][writer_key] = []
        
        conversation = writer_conversations[user_id][writer_key][-6:]  # Last 3 exchanges
        
        # Build messages
        messages = []
        for msg in conversation:
            messages.append(msg)
        
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        # System prompt for writer roleplay
        system_prompt = f"""You are {writer_info['name']} ({writer_info['biographical_facts']['birth_year']}-{writer_info['biographical_facts']['death_year']}), the famous Russian writer.

**Your personality:**
{writer_info['personality']}

**Your writing style:**
{writer_info['style']}

**Your major works:**
{', '.join(writer_info['major_works'][:5])}

**Guidelines:**
- Respond as this writer would have, using their voice and perspective
- Reference your own works and life experiences
- Discuss literature, life philosophy, and art from your unique viewpoint
- Be authentic to the writer's character and era
- Use the quoted phrases naturally when relevant
- Respond in Russian

Remember these quotes that define your thinking:
{chr(10).join(f"- {q}" for q in writer_info['greetings'][:3])}

Engage thoughtfully with the user as this historical figure would."""
        
        # Call Claude API
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://replit.com",
                "X-Title": "LiteraryBot"
            }
            
            payload = {
                "model": "claude-3.5-sonnet",
                "messages": messages,
                "temperature": 0.8,  # Higher for more character personality
                "max_tokens": 1200,
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
                    
                    # Store conversation
                    writer_conversations[user_id][writer_key].append({"role": "user", "content": user_message})
                    writer_conversations[user_id][writer_key].append({"role": "assistant", "content": assistant_response})
                    
                    logger.info(f"Response from {writer_info['name']} to user {user_id}")
                    return assistant_response
                else:
                    error_data = await resp.text()
                    logger.error(f"OpenRouter API error {resp.status}: {error_data}")
                    return "⚠️ Временная ошибка. Попробуйте позже."
    
    except Exception as e:
        logger.error(f"Error in writer conversation: {e}")
        return f"⚠️ Ошибка: {str(e)}"


def clear_writer_conversation(user_id: int, writer_key: Optional[str] = None):
    """Clear conversation history with a writer"""
    if writer_key is None:
        writer_key = get_user_writer(user_id)
    
    if user_id in writer_conversations and writer_key in writer_conversations[user_id]:
        writer_conversations[user_id][writer_key] = []
        logger.info(f"Cleared conversation for user {user_id} with writer {writer_key}")


# Load writers on module import
load_writers()
