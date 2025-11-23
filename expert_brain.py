"""
Expert Brain - Intelligent System
Routes requests to best available response method
"""
import asyncio
from smart_conversation import generate_smart_response
from internet_response import get_internet_response

class ExpertBrain:
    """Intelligent routing system for best responses"""
    
    async def generate_response(self, user_id, message, author_data):
        """
        Generate response using intelligent routing:
        1. Check if web search needed (current events, dates, news)
        2. Use SmartConversation with GPT-4 (main intelligence)
        3. Fallback to conversation system
        """
        
        # Try internet response if needed for current info
        internet_response = await get_internet_response(message, author_data)
        if internet_response:
            print("✅ Используется интернет-поиск")
            return internet_response
        
        # Primary: SmartConversation system
        print("🧠 SmartConversation: основной режим")
        response = await generate_smart_response(user_id, message, author_data)
        
        if response and len(response.strip()) > 20:
            return response
        
        # Fallback: simple response
        print("⚠️ Fallback режим")
        return "Извините, я размышляю над вашим вопросом..."


# Global instance
expert_brain = ExpertBrain()


async def generate_omniscient_response(user_id, message, author_data):
    """Main function for response generation"""
    return await expert_brain.generate_response(user_id, message, author_data)
