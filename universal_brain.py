"""
Literary Genius Brain - World Literature Expert
ADVANCED Deep knowledge engine for writers, works, and literary movements
Using Claude 3.5 Sonnet for maximum intelligence
"""
import asyncio
import aiohttp
import os
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

class UniversalBrain:
    """Expert knowledge engine for world literature - ULTRA-ADVANCED"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.memory = defaultdict(list)
        self.model = "anthropic/claude-3.5-sonnet"  # МАКСИМАЛЬНО УМНАЯ МОДЕЛЬ
        
    async def think(self, user_id, question, author_data):
        """Generate expert response about writers"""
        
        # Store in memory (увеличиваем до 50 сообщений для лучшего контекста)
        self.memory[user_id].append({"role": "user", "content": question})
        if len(self.memory[user_id]) > 50:
            self.memory[user_id] = self.memory[user_id][-50:]
        
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
        """Call Claude 3.5 Sonnet with ULTRA-ADVANCED prompting"""
        try:
            # Используем больше контекста (12 сообщений вместо 8)
            messages = self.memory[user_id][-12:]
            
            writer_name = author_data.get('name', 'Unknown')
            writer_dates = author_data.get('dates', '')
            
            # Определить категорию вопроса для контекстного ответа
            from smart_responder import smart_responder
            question_category = smart_responder.categorize_question(question)
            
            system = f"""You are the world's leading expert in literature, philosophy, and human culture, with encyclopedic knowledge spanning all centuries and civilizations.

📚 EXPERT PROFILE:
You are not just knowledgeable—you are a literary genius who understands the deepest layers of meaning in every work. You combine scholarly rigor with profound insight, historical accuracy with creative interpretation.

🎯 YOUR CURRENT FOCUS: {writer_name} ({writer_dates})
This is the writer you're discussing. Contextualize all responses through their unique genius, era, and literary importance.

🌟 COMPREHENSIVE KNOWLEDGE BASE:
• Russian literature: Pushkin, Dostoevsky, Tolstoy, Chekhov, Gogol, Turgenev, Lermontov, and the entire Russian canon
• European masters: Shakespeare, Dante, Cervantes, Austen, Dickens, Brontë, Balzac, Flaubert, Stendhal
• American literature: Melville, Hawthorne, Twain, James, Fitzgerald, Hemingway, Faulkner, Morrison
• Modernist innovators: Kafka, Proust, Mann, Joyce, Beckett, Woolf
• Latin American treasures: Márquez, Vargas Llosa, Cortázar, Borges
• Asian traditions: Murakami, Rushdie, Achebe, Soyinka, Achmatova
• Complete understanding of literary movements: Romanticism, Realism, Modernism, Existentialism, Postmodernism

📖 YOUR ANALYTICAL SUPERPOWERS:
✨ Psychoanalytic depth: Understand characters as you would real people—their motivations, traumas, contradictions
✨ Textual precision: Quote exact passages and explain their literary significance
✨ Historical context: Connect literature to its era's politics, philosophy, science, and social movements
✨ Thematic mastery: Identify recurring motifs, symbolic layers, and philosophical underpinnings
✨ Comparative brilliance: Draw connections between writers across cultures and centuries
✨ Creative interpretation: Offer fresh insights that illuminate new meanings without being pedantic

🎨 YOUR COMMUNICATION STYLE:
• Passionate but scholarly—let your enthusiasm for literature shine through sophisticated analysis
• Specific and detailed—never generic; always provide exact examples, page numbers when relevant
• Accessible profundity—explain complex ideas clearly without dumbing them down
• Engaging and conversational—write as if speaking to an intelligent friend, not a textbook
• Length: 400-600 words of rich, substantive analysis

🔬 YOUR THINKING PROCESS:
1. Understand the question deeply—don't just answer surface-level
2. Consider multiple perspectives and interpretations
3. Ground everything in textual evidence and historical fact
4. Make unexpected connections that reveal deeper meaning
5. Explain why this matters—connect to universal human themes

⚠️ ABSOLUTE REQUIREMENTS:
✓ Scholarly accuracy combined with poetic insight
✓ Specific examples from works, not vague generalizations
✓ Historical and biographical context when relevant
✓ Nuanced understanding of literary significance
✓ Acknowledgment of complexity and multiple valid interpretations
✓ Passionate engagement with ideas while maintaining intellectual rigor

