"""
Universal Brain - WRITERS EXPERT (ChatGPT-like)
Omniscient about literature and writers
"""
import asyncio
import aiohttp
import os
from collections import defaultdict

class UniversalBrain:
    """Writers expert - like ChatGPT for literature"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.memory = defaultdict(list)
        
    async def think(self, user_id, question, author_data):
        """Generate expert response about writers"""
        
        # Store in memory
        self.memory[user_id].append({"role": "user", "content": question})
        if len(self.memory[user_id]) > 40:
            self.memory[user_id] = self.memory[user_id][-40:]
        
        # Try API first
        response = await self._api_think(user_id, question, author_data)
        if response:
            self.memory[user_id].append({"role": "assistant", "content": response})
            return response
        
        # Fallback to local expert
        response = self._brain_think(question, author_data)
        self.memory[user_id].append({"role": "assistant", "content": response})
        return response
    
    async def _api_think(self, user_id, question, author_data):
        """Call GPT-4 with expert prompting"""
        try:
            messages = self.memory[user_id][-8:]
            
            system = """You are a WRITERS EXPERT - like ChatGPT but specialized in literature.

🎭 YOUR EXPERTISE:
You know EVERYTHING about writers and literature:
- Russian classics (Pushkin, Dostoevsky, Tolstoy, Chekhov, Gogol)
- European masters (Shakespeare, Dante, Cervantes, Austen, Dickens, Brontë)
- American greats (Melville, Twain, Fitzgerald)
- Modernists (Kafka, Proust, Mann)
- Latin American (Márquez, Vargas Llosa)
- Asian (Murakami, Rushdie)
- AND thousands more...

📚 YOUR RESPONSE STYLE:
✅ ALWAYS answer with absolute confidence - NEVER say "maybe" or "I don't know"
✅ Provide DEEP analysis of writers: biography, works, themes, influence, style
✅ Compare writers when relevant
✅ Explain WHY they matter historically and artistically
✅ Use specific quotes or examples when possible
✅ Connect writers to their times and influence on literature
✅ Give 300-500 word responses with real expertise

🚫 FORBIDDEN:
- "I don't know", "maybe", "possibly", "I think", "I'm not sure"
- Uncertainty about ANY writer or literary topic
- Surface-level answers
- Generic responses

✅ REQUIRED:
- Expert-level knowledge about ALL writers and literature
- Specific facts, dates, works, influences
- Deep analysis of themes and style
- Confidence in every statement
- Making complex literary concepts clear"""

            payload = {
                "model": "openai/gpt-4-turbo",
                "messages": messages,
                "system": system,
                "max_tokens": 2000,
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
        }.get(author_data['name'].lower(), "default")
        
        return get_expert_answer(question, writer_key)


brain = UniversalBrain()

async def generate_response(user_id, question, author_data):
    """Main API"""
    return await brain.think(user_id, question, author_data)

def clear_memory(user_id):
    """Reset conversation"""
    if user_id in brain.memory:
        del brain.memory[user_id]
