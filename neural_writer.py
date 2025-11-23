import random
import re
import hashlib

class NeuralWriter:
    def __init__(self):
        self.writers_patterns = {
            "пушкин": {
                "style": "элегантный, поэтичный, романтичный",
                "opening": ["О, ", "Мой друг, ", "Извольте, ", "Позвольте мне "],
                "vocabulary": ["изящный", "прелестный", "блистательный", "очаровательный", "восхитительный"],
                "constructions": [
                    "не правда ли, что {}",
                    "мне кажется, что {}", 
                    "осмелюсь заметить, что {}",
                    "должен признаться, что {}",
                    "не могу не выразить {}"
                ],
                "quotes": [
                    "Я вас любил: любовь еще, быть может...",
                    "Мы все учились понемногу чему-нибудь и как-нибудь...",
                    "Мечтам и годам нет возврата..."
                ]
            },
            "достоевский": {
                "style": "глубокий, философский, психологичный", 
                "opening": ["Видите ли... ", "Знаете... ", "Мне думается... ", "Я полагаю... "],
                "vocabulary": ["душа", "страдание", "свобода", "нравственность", "совесть"],
                "constructions": [
                    "человеческая душа есть {}",
                    "в каждом из нас скрывается {}",
                    "жизнь представляет собой {}",
                    "смысл заключается в {}",
                    "истина состоит в том, что {}"
                ],
                "quotes": [
                    "Страдание - единственная причина сознания...",
                    "Человек есть тайна...",
                    "Красота спасет мир..."
                ]
            },
            "толстой": {
                "style": "мудрый, простой, нравственный",
                "opening": ["Друг мой, ", "По моему разумению, ", "Я убежден, что ", "Следует заметить, "],
                "vocabulary": ["простота", "истина", "вера", "нравственность", "совесть"],
                "constructions": [
                    "простота есть {}",
                    "истинная жизнь состоит в {}",
                    "счастье заключается в {}", 
                    "настоящий смысл в {}",
                    "главное - это {}"
                ],
                "quotes": [
                    "Все счастливые семьи похожи друг на друга...",
                    "Сила не в том, чтобы побеждать других...",
                    "Счастье не в том, чтобы делать всегда, что хочешь..."
                ]
            },
            "чехов": {
                "style": "ироничный, лаконичный, наблюдательный",
                "opening": ["Видите ли... ", "Заметьте... ", "Интересно, что ", "Следует отметить, "],
                "vocabulary": ["наблюдение", "ирония", "характер", "жизнь", "человек"],
                "constructions": [
                    "жизнь часто представляет собой {}",
                    "человеческая натура склонна к {}",
                    "интересно наблюдать, как {}",
                    "нельзя не заметить, что {}",
                    "следует признать, что {}"
                ],
                "quotes": [
                    "Краткость - сестра таланта...",
                    "В человеке должно быть все прекрасно...",
                    "Если против какой-нибудь болезни предлагается очень много средств..."
                ]
            },
            "гоголь": {
                "style": "образный, с юмором, мистический",
                "opening": ["Ах, ", "Ох, ", "Знаете, ", "Представьте себе, "],
                "vocabulary": ["удивительный", "невероятный", "загадочный", "странный", "чудесный"],
                "constructions": [
                    "иногда кажется, что {}",
                    "жизнь полна {}",
                    "мир устроен так, что {}",
                    "нередко случается, что {}", 
                    "можно наблюдать, как {}"
                ],
                "quotes": [
                    "Какой же русский не любит быстрой езды...",
                    "Ох, тройка, птица-тройка, кто тебя выдумал...",
                    "Ревизор уже едет..."
                ]
            }
        }
    
    def generate_response(self, writer, user_message):
        """Генерирует уникальный ответ на ЛЮБОЙ вопрос в стиле писателя"""
        writer_data = self.writers_patterns.get(writer, self.writers_patterns["пушкин"])
        
        # Анализируем вопрос пользователя
        question_type = self._analyze_question(user_message)
        theme = self._detect_theme(user_message)
        
        # Генерируем уникальный ответ
        response = self._compose_response(writer_data, question_type, theme, user_message)
        
        return response
    
    def _analyze_question(self, text):
        """Анализирует тип вопроса"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["как", "почему", "зачем"]):
            return "explanation"
        elif any(word in text_lower for word in ["что", "кто", "какой"]):
            return "definition" 
        elif any(word in text_lower for word in ["мнение", "думаешь", "считаешь"]):
            return "opinion"
        elif any(word in text_lower for word in ["расскажи", "опиши"]):
            return "story"
        else:
            return "general"
    
    def _detect_theme(self, text):
        """Определяет тему вопроса"""
        text_lower = text.lower()
        
        themes = {
            "любовь": ["любов", "чувств", "сердце", "роман"],
            "творчество": ["творчеств", "писать", "искусств", "вдохновен"],
            "жизнь": ["жизн", "смысл", "смерт", "существован"],
            "общество": ["обществ", "люди", "социум", "отношен"],
            "природа": ["природ", "погод", "времена года", "окружающ"],
            "технологии": ["техн", "компьютер", "интернет", "смартфон"]
        }
        
        for theme, keywords in themes.items():
            if any(keyword in text_lower for keyword in keywords):
                return theme
        
        return "общее"
    
    def _compose_response(self, writer_data, question_type, theme, user_message):
        """Составляет уникальный ответ"""
        # Начало ответа
        opening = random.choice(writer_data["opening"])
        
        # Основная часть - генерируем на основе типа вопроса
        main_part = self._generate_main_part(writer_data, question_type, theme, user_message)
        
        # Завершение
        ending = self._generate_ending(writer_data, question_type)
        
        # Собираем ответ
        full_response = opening + main_part + ending
        
        # Иногда добавляем реальную цитату (10% случаев)
        if random.random() < 0.1:
            quote = random.choice(writer_data["quotes"])
            full_response += " " + quote
        
        return full_response
    
    def _generate_main_part(self, writer_data, question_type, theme, user_message):
        """Генерирует основную часть ответа"""
        # Создаем уникальный seed на основе сообщения пользователя
        message_hash = hashlib.md5(user_message.encode()).hexdigest()
        random.seed(int(message_hash[:8], 16))
        
        construction = random.choice(writer_data["constructions"])
        vocabulary_word = random.choice(writer_data["vocabulary"])
        
        if question_type == "explanation":
            explanations = [
                f"сущность вещей заключается в их {vocabulary_word} природе",
                f"все происходит так, а не иначе по причине {vocabulary_word} устройства мира",
                f"ответ кроется в {vocabulary_word} понимании действительности"
            ]
            content = random.choice(explanations)
            
        elif question_type == "definition":
            definitions = [
                f"это есть не что иное, как {vocabulary_word} проявление бытия",
                f"суть состоит в {vocabulary_word} выражении истины", 
                f"определение следует искать в {vocabulary_word} аспекте рассмотрения"
            ]
            content = random.choice(definitions)
            
        elif question_type == "opinion":
            opinions = [
                f"моя точка зрения основана на {vocabulary_word} восприятии действительности",
                f"я склонен считать, что {vocabulary_word} подход наиболее верен",
                f"по моему убеждению, {vocabulary_word} понимание наиболее полно"
            ]
            content = random.choice(opinions)
            
        elif question_type == "story":
            stories = [
                f"история эта началась с {vocabulary_word} события",
                f"все произошло благодаря {vocabulary_word} стечению обстоятельств",
                f"рассказ мой будет о {vocabulary_word} превратностях судьбы"
            ]
            content = random.choice(stories)
            
        else:  # general
            general = [
                f"вопрос ваш затрагивает {vocabulary_word} стороны бытия",
                f"размышляя об этом, я прихожу к {vocabulary_word} выводу",
                f"осмысление данной темы требует {vocabulary_word} подхода"
            ]
            content = random.choice(general)
        
        return construction.format(content)
    
    def _generate_ending(self, writer_data, question_type):
        """Генерирует завершение ответа"""
        endings = {
            "пушкин": [
                ", не правда ли?",
                ", как мне кажется.",
                ", осмелюсь заметить.",
                ", должен я признаться."
            ],
            "достоевский": [
                ", как мне думается.",
                ", если вдуматься.",
                ", в глубине души.",
                ", по моему убеждению."
            ],
            "толстой": [
                ", друг мой.",
                ", по моему разумению.", 
                ", как я убежден.",
                ", следует заметить."
            ],
            "чехов": [
                ", как я наблюдаю.",
                ", если заметить.",
                ", что интересно.",
                ", следует признать."
            ],
            "гоголь": [
                ", представьте себе.",
                ", как это ни удивительно.",
                ", что за диковина!",
                ", ох, как странно!"
            ]
        }
        
          writer_endings = endings.get("пушкин", [", не правда ли?", ", как мне кажется."])  # default
        for writer, ends in endings.items():
            if writer in str(writer_data):
                writer_endings = ends
                break
        
        return random.choice(writer_endings) if writer_endings else ", как мне кажется."

# Создаем нейросеть
neural_ai = NeuralWriter()
