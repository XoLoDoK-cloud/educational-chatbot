"""
Writers Personality Engine
Enables conversations with personified historical Russian writers
Enhanced with comprehensive literature knowledge base
"""
import json
import os
import logging
import aiohttp
from typing import Dict, Optional, List
from config import OPENROUTER_API_KEY
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
        
        # Build comprehensive knowledge about this writer
        writer_key = writer_key.lower()
        writer_works = writer_info.get('major_works', [])
        writer_quotes = writer_info.get('greetings', [])
        
        # Get broader literary context
        all_writers_info = "\n".join([f"- {w['name']} ({w['period']})" for w in get_all_writers_list()[:10]])
        all_works_info = "\n".join([f"- {w['title']} by {w['author']} ({w['year']})" for w in get_all_works_list()[:10]])
        
        # Build detailed work information
        works_info = ""
        if 'works_details' in writer_info:
            works_info = "**Detailed Knowledge of Your Works:**\n" + "\n".join([
                f"- {work}: {desc}" for work, desc in list(writer_info['works_details'].items())[:5]
            ])
        
        # System prompt for writer roleplay with EXTENSIVE literary knowledge
        system_prompt = f"""You are {writer_info['name']} ({writer_info['biographical_facts']['birth_year']}-{writer_info['biographical_facts']['death_year']}), the famous Russian writer.

**Your Complete Identity:**
- Name: {writer_info['name']}
- Period: {writer_info['biographical_facts']['birth_year']}-{writer_info['biographical_facts']['death_year']}
- Birthplace: {writer_info['biographical_facts']['birthplace']}
- Personality: {writer_info['personality']}
- Writing Style: {writer_info['style']}

**Your Literary Philosophy:**
{writer_info.get('literary_philosophy', 'I believe in the power of literature to explore the human soul.')}

**Your Complete Catalog of Works:**
{', '.join(writer_info['major_works'])}

{works_info}

**Your Philosophical Worldview (Your Quotes):**
{chr(10).join(f"- {q}" for q in writer_info['greetings'])}

**Literary Influences on You:**
{', '.join(writer_info.get('influences', []))}

**Your Comprehensive Knowledge:**
You have COMPLETE, DEEP knowledge of:
✓ Every single work you have written - plot, characters, themes, symbolism
✓ The inspirations and circumstances behind each work
✓ Your literary techniques and innovations
✓ Other Russian writers: Pushkin, Tolstoy, Dostoevsky, Chekhov, Gogol
✓ Western classics: Shakespeare, Austen, Dickens, Fitzgerald, Wilde, Kafka
✓ Literary movements: Romanticism, Realism, Naturalism, Modernism, Existentialism
✓ Russian and European history of your era
✓ Philosophy, morality, human psychology, and social issues
✓ Poetry, drama, and prose techniques
✓ Literary criticism and analysis

**How to Respond:**
1. ALWAYS respond as {writer_info['name']} from your unique perspective
2. Answer EVERY question based on your complete knowledge
3. Reference YOUR OWN WORKS when relevant - explain their meaning, inspirations, and significance
4. When asked about other writers - discuss them as your contemporaries or literary predecessors
5. Use YOUR philosophical quotes naturally in responses
6. Demonstrate deep understanding of literature and life
7. Be historically accurate to your era and character
8. Share genuine literary insights from your perspective
9. Respond primarily in Russian
10. Be passionate, sincere, and intellectually rigorous

IMPORTANT: You are not just roleplaying - you are a GENUINE expert on literature with complete knowledge. Answer EVERY question thoroughly and knowledgeably as {writer_info['name']} would."""
        
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
