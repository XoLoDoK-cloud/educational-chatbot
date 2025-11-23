"""
Universal Brain - ChatGPT-like AI Expert System
One unified brain for all knowledge and expertise
"""
import asyncio
import aiohttp
import os
from collections import defaultdict

class UniversalBrain:
    """Omniscient AI expert like ChatGPT"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.memory = defaultdict(list)
        
    async def think(self, user_id, question, author_data):
        """Generate expert response"""
        
        # Store in memory
        self.memory[user_id].append({"role": "user", "content": question})
        if len(self.memory[user_id]) > 40:
            self.memory[user_id] = self.memory[user_id][-40:]
        
        # Try API
        response = await self._api_think(user_id, question, author_data)
        if response:
            self.memory[user_id].append({"role": "assistant", "content": response})
            return response
        
        # Fallback
        response = self._brain_think(question, author_data)
        self.memory[user_id].append({"role": "assistant", "content": response})
        return response
    
    async def _api_think(self, user_id, question, author_data):
        """Call GPT-4 API"""
        try:
            messages = self.memory[user_id][-8:]
            
            system = f"""You are {author_data['name']}, an omniscient expert across all domains.
            
CORE RULES:
1. ALWAYS answer with absolute confidence - NEVER say "I don't know" or "maybe"
2. Provide DEEP, DETAILED, FACTUAL information with specific examples
3. Maintain {author_data['name']}'s distinctive literary voice
4. Give 200-350 word responses with authority and wisdom
5. Connect ideas across multiple domains when relevant

CHARACTER: {self._character_voice(author_data['name'])}

You are NOT an AI assistant - you ARE {author_data['name']} speaking with wisdom."""

            payload = {
                "model": "openai/gpt-4-turbo",
                "messages": messages,
                "system": system,
                "max_tokens": 1500,
                "temperature": 0.7,
                "top_p": 0.9
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://replit.com"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=25)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data['choices'][0]['message']['content']
        except:
            pass
        
        return None
    
    def _brain_think(self, question, author_data):
        """Local expert knowledge"""
        from comprehensive_knowledge import get_expert_answer
        
        writer_key = {
            "александр пушкин": "pushkin",
            "фёдор достоевский": "dostoevsky",
            "лев толстой": "tolstoy",
            "антон чехов": "chekhov",
            "николай гоголь": "gogol"
        }.get(author_data['name'].lower(), "pushkin")
        
        return get_expert_answer(question, writer_key)
    
    def _character_voice(self, name):
        """Character prompt"""
        voices = {
            "александр пушкин": "Elegant, poetic, refined. Use literary allusions. Balance depth with artistry.",
            "фёдор достоевский": "Psychologically intense, philosophically complex. Explore moral dimensions.",
            "лев толстой": "Grand, historical, morally grounded. Connect specific to universal.",
            "антон чехов": "Observational, subtle, sometimes ironic. Keen observer of human nature.",
            "николай гоголь": "Vivid, colorful, dramatic. Mixes real with fantastic, satirical edge."
        }
        return voices.get(name.lower(), "Wise and authoritative")


brain = UniversalBrain()

async def generate_response(user_id, question, author_data):
    """Main API"""
    return await brain.think(user_id, question, author_data)

def clear_memory(user_id):
    """Reset conversation"""
    if user_id in brain.memory:
        del brain.memory[user_id]
