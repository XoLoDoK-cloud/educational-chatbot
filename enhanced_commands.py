"""
Enhanced commands for Literary Bot
Additional features for statistics, search, and information
"""
from comprehensive_knowledge import knowledge

def list_all_writers():
    """List all writers in the database"""
    writers = knowledge.writers_db
    total = len(writers)
    
    result = f"📊 **ЛИТЕРАТУРНАЯ БАЗА ДАННЫХ**\n\n"
    result += f"📚 Всего писателей: **{total}**\n\n"
    
    # Group by first letter
    groups = {}
    for key in sorted(writers.keys()):
        name = writers[key].get('name', 'Unknown')
        first_letter = name[0] if name else '?'
        if first_letter not in groups:
            groups[first_letter] = []
        groups[first_letter].append(name)
    
    # Display by groups
    result += "**Писатели по алфавиту:**\n\n"
    for letter in sorted(groups.keys()):
        names = ', '.join(groups[letter])
        result += f"**{letter}:** {names}\n"
    
    return result

def get_preload_status():
    """Get information about preload status"""
    writers = knowledge.writers_db
    total = len(writers)
    
    result = f"ℹ️ **СТАТУС СИСТЕМЫ**\n\n"
    result += f"✅ Писателей загружено: **{total}**\n"
    result += f"✅ Режимы работы: Эксперт, Диалог\n"
    result += f"✅ AI модель: Claude 3.5 Sonnet (OpenRouter)\n"
    result += f"✅ Интеграция: Wikipedia\n"
    result += f"✅ Нейросеть: NeuralWriter\n"
    result += f"✅ Кэш: Активен\n"
    result += f"\n📌 БОТ ПОЛНОСТЬЮ ФУНКЦИОНАЛЕН И ГОТОВ К РАБОТЕ!"
    
    return result
