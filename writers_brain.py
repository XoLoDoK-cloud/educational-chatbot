"""
Writers Personality Engine - LOCAL VERSION (No API Required)
Enables conversations with personified historical Russian writers
Uses local knowledge base only
"""
import json
import os
import logging
from typing import Dict, Optional, List
from literature_knowledge import get_all_writers_list, get_all_works_list, LITERATURE_DB

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


def generate_writer_response(writer_info: Dict, message: str) -> str:
    """Generate response from writer using local knowledge base"""
    writer_name = writer_info['name']
    quotes = writer_info.get('greetings', [])
    works = writer_info.get('major_works', [])
    
    msg_lower = message.lower()
    
    # Simple pattern matching for common responses
    responses = []
    
    if any(word in msg_lower for word in ['привет', 'hello', 'как дела', 'how are you']):
        responses.append(f"🎭 {writer_name}: Приветствую вас! Рад познакомиться.")
    
    if any(word in msg_lower for word in ['произведение', 'work', 'книга', 'book', 'роман', 'novel']):
        if works:
            works_str = ', '.join(works[:3])
            responses.append(f"📚 {writer_name}: Мои наиболее значимые произведения - {works_str}.")
    
    if any(word in msg_lower for word in ['стиль', 'style', 'писал', 'wrote', 'манер', 'manner']):
        style = writer_info.get('style', 'уникальный')
        responses.append(f"🖊️ {writer_name}: Мой стиль можно охарактеризовать как {style}.")
    
    if any(word in msg_lower for word in ['цитата', 'quote', 'мудр', 'wise', 'мысль', 'thought']):
        if quotes:
            responses.append(f"💭 {writer_name}: Как я говорил, \"{quotes[0]}\"")
    
    if any(word in msg_lower for word in ['жизнь', 'life', 'история', 'history', 'биография', 'biography']):
        bio = writer_info.get('biographical_facts', {})
        birth = bio.get('birth_year', '?')
        responses.append(f"📖 {writer_name}: Я родился в {birth} году в России...")
    
    if not responses:
        # Default response
        responses.append(f"🎭 {writer_name}: Это интересный вопрос. Позвольте мне поделиться своими размышлениями...")
        if quotes:
            responses.append(f"Как я верил, \"{quotes[0]}\"")
    
    return "\n".join(responses)


async def talk_to_writer(user_id: int, user_message: str) -> str:
    """
    Engage in conversation with a personified writer
    Uses local knowledge base (no API required)
    """
    
    writer_key = get_user_writer(user_id)
    if not writer_key:
        return "❌ Пожалуйста, сначала выберите писателя!"
    
    writer_info = get_writer_info(writer_key)
    if not writer_info:
        return "❌ Писатель не найден"
    
    # Use local response generation (no API needed)
    try:
        response = generate_writer_response(writer_info, user_message)
        
        # Store in conversation history
        if user_id not in writer_conversations:
            writer_conversations[user_id] = {}
        if writer_key not in writer_conversations[user_id]:
            writer_conversations[user_id][writer_key] = []
        
        writer_conversations[user_id][writer_key].append({
            "role": "user",
            "content": user_message
        })
        writer_conversations[user_id][writer_key].append({
            "role": "assistant", 
            "content": response
        })
        
        logger.info(f"✅ Generated response for {writer_info['name']}")
        return response
    
    except Exception as e:
        logger.error(f"Error generating writer response: {e}")
        return "⚠️ Извините, произошла ошибка при обработке вашего вопроса."


def clear_writer_conversation(user_id: int, writer_key: str = None):
    """Clear conversation history"""
    if writer_key:
        if user_id in writer_conversations and writer_key in writer_conversations[user_id]:
            writer_conversations[user_id][writer_key] = []
    else:
        if user_id in writer_conversations:
            writer_conversations[user_id] = {}
