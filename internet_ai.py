import aiohttp
import random
import re
import json
from bs4 import BeautifulSoup
import asyncio

class InternetWriterAI:
    def __init__(self):
        self.session = None
        self.writers_info = {
            "пушкин": {
                "name": "Александр Сергеевич Пушкин",
                "search_terms": ["Пушкин цитаты", "творчество Пушкина", "биография Пушкина"],
                "style": "элегантный, поэтичный, романтичный"
            },
            "достоевский": {
                "name": "Фёдор Михайлович Достоевский", 
                "search_terms": ["Достоевский цитаты", "философия Достоевского", "романы Достоевского"],
                "style": "глубокий, философский, психологичный"
            },
            "толстой": {
                "name": "Лев Николаевич Толстой",
                "search_terms": ["Толстой цитаты", "философия Толстого", "Война и мир цитаты"],
                "style": "мудрый, простой, нравственный"
            },
            "чехов": {
                "name": "Антон Павлович Чехов",
                "search_terms": ["Чехов цитаты", "рассказы Чехова", "Чехов афоризмы"],
                "style": "ироничный, лаконичный, наблюдательный"
            },
            "гоголь": {
                "name": "Николай Васильевич Гоголь",
                "search_terms": ["Гоголь цитаты", "Гоголь юмор", "Мертвые души цитаты"],
                "style": "образный, с юмором, мистический"
            }
        }
    
    async def ensure_session(self):
        """Создает сессию если ее нет"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
    
    async def generate_response(self, writer, user_message):
        """Генерирует ответ используя интернет-поиск"""
        await self.ensure_session()
        
        try:
            # Ищем информацию в интернете
            search_results = await self.search_internet(user_message, writer)
            quotes = await self.search_writer_quotes(writer)
            
            # Генерируем ответ на основе найденной информации
            response = await self.compose_response(writer, user_message, search_results, quotes)
            return response
            
        except Exception as e:
            # Если интернет не доступен - используем локальную генерацию
            return await self.fallback_response(writer, user_message)
    
    async def search_internet(self, query, writer):
        """Ищет информацию в интернете"""
        try:
            # Поиск через Google (имитация)
            search_url = f"https://www.google.com/search?q={query}+{writer}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with self.session.get(search_url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Извлекаем сниппеты из результатов поиска
                    snippets = []
                    for g in soup.find_all('div', class_='g'):
                        title = g.find('h3')
                        desc = g.find('span', class_='aCOpRe')
                        if title and desc:
                            snippets.append({
                                'title': title.get_text(),
                                'description': desc.get_text()[:200]
                            })
                    
                    return snippets[:3]  # Возвращаем первые 3 результата
                    
        except:
            pass
        
        return []
    
    async def search_writer_quotes(self, writer):
        """Ищет цитаты писателя"""
        try:
            writer_name = self.writers_info[writer]["name"]
            quotes_url = f"https://citaty.info/author/{writer_name.replace(' ', '-').lower()}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with self.session.get(quotes_url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    quotes = []
                    quote_elements = soup.find_all('div', class_='field-item')
                    
                    for element in quote_elements[:10]:  # Берем первые 10 цитат
                        text = element.get_text().strip()
                        if len(text) > 20 and len(text) < 300:
                            quotes.append(text)
                    
                    return quotes
                    
        except:
            pass
        
        # Локальные цитаты на случай если интернет не доступен
        return self.get_local_quotes(writer)
    
    def get_local_quotes(self, writer):
        """Локальная база цитат"""
        local_quotes = {
            "пушкин": [
                "Я вас любил: любовь еще, быть может, в душе моей угасла не совсем",
                "Мы все учились понемногу чему-нибудь и как-нибудь",
                "Мечтам и годам нет возврата",
                "Быть можно дельным человеком и думать о красе ногтей",
                "На свете счастья нет, но есть покой и воля"
            ],
            "достоевский": [
                "Страдание - единственная причина сознания",
                "Человек есть тайна",
                "Красота спасет мир", 
                "Свобода не в том, чтоб не сдерживать себя, а в том, чтоб владеть собой",
                "Деньги есть чеканенная свобода"
            ],
            "толстой": [
                "Все счастливые семьи похожи друг на друга, каждая несчастливая семья несчастлива по-своему",
                "Сила не в том, чтобы побеждать других, а в том, чтобы побеждать себя",
                "Счастье не в том, чтобы делать всегда, что хочешь, а в том, чтобы всегда хотеть того, что делаешь",
                "Время - это самый ценный ресурс",
                "Истинная сила человека не в порывах, а в нерушимом спокойствии"
            ],
            "чехов": [
                "Краткость - сестра таланта",
                "В человеке должно быть все прекрасно: и лицо, и одежда, и душа, и мысли",
                "Если против какой-нибудь болезни предлагается очень много средств, то это значит, что болезнь неизлечима",
                "Замечательный день сегодня. То ли чай пойти выпить, то ли повеситься",
                "Чем выше человек по умственному и нравственному развитию, тем он свободнее"
            ],
            "гоголь": [
                "Какой же русский не любит быстрой езды",
                "Ох, тройка, птица-тройка, кто тебя выдумал",
                "Ревизор уже едет",
                "Есть еще порох в пороховницах",
                "Чему смеетесь? Над собой смеетесь!"
            ]
        }
        return local_quotes.get(writer, [])
    
    async def compose_response(self, writer, user_message, search_results, quotes):
        """Составляет ответ на основе найденной информации"""
        writer_style = self.writers_info[writer]["style"]
        
        # Анализируем вопрос
        question_type = self.analyze_question(user_message)
        
        # Начало ответа в стиле писателя
        opening = self.get_opening_phrase(writer)
        
        # Основная часть с информацией из интернета
        main_content = await self.generate_main_content(writer, user_message, search_results, quotes, question_type)
        
        # Добавляем цитату если есть
        quote_part = ""
        if quotes and random.random() < 0.6:  # 60% шанс добавить цитату
            quote = random.choice(quotes)
            quote_part = f" Как говорится: «{quote}»"
        
        # Завершение
        ending = self.get_ending_phrase(writer)
        
        # Собираем полный ответ
        full_response = f"{opening} {main_content}{quote_part}{ending}"
        
        return full_response
    
    def analyze_question(self, text):
        """Анализирует тип вопроса"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["что", "кто", "какой", "что такое"]):
            return "definition"
        elif any(word in text_lower for word in ["как", "почему", "зачем"]):
            return "explanation"
        elif any(word in text_lower for word in ["когда", "где", "сколько"]):
            return "fact"
        elif any(word in text_lower for word in ["мнение", "думаешь", "считаешь"]):
            return "opinion"
        else:
            return "general"
    
    def get_opening_phrase(self, writer):
        """Возвращает начальную фразу в стиле писателя"""
        openings = {
            "пушкин": ["О, ", "Мой друг, ", "Извольте выслушать, ", "Позвольте мне заметить, "],
            "достоевский": ["Видите ли... ", "Знаете... ", "Мне думается... ", "Я полагаю... "],
            "толстой": ["Друг мой, ", "По моему разумению, ", "Я убежден, что ", "Следует заметить, "],
            "чехов": ["Видите ли... ", "Заметьте... ", "Интересно, что ", "Следует отметить, "],
            "гоголь": ["Ах, ", "Ох, ", "Знаете, ", "Представьте себе, "]
        }
        return random.choice(openings.get(writer, ["Я думаю, что "]))
    
    async def generate_main_content(self, writer, user_message, search_results, quotes, question_type):
        """Генерирует основное содержание ответа"""
        
        # Если есть результаты поиска - используем их
        if search_results:
            # Берем информацию из первого результата
            first_result = search_results[0]
            info = first_result.get('description', '')
            
            if question_type == "definition":
                responses = [
                    f"на основании различных источников могу сказать, что {info}",
                    f"исследуя этот вопрос, я нашел, что {info}",
                    f"в литературных источниках указывается, что {info}"
                ]
            elif question_type == "explanation":
                responses = [
                    f"объяснение этому следующее: {info}",
                    f"причина заключается в том, что {info}",
                    f"суть дела в том, что {info}"
                ]
            else:
                responses = [
                    f"что касается вашего вопроса, то {info}",
                    f"по этому поводу могу отметить, что {info}",
                    f"исследование показывает, что {info}"
                ]
            
            return random.choice(responses)
        
        # Если нет результатов поиска - генерируем общий ответ
        return self.generate_general_response(writer, question_type)
    
    def generate_general_response(self, writer, question_type):
        """Генерирует общий ответ если нет интернета"""
        responses = {
            "definition": {
                "пушкин": "сущность этого вопроса требует глубокого осмысления и поэтического восприятия",
                "достоевский": "этот вопрос затрагивает глубины человеческого сознания и требует философского подхода",
                "толстой": "понимание этого вопроса лежит в плоскости нравственного осмысления и простоты восприятия",
                "чехов": "данный вопрос интересен для наблюдения и требует лаконичного, но точного объяснения",
                "гоголь": "этот вопрос полон загадок и требует образного, живого рассмотрения"
            },
            "explanation": {
                "пушкин": "объяснение этому явлению следует искать в гармонии и красоте мироздания",
                "достоевский": "причина кроется в сложной природе человеческой души и ее вечных противоречиях",
                "толстой": "суть объясняется простыми и вечными истинами человеческого бытия",
                "чехов": "объяснение можно найти в внимательном наблюдении за человеческой природой",
                "гоголь": "объяснение этому удивительному явлению столь же необычно, как и оно само"
            },
            "general": {
                "пушкин": "вопрос ваш достоин самого пристального внимания и поэтического осмысления",
                "достоевский": "этот вопрос заставляет задуматься о вечных проблемах человеческого существования",
                "толстой": "размышление над этим вопросом ведет к пониманию простых и важных истин",
                "чехов": "данный вопрос представляет интерес для наблюдательного ума",
                "гоголь": "вопрос этот столь же интересен, сколь и неожиданен"
            }
        }
        
        category_responses = responses.get(question_type, responses["general"])
        return category_responses.get(writer, "этот вопрос требует глубокого осмысления")
    
    def get_ending_phrase(self, writer):
        """Возвращает завершающую фразу"""
        endings = {
            "пушкин": [", не правда ли?", ", как мне кажется.", ", осмелюсь заметить."],
            "достоевский": [", как мне думается.", ", если вдуматься.", ", в глубине души."],
            "толстой": [", друг мой.", ", по моему разумению.", ", как я убежден."],
            "чехов": [", как я наблюдаю.", ", если заметить.", ", что интересно."],
            "гоголь": [", представьте себе.", ", как это ни удивительно.", ", что за диковина!"]
        }
        return random.choice(endings.get(writer, ["."]))
