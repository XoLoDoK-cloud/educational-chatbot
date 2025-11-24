"""
Advanced Flask API with Neural Network Learning Capabilities
REST API for Literature Chatbot with Web Learning & Feedback
"""
from flask import Flask, request, jsonify, render_template
import os
import asyncio
import logging
from advanced_chatgpt_brain import (
    advanced_answer_literature_question, rate_response, get_neural_metrics
)
from neural_trainer import load_training_data, save_training_data

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load training data on startup
load_training_data()

# Sample Russian literature database (fallback)
LITERATURE_DB = {
    "pushkin": {
        "name": "Александр Сергеевич Пушкин",
        "years": "1799-1837",
        "bio": "Основатель современного русского литературного языка. Романтик с острым умом и независимым характером.",
        "works": ["Евгений Онегин", "Медный всадник", "Борис Годунов", "Пиковая дама", "Капитанская дочка"],
        "quotes": [
            "Я помню чудное мгновенье: передо мною явилась вы",
            "Красота спасает мир",
            "Вольность - святое право"
        ]
    }
}

@app.route('/')
def index():
    """Serve web interface"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
async def chat():
    """Advanced chat endpoint with learning"""
    try:
        data = request.get_json()
        user_query = data.get('query', '')
        user_id = data.get('user_id', 1)
        
        if not user_query:
            return jsonify({'error': 'Empty query'}), 400
        
        logger.info(f"🧠 Processing query from user {user_id}: {user_query[:50]}...")
        
        # Get advanced response
        response = await advanced_answer_literature_question(user_id, user_query)
        
        if not response:
            response = "I'm thinking about your question. Please try again."
        
        logger.info(f"✅ Response generated: {len(response)} chars")
        
        return jsonify({
            'response': response,
            'user_id': user_id,
            'learning_mode': True
        })
    
    except Exception as e:
        logger.error(f"❌ Chat error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/feedback', methods=['POST'])
async def submit_feedback():
    """Submit response feedback for neural network training"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 1)
        question = data.get('question', '')
        response = data.get('response', '')
        rating = data.get('rating', 3)  # 1-5 stars
        
        if not (1 <= rating <= 5):
            return jsonify({'error': 'Rating must be 1-5'}), 400
        
        # Record feedback for training
        await rate_response(user_id, question, response, rating)
        
        logger.info(f"📊 Feedback recorded: {rating}⭐ from user {user_id}")
        
        return jsonify({
            'status': 'success',
            'message': f'Thank you! Your {rating}⭐ rating helps us improve.',
            'learning': True
        })
    
    except Exception as e:
        logger.error(f"Feedback error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/metrics', methods=['GET'])
async def get_metrics():
    """Get neural network training metrics"""
    try:
        metrics = await get_neural_metrics()
        
        return jsonify({
            'metrics': metrics,
            'status': 'success'
        })
    
    except Exception as e:
        logger.error(f"Metrics error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'service': 'Advanced Literary Neural Network',
        'version': '2.0',
        'learning_enabled': True,
        'web_access': True
    })

@app.route('/api/save-training', methods=['POST'])
def save_training():
    """Save training data"""
    try:
        save_training_data()
        return jsonify({
            'status': 'success',
            'message': 'Training data saved successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info("🚀 Starting Advanced Literary Neural Network API...")
    logger.info("📚 Features: Web Learning, Neural Training, Real-time Feedback")
    logger.info("🧠 Learning Mode: ENABLED")
    logger.info("🌐 Web Access: ENABLED")
    app.run(host='0.0.0.0', port=5000, debug=True)
