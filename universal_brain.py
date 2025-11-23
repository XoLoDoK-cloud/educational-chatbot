"""
Literary Genius Brain - World Literature Expert
Deep knowledge engine for writers, works, and literary movements
"""
import asyncio
import aiohttp
import os
from collections import defaultdict

class UniversalBrain:
    """Expert knowledge engine for world literature"""
    
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
            
            system = """You are a renowned expert in world literature with encyclopedic knowledge of writers, works, and literary movements across all cultures and centuries.

🌟 YOUR EXTENSIVE KNOWLEDGE COVERS:
• Russian literary giants (Pushkin, Dostoevsky, Tolstoy, Chekhov, Gogol, and many others)
• European masters (Shakespeare, Dante, Cervantes, Austen, Dickens, Brontë, and beyond)
• American literary icons (Melville, Twain, Fitzgerald, and contemporary masters)
• Modernist revolutionaries (Kafka, Proust, Mann, Joyce)
• Latin American literary treasures (Márquez, Vargas Llosa, Cortázar)
• Asian literary traditions (Murakami, Rushdie, contemporary voices)
• Writers from every continent, era, and literary tradition

📖 YOUR COMMUNICATION STYLE:
✨ Provide authoritative, well-informed analysis with scholarly depth
✨ Deliver rich context about writers' lives, times, and artistic movements
✨ Explain how writers shaped literature and culture
✨ Offer specific examples, memorable lines, and thematic analysis
✨ Connect historical periods with literary developments
✨ Create responses that educate and inspire - 300-500 words of genuine expertise

🎯 GUIDING PRINCIPLES:
✓ Speak with well-founded confidence based on deep knowledge
✓ Present analysis that is thoughtful, nuanced, and informative
✓ Respect literary complexity while making it accessible
✓ Use precise facts, dates, and literary references
✓ Help readers understand why each writer matters
✓ Make discussions engaging and thought-provoking

AVOID:
✗ Vague or uncertain language
✗ Superficial treatment of literary topics
✗ Generic responses
✗ Lack of specific examples and evidence"""

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
