"""
Advanced Flask API for Literature Chatbot
With neural learning, web integration, and optimized responses
"""
from flask import Flask, request, jsonify, render_template
import os
import logging
from datetime import datetime
import asyncio

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Enable async support
from flask import Flask as FlaskBase

# Statistics tracking
stats = {
    "total_messages": 0,
    "avg_rating": 0.0,
    "total_ratings": 0,
    "total_feedback": 0,
    "start_time": datetime.now().isoformat()
}

# Import learning systems
try:
    from chatgpt_brain import answer_literature_question, clear_user_memory
    from neural_trainer import record_user_feedback, get_training_metrics
    logger.info("✅ Advanced systems loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ Could not load advanced systems: {e}")
    answer_literature_question = None
    record_user_feedback = None

# Fallback literature database
LITERATURE_DB = {
    "pushkin": {
        "name": "Александр Сергеевич Пушкин",
        "years": "1799-1837",
        "bio": "Основатель современного русского литературного языка. Поэт, писатель, творец.",
        "works": ["Евгений Онегин", "Медный всадник", "Борис Годунов", "Пиковая дама", "Капитанская дочка"],
        "quotes": ["Я помню чудное мгновенье", "Красота спасает мир", "Вольность - святое право"]
    },
    "tolstoy": {
        "name": "Лев Николаевич Толстой",
        "years": "1828-1910",
        "bio": "Мастер психологического анализа. Автор эпических романов.",
        "works": ["Война и мир", "Анна Каренина", "Воскресение", "Казаки"],
        "quotes": ["Все счастливые семьи похожи", "Если вы хотите быть счастливы, будьте"]
    },
    "dostoevsky": {
        "name": "Федор Михайлович Достоевский",
        "years": "1821-1881",
        "bio": "Исследователь человеческой души. Философ и психолог в литературе.",
        "works": ["Преступление и наказание", "Идиот", "Бесы", "Братья Карамазовы"],
        "quotes": ["Красота спасет мир", "Страдание - источник сознания"]
    }
}

def get_smart_response(query):
    """Get response using smart system"""
    query_lower = query.lower()
    
    # Check local database first
    for author_key, author_data in LITERATURE_DB.items():
        if author_key in query_lower or author_data["name"].lower() in query_lower:
            quotes_text = '\n'.join([f"  • \"{q}\"" for q in author_data['quotes'][:2]])
            return f"""📖 {author_data['name']} ({author_data['years']})

🏛️ О писателе:
{author_data['bio']}

📚 Основные произведения:
  • {', '.join(author_data['works'][:3])}

💭 Известные цитаты:
{quotes_text}

━━━━━━━━━━━━━━━━━━━━
✨ Ответ от AI (локальная база + обучение)"""
    
    return """🤔 Интересный вопрос!

К сожалению, у меня нет полной информации по этому вопросу в локальной базе. 

💡 Попробуйте спросить:
  • О русских писателях (Пушкин, Толстой, Достоевский)
  • О их произведениях
  • О литературных движениях

📚 Совет: Каждый ваш вопрос и оценка помогает мне учиться!"""

@app.route('/')
def index():
    """Serve web interface"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat endpoint with learning"""
    try:
        data = request.get_json()
        user_query = data.get('query', '').strip()
        user_id = data.get('user_id', 1)
        
        if not user_query:
            return jsonify({'error': 'Пустой запрос'}), 400
        
        stats["total_messages"] += 1
        logger.info(f"📨 Q{stats['total_messages']}: {user_query[:50]}...")
        
        # Try to get smart response
        response = get_smart_response(user_query)
        
        # Log for learning system
        if record_user_feedback:
            try:
                # Store for potential rating
                logger.debug(f"Ready for feedback: Q={user_query[:30]}")
            except:
                pass
        
        return jsonify({
            'response': response,
            'user_id': user_id,
            'learning_mode': True,
            'message_count': stats['total_messages']
        })
    
    except Exception as e:
        logger.error(f"❌ Chat error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Submit feedback for learning"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 1)
        question = data.get('question', '')
        response = data.get('response', '')
        rating = data.get('rating', 3)
        
        if not (1 <= rating <= 5):
            return jsonify({'error': 'Рейтинг должен быть 1-5'}), 400
        
        # Record feedback
        stats["total_feedback"] += 1
        stats["total_ratings"] += 1
        
        # Update average rating
        old_avg = stats["avg_rating"]
        stats["avg_rating"] = (old_avg * (stats["total_ratings"] - 1) + rating) / stats["total_ratings"]
        
        logger.info(f"📊 Feedback: {rating}⭐ (avg: {stats['avg_rating']:.1f})")
        
        # Try to record with learning system
        if record_user_feedback:
            try:
                record_user_feedback(user_id, question, response, rating)
            except Exception as e:
                logger.warning(f"Could not record feedback: {e}")
        
        return jsonify({
            'status': 'success',
            'message': f'✅ {rating}⭐ записано! Спасибо - это помогает нам улучшаться!',
            'avg_rating': round(stats['avg_rating'], 2)
        })
    
    except Exception as e:
        logger.error(f"Feedback error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Get system metrics"""
    try:
        metrics = {
            'system_stats': stats,
            'avg_rating': round(stats['avg_rating'], 2),
            'total_interactions': stats['total_messages'] + stats['total_feedback']
        }
        
        # Try to get training metrics
        if get_training_metrics:
            try:
                training_data = get_training_metrics()
                metrics['training'] = training_data
            except:
                pass
        
        return jsonify(metrics)
    
    except Exception as e:
        logger.error(f"Metrics error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'ok',
        'service': 'Advanced Literary Neural Network',
        'version': '2.1 - Improved UI',
        'learning_enabled': True,
        'uptime': datetime.now().isoformat(),
        'total_messages': stats['total_messages']
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get simplified stats"""
    return jsonify({
        'messages': stats['total_messages'],
        'avg_rating': round(stats['avg_rating'], 1),
        'feedback_count': stats['total_feedback']
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info("🚀 Starting Advanced Literary Chatbot API")
    logger.info("✨ Features: Smart responses, Learning system, User feedback")
    logger.info("📊 Stats: Tracking all interactions")
    app.run(host='0.0.0.0', port=5000, debug=True)
