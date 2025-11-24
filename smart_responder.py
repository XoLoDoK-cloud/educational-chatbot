"""
Умный респондер - обработка вопросов с пониманием контекста
Определяет что спрашивает пользователь и дает точный ответ
"""
import re
from typing import Dict, List, Optional


class SmartResponder:
    """Умный анализ вопросов и маршрутизация ответов"""
    
    # Категории вопросов
    ABOUT_SELF_PATTERNS = [
        r'расскажи.*о\s*себе',
        r'кто\s+ты',
        r'tell.*about.*yourself',
        r'who.*are.*you',
        r'что\s+ты',
        r'какой\s+ты',
    ]
    
    FIRST_WORK_PATTERNS = [
        r'первое\s+произведение',
        r'first.*work',
        r'first.*novel',
        r'первый\s+роман',
        r'начал.*писать',
        r'когда.*начал',
    ]
    
    MAJOR_WORKS_PATTERNS = [
        r'главные\s+произведения',
        r'основные\s+работы',
        r'major.*works',
        r'best.*works',
        r'создал',
        r'написал',
    ]
    
    BIOGRAPHY_PATTERNS = [
        r'биография',
        r'жизнь',
        r'biography',
        r'life',
        r'родился',
        r'когда.*жил',
    ]
    
    INFLUENCE_PATTERNS = [
        r'влияние',
        r'impact',
        r'наследие',
        r'legacy',
        r'значение',
        r'влиял',
    ]
    
    ANALYSIS_PATTERNS = [
        r'анализ',
        r'analyse',
        r'объясни',
        r'расскажи\s+о\s+',
        r'tell.*about',
        r'explain',
    ]
    
    def __init__(self):
        self.question_categories = {
            'about_self': self.ABOUT_SELF_PATTERNS,
            'first_work': self.FIRST_WORK_PATTERNS,
            'major_works': self.MAJOR_WORKS_PATTERNS,
            'biography': self.BIOGRAPHY_PATTERNS,
            'influence': self.INFLUENCE_PATTERNS,
            'analysis': self.ANALYSIS_PATTERNS,
        }
    
    def categorize_question(self, question: str) -> str:
        """Определить категорию вопроса"""
        question_lower = question.lower().strip()
        
        for category, patterns in self.question_categories.items():
            for pattern in patterns:
                if re.search(pattern, question_lower):
                    return category
        
        return 'general'
    
    def build_context_prompt(self, category: str, writer_data: Dict) -> str:
        """Построить контекстный промпт для ответа"""
        writer_name = writer_data.get('name', 'Unknown')
        
        context_prompts = {
            'about_self': f"Расскажи о себе как {writer_name} - твоей личности, взглядах, философии. Говори от первого лица.",
            
            'first_work': f"Какое было твоё первое произведение? Расскажи как {writer_name} о начале творческого пути.",
            
            'major_works': f"Назови твои главные произведения. Объясни значение каждого и почему они важны для литературы.",
            
            'biography': f"Расскажи о своей жизни как {writer_name}. Какие события сформировали твоё творчество?",
            
            'influence': f"Какое влияние ты оказал на мировую литературу? Расскажи о своём наследии.",
            
            'analysis': f"Проанализируй глубже, дай точный и развёрнутый ответ, используя знание о литературе и контексте эпохи.",
            
            'general': f"Ответь на вопрос как {writer_name}, использую свои знания и опыт.",
        }
        
        return context_prompts.get(category, context_prompts['general'])
    
    def get_system_prompt_for_category(self, category: str, writer_data: Dict) -> str:
        """Получить системный промпт для конкретной категории"""
        writer_name = writer_data.get('name', 'Unknown')
        writer_about = writer_data.get('about', '')
        
        base_prompt = f"""You are {writer_name}, a renowned literary figure. 

CHARACTER PROFILE:
{writer_about}

INSTRUCTIONS FOR RESPONDING:
1. ANSWER THE SPECIFIC QUESTION - Don't give generic information
2. Use your expertise and perspective as {writer_name}
3. Be authentic and personal
4. Reference your own works when relevant
5. Show your unique voice and worldview

Current question category: {category}
Respond thoughtfully, specifically, and authoritically."""
        
        if category == 'about_self':
            return base_prompt + "\n\nFocus: Personal identity, philosophy, and character. Speak in first person."
        elif category == 'first_work':
            return base_prompt + "\n\nFocus: Your creative beginning. Describe your first work specifically."
        elif category == 'major_works':
            return base_prompt + "\n\nFocus: Your most important works. Explain their significance."
        elif category == 'biography':
            return base_prompt + "\n\nFocus: Your life story. Describe key biographical events."
        elif category == 'influence':
            return base_prompt + "\n\nFocus: Your literary legacy and influence."
        
        return base_prompt


# Глобальный экземпляр
smart_responder = SmartResponder()
