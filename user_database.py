"""
User Profile Database - Persists user data and statistics
Сохранение профилей пользователей и статистики
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class UserDatabase:
    def __init__(self, db_file: str = "user_data.json"):
        self.db_file = db_file
        self.users = {}
        self.load()
    
    def load(self):
        """Load users from file"""
        try:
            if os.path.exists(self.db_file):
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    self.users = json.load(f)
                logger.info(f"✅ Loaded {len(self.users)} users from database")
            else:
                logger.info("Creating new user database")
        except Exception as e:
            logger.error(f"Error loading database: {e}")
            self.users = {}
    
    def save(self):
        """Save users to file"""
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                # Convert sets to lists for JSON serialization
                users_copy = {}
                for user_id, data in self.users.items():
                    data_copy = data.copy()
                    if isinstance(data_copy.get('writers_talked'), set):
                        data_copy['writers_talked'] = list(data_copy['writers_talked'])
                    users_copy[user_id] = data_copy
                
                json.dump(users_copy, f, ensure_ascii=False, indent=2)
                logger.info(f"💾 Saved {len(self.users)} users")
        except Exception as e:
            logger.error(f"Error saving database: {e}")
    
    def get_user(self, user_id: int) -> Dict:
        """Get user profile"""
        user_id_str = str(user_id)
        if user_id_str not in self.users:
            self.users[user_id_str] = self._create_new_user(user_id)
        return self.users[user_id_str]
    
    def _create_new_user(self, user_id: int) -> Dict:
        """Create new user profile"""
        return {
            'user_id': user_id,
            'joined_date': datetime.now().isoformat(),
            'questions_asked': 0,
            'messages_count': 0,
            'writers_talked': [],
            'quiz_score': 0,
            'avg_rating': 0.0,
            'achievements': [],
            'favorite_writer': None,
            'interaction_history': [],
            'learning_progress': {
                'topics_learned': [],
                'response_quality': 0.0
            }
        }
    
    def update_question_count(self, user_id: int, question: str):
        """Update question statistics"""
        user = self.get_user(user_id)
        user['questions_asked'] += 1
        user['messages_count'] += 1
        user['interaction_history'].append({
            'type': 'question',
            'content': question[:100],
            'timestamp': datetime.now().isoformat()
        })
        self.save()
    
    def add_writer_interaction(self, user_id: int, writer: str):
        """Record writer interaction"""
        user = self.get_user(user_id)
        if writer not in user['writers_talked']:
            user['writers_talked'].append(writer)
        user['favorite_writer'] = writer
        user['messages_count'] += 1
        self.save()
    
    def update_quiz_score(self, user_id: int, points: int):
        """Update quiz score"""
        user = self.get_user(user_id)
        user['quiz_score'] += points
        self.save()
    
    def add_achievement(self, user_id: int, achievement: str):
        """Add achievement badge"""
        user = self.get_user(user_id)
        if achievement not in user['achievements']:
            user['achievements'].append(achievement)
            logger.info(f"🏆 User {user_id} earned: {achievement}")
            self.save()
    
    def get_stats(self, user_id: int) -> Dict:
        """Get user statistics"""
        user = self.get_user(user_id)
        days_active = (datetime.now() - datetime.fromisoformat(user['joined_date'])).days + 1
        
        return {
            'user_id': user_id,
            'joined_date': user['joined_date'][:10],
            'questions_asked': user['questions_asked'],
            'total_messages': user['messages_count'],
            'writers_visited': len(user['writers_talked']),
            'quiz_score': user['quiz_score'],
            'achievements_count': len(user['achievements']),
            'days_active': days_active,
            'avg_rating': user['avg_rating'],
            'favorite_writer': user['favorite_writer']
        }
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get top users by activity"""
        users_stats = []
        for user_id in self.users.keys():
            stats = self.get_stats(int(user_id))
            stats['activity_score'] = (
                stats['questions_asked'] * 2 +
                stats['total_messages'] +
                stats['quiz_score'] / 10 +
                stats['achievements_count'] * 5
            )
            users_stats.append(stats)
        
        users_stats.sort(key=lambda x: x['activity_score'], reverse=True)
        return users_stats[:limit]

# Global database instance
db = UserDatabase()
