"""
Neural Network Training System
Learns from user interactions and feedback
Continuously improves response quality
"""
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import asyncio
from collections import defaultdict

logger = logging.getLogger(__name__)

class NeuralNetworkTrainer:
    """Trains and optimizes the neural network based on interactions"""
    
    def __init__(self):
        self.user_interactions = []
        self.question_patterns = defaultdict(list)
        self.response_ratings = defaultdict(list)
        self.learned_answers = {}
        self.improvement_metrics = {
            "total_interactions": 0,
            "avg_response_quality": 0.0,
            "learned_answers_count": 0,
            "user_satisfaction": 0.0
        }
    
    def record_interaction(self, user_id: int, question: str, response: str, 
                          rating: Optional[int] = None, category: str = "general"):
        """Record user interaction for learning"""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "question": question,
            "response": response,
            "rating": rating,  # 1-5 stars
            "category": category,
        }
        
        self.user_interactions.append(interaction)
        
        # Analyze question pattern
        question_type = self._classify_question(question)
        self.question_patterns[question_type].append({
            "question": question,
            "rating": rating or 0,
            "response": response
        })
        
        # Update metrics
        self.improvement_metrics["total_interactions"] += 1
        if rating:
            self.response_ratings[question_type].append(rating)
            avg = sum(self.response_ratings[question_type]) / len(self.response_ratings[question_type])
            self.improvement_metrics["avg_response_quality"] = avg
        
        logger.info(f"📊 Recorded interaction: {question[:50]}... (rating: {rating})")
        return True
    
    def _classify_question(self, question: str) -> str:
        """Classify question type"""
        q_lower = question.lower()
        
        if any(kw in q_lower for kw in ['who', 'who is', 'кто', 'кто такой']):
            return "author_info"
        elif any(kw in q_lower for kw in ['what', 'what is', 'что', 'что такое']):
            return "definition"
        elif any(kw in q_lower for kw in ['compare', 'vs', 'difference', 'сравн', 'отличие']):
            return "comparison"
        elif any(kw in q_lower for kw in ['analyze', 'анализ', 'explain', 'объясн']):
            return "analysis"
        elif any(kw in q_lower for kw in ['quote', 'цитата', 'said', 'сказал']):
            return "quotes"
        else:
            return "general"
    
    def learn_effective_patterns(self) -> Dict[str, Dict]:
        """Learn effective response patterns from high-rated interactions"""
        effective_patterns = {}
        
        for question_type, interactions in self.question_patterns.items():
            high_rated = [i for i in interactions if i.get('rating', 0) >= 4]
            
            if high_rated:
                effective_patterns[question_type] = {
                    "count": len(high_rated),
                    "avg_rating": sum(i['rating'] for i in high_rated) / len(high_rated),
                    "common_keywords": self._extract_keywords(high_rated),
                    "response_style": self._analyze_response_style(high_rated),
                }
                
                logger.info(f"📈 Learned pattern for {question_type}: {effective_patterns[question_type]}")
        
        self.improvement_metrics["learned_answers_count"] = len(effective_patterns)
        return effective_patterns
    
    def _extract_keywords(self, interactions: List[Dict]) -> List[str]:
        """Extract common keywords from high-rated interactions"""
        keywords = defaultdict(int)
        
        for interaction in interactions:
            words = interaction['question'].lower().split()
            for word in words:
                if len(word) > 4:  # Filter short words
                    keywords[word] += 1
        
        # Return top 10 keywords
        return sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:10]
    
    def _analyze_response_style(self, interactions: List[Dict]) -> Dict:
        """Analyze response style of high-rated answers"""
        avg_length = sum(len(i['response']) for i in interactions) / len(interactions)
        has_formatting = sum(1 for i in interactions if '**' in i['response'] or '✅' in i['response'])
        has_examples = sum(1 for i in interactions if 'example' in i['response'].lower())
        
        return {
            "avg_response_length": int(avg_length),
            "uses_formatting": has_formatting / len(interactions) > 0.5,
            "uses_examples": has_examples / len(interactions) > 0.5,
            "style": "detailed" if avg_length > 300 else "concise"
        }
    
    def get_trained_response_template(self, question_type: str) -> Dict:
        """Get trained template for specific question type"""
        patterns = self.learn_effective_patterns()
        
        if question_type in patterns:
            return patterns[question_type]
        
        return None
    
    def predict_optimal_response_format(self, question: str) -> Dict:
        """Predict optimal response format for a question"""
        question_type = self._classify_question(question)
        pattern = self.get_trained_response_template(question_type)
        
        if pattern:
            return {
                "type": question_type,
                "recommended_length": pattern["response_style"]["avg_response_length"],
                "use_formatting": pattern["response_style"]["uses_formatting"],
                "use_examples": pattern["response_style"]["uses_examples"],
                "style": pattern["response_style"]["style"],
                "confidence": pattern["avg_rating"],
            }
        
        return {
            "type": question_type,
            "recommended_length": 300,
            "use_formatting": True,
            "use_examples": True,
            "style": "balanced",
            "confidence": 0.5,
        }
    
    def get_improvement_metrics(self) -> Dict:
        """Get overall improvement metrics"""
        return {
            **self.improvement_metrics,
            "interactions_recorded": len(self.user_interactions),
            "question_types_learned": len(self.question_patterns),
            "timestamp": datetime.now().isoformat(),
        }
    
    def save_training_data(self, filepath: str = "training_data.json"):
        """Save training data for persistence"""
        training_data = {
            "interactions": self.user_interactions,
            "patterns": dict(self.question_patterns),
            "metrics": self.improvement_metrics,
            "timestamp": datetime.now().isoformat(),
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(training_data, f, ensure_ascii=False, indent=2)
            logger.info(f"✅ Training data saved to {filepath}")
        except Exception as e:
            logger.error(f"❌ Failed to save training data: {e}")
    
    def load_training_data(self, filepath: str = "training_data.json"):
        """Load previous training data"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                training_data = json.load(f)
            
            self.user_interactions = training_data.get("interactions", [])
            self.question_patterns = defaultdict(list, training_data.get("patterns", {}))
            self.improvement_metrics = training_data.get("metrics", {})
            
            logger.info(f"✅ Training data loaded from {filepath}")
        except Exception as e:
            logger.warning(f"⚠️ Could not load training data: {e}")


class ResponseOptimizer:
    """Optimizes responses based on training data"""
    
    def __init__(self, trainer: NeuralNetworkTrainer):
        self.trainer = trainer
    
    def optimize_response(self, response: str, question: str) -> str:
        """Optimize response based on learned patterns"""
        format_hint = self.trainer.predict_optimal_response_format(question)
        
        # Apply optimizations
        if format_hint["use_formatting"] and "**" not in response:
            response = self._add_formatting(response)
        
        if format_hint["use_examples"] and "example" not in response.lower():
            response = self._add_examples(response)
        
        # Adjust length if needed
        if len(response) > format_hint["recommended_length"] * 1.5:
            response = self._trim_response(response, format_hint["recommended_length"])
        
        return response
    
    def _add_formatting(self, response: str) -> str:
        """Add formatting to response"""
        # Add emojis and bold text
        lines = response.split('\n')
        formatted_lines = []
        
        for line in lines:
            if len(line.strip()) > 0:
                if any(marker in line for marker in [':', '●', '•', '-']):
                    line = f"• {line.strip()}"
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    def _add_examples(self, response: str) -> str:
        """Add examples to response"""
        return response + "\n\n💡 *Example: This is a sample response format.*"
    
    def _trim_response(self, response: str, max_length: int) -> str:
        """Trim response to recommended length"""
        if len(response) <= max_length:
            return response
        
        trimmed = response[:max_length].rsplit(' ', 1)[0] + "..."
        return trimmed


# Global trainer instance
_trainer = NeuralNetworkTrainer()
_optimizer = ResponseOptimizer(_trainer)


def record_user_feedback(user_id: int, question: str, response: str, rating: int):
    """Record user feedback for training"""
    _trainer.record_interaction(user_id, question, response, rating)


def get_training_metrics() -> Dict:
    """Get current training metrics"""
    return _trainer.get_improvement_metrics()


def optimize_response(response: str, question: str) -> str:
    """Optimize response before sending to user"""
    return _optimizer.optimize_response(response, question)


def save_training_data():
    """Save training progress"""
    _trainer.save_training_data()


def load_training_data():
    """Load previous training progress"""
    _trainer.load_training_data()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    trainer = NeuralNetworkTrainer()
    
    # Record some interactions
    trainer.record_interaction(1, "Who is Pushkin?", "Pushkin was a Russian poet...", rating=5)
    trainer.record_interaction(1, "What is romanticism?", "Romanticism is a movement...", rating=4)
    trainer.record_interaction(1, "Compare Tolstoy and Dostoevsky", "Both are great, but...", rating=5)
    
    # Learn patterns
    patterns = trainer.learn_effective_patterns()
    print("Learned Patterns:", json.dumps(patterns, ensure_ascii=False, indent=2))
    
    # Get metrics
    print("Metrics:", trainer.get_improvement_metrics())