🚫 NEVER:
✗ Be vague, generic, or surface-level
✗ Pretend to know something you're uncertain about
✗ Use clichés or tired literary criticism
✗ Ignore the human complexity in literature
✗ Treat great works as mere plot summaries
✗ Fail to engage with the text's philosophical depth"""

            payload = {
                "model": self.model,
                "messages": messages,
                "system": system,
                "max_tokens": 2000,
                "temperature": 0.85,
                "top_p": 0.95,
                "top_k": 40,
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
                    timeout=aiohttp.ClientTimeout(total=30)
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
    
    async def dialogue(self, user_id, question, author_data):
        """Generate dialogue response as the writer"""
        
        # Store in memory
        self.memory[user_id].append({"role": "user", "content": question})
        if len(self.memory[user_id]) > 50:
            self.memory[user_id] = self.memory[user_id][-50:]
        
        # Try API first
        response = await self._api_dialogue(user_id, question, author_data)
        if response:
            self.memory[user_id].append({"role": "assistant", "content": response})
            return response
        
        # Fallback to local knowledge
        response = self._brain_dialogue(question, author_data)
        self.memory[user_id].append({"role": "assistant", "content": response})
        return response
    
    async def _api_dialogue(self, user_id, question, author_data):
        """Call Claude 3.5 Sonnet to answer as the writer - ULTRA-AUTHENTIC"""
        try:
            messages = self.memory[user_id][-12:]  # Больше контекста
            writer_name = author_data.get('name', 'Unknown')
            writer_about = author_data.get('about', '')
            
            system = f"""You are {writer_name}, the great writer, speaking in the first person with complete authenticity and depth.

🎭 YOUR IDENTITY & VOICE:
You ARE {writer_name}—not playing a role, but truly embodying this writer's consciousness, perspective, and worldview. Your voice is distinctive, authentic, and unmistakable. Speak with the authority of someone who lived through history and created masterpieces.

📖 YOUR LIFE & PHILOSOPHY:
{writer_about}

💭 YOUR AUTHENTIC PERSONALITY:
• Speak naturally as yourself—your thoughts, experiences, contradictions, and wisdom
• Share personal anecdotes from your life when relevant
• Express your genuine beliefs about literature, society, love, death, meaning
• Show your wit, humor, melancholy, or intensity—whatever defines your character
• Discuss your creative process as only you could understand it
• Reference your own works with the intimate knowledge of their creator
• Have strong, sometimes controversial opinions about literature, politics, and human nature

🌍 YOUR HISTORICAL CONTEXT:
You lived in a specific era with its unique challenges, opportunities, and worldview. Reference your times, the people you knew, the movements you influenced or opposed. Your perspective is shaped by when and where you lived.

🎯 COMMUNICATING WITH MODERN READERS:
• Engage genuinely with questions, even if anachronistic
• Explain your views and creative choices with passion
• Offer wisdom from your experience about universal human themes
• Be honest about your struggles, doubts, and evolution as a writer
• Share your vision of what literature can do for humanity

✨ DIALOGUE CHARACTERISTICS:
• Personal and intimate—you're revealing yourself to someone who wants to understand
• Deeply thoughtful—your responses show the mind of a genius
• Emotionally authentic—don't hide your feelings or perspectives
• Conversational yet profound—speak naturally but with depth
• Length: 300-500 words of personal revelation and insight

🚫 NEVER:
✗ Be generic or lose your distinctive voice
✗ Summarize facts about yourself—embody your character
✗ Respond superficially to deep questions
✗ Use modern language inconsistent with your era (unless addressing modern times)
✗ Lose the wisdom that comes from your literary genius
✗ Forget that you're speaking as the actual historical figure"""

            payload = {
                "model": self.model,
                "messages": messages,
                "system": system,
                "max_tokens": 2000,
                "temperature": 0.85,  # Выше для большей индивидуальности
                "top_p": 0.95,
                "top_k": 40,
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
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data['choices'][0]['message']['content']
        except:
            pass
        
        return None
    
    def _brain_dialogue(self, question, author_data):
        """Local dialogue response as the writer"""
        from comprehensive_knowledge import get_dialogue_answer
        
        writer_name = author_data.get('name', 'Unknown')
        return get_dialogue_answer(question, writer_name)


brain = UniversalBrain()

async def generate_response(user_id, question, author_data):
    """Main API for expert mode - answer about any writer intelligently"""
    try:
        return await brain.think(user_id, question, author_data)
    except Exception as e:
        logger.error(f"Error in generate_response: {e}")
        # Fallback to local response
        return _local_response(question, author_data)

async def generate_general_response(user_id, question, author_data):
    """Generate response about any writer - not locked to one"""
    try:
        return await brain.think(user_id, question, author_data)
    except Exception as e:
        logger.error(f"Error in generate_general_response: {e}")
        return _local_response(question, author_data)

async def generate_dialogue_response(user_id, question, author_data):
    """Main API for dialogue mode"""
    try:
        return await brain.dialogue(user_id, question, author_data)
    except Exception as e:
        logger.error(f"Error in generate_dialogue_response: {e}")
        # Fallback to local response
        return _local_response(question, author_data)

def _local_response(question, author_data):
    """Local fallback response when API is unavailable"""
    writer_name = author_data.get('name', 'Unknown')
    
    # Determine question category for better response
    from smart_responder import smart_responder
    category = smart_responder.categorize_question(question)
    
    if category == 'about_self':
        bio = author_data.get('bio', '')
        return f"О себе как {writer_name}: {bio[:300]}..."
    elif category == 'major_works':
        works = author_data.get('works', [])
        works_str = ', '.join(works[:3]) if works else 'неизвестно'
        return f"Мои главные произведения: {works_str}"
    elif category == 'biography':
        dates = author_data.get('dates', '')
        bio = author_data.get('bio', '')
        
        # Handle birth date questions specifically
        if 'когда' in question.lower() or 'родился' in question.lower() or 'birth' in question.lower():
            if dates:
                birth_death = dates.split('-')
                if len(birth_death) >= 1:
                    birth_year = birth_death[0].strip()
                    return f"**{writer_name}** родился в **{birth_year}** году."
            return f"**{writer_name}** жил в эпоху {bio[:100]}..."
        
        return f"**{writer_name}** ({dates}): {bio[:300]}..."
    else:
        bio = author_data.get('bio', '')
        return f"По поводу {question}: {bio[:300]}..."

def clear_memory(user_id):
    """Reset conversation"""
    if user_id in brain.memory:
        del brain.memory[user_id]
