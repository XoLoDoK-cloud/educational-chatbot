"""
Comprehensive Literature Knowledge Base
Contains extensive information about writers, works, quotes, and literary movements
"""

# Comprehensive Database of Writers with Works and Quotes
LITERATURE_DB = {
    "classic_authors": {
        "russian": {
            "aleksandr_pushkin": {
                "name": "Александр Пушкин",
                "period": "Romantic Era (1799-1837)",
                "works": [
                    "Eugene Onegin", "The Bronze Horseman", "Ruslian and Ludmila",
                    "Boris Godunov", "The Queen of Spades", "The Captain's Daughter",
                    "Dubrovsky", "Tales of Belkin", "The Gypsies", "Angelo"
                ],
                "quotes": [
                    "I remember a marvelous moment: you appeared before me",
                    "The beauty of the soul shines out when the person is happy",
                    "The pursuit of the extraordinary is the ruin of the ordinary",
                    "Alas, our youth we waste on trivial pursuits"
                ],
                "genres": ["Poetry", "Drama", "Prose", "Epic"],
                "influence": "Founder of modern Russian literature"
            },
            "lev_tolstoy": {
                "name": "Лев Толстой",
                "period": "Realist Era (1828-1910)",
                "works": [
                    "War and Peace", "Anna Karenina", "Resurrection", "The Cossacks",
                    "Youth", "Boyhood", "Childhood", "Kreutzer Sonata", "Master and Man",
                    "The Death of Ivan Ilyich", "Family Happiness"
                ],
                "quotes": [
                    "All happy families are alike; each unhappy family is unhappy in its own way",
                    "If you want to be happy, be",
                    "The task of art is immense",
                    "There is no greatness where there is not simplicity, goodness, and truth"
                ],
                "genres": ["Novel", "Novella", "Drama"],
                "influence": "Master of psychological realism and epic narrative"
            },
            "fedor_dostoevsky": {
                "name": "Фёдор Достоевский",
                "period": "Psychological Realism (1821-1881)",
                "works": [
                    "Crime and Punishment", "The Idiot", "Demons/The Possessed",
                    "The Brothers Karamazov", "Poor Folk", "Notes from Underground",
                    "The Gambler", "The Humiliated and Insulted", "House of the Dead"
                ],
                "quotes": [
                    "Suffering is the sole origin of consciousness",
                    "The mystery of human existence lies not in just staying alive, but in finding something to live for",
                    "Beauty will save the world",
                    "To love one person with a whole heart and soul, and to always respect that person is something beautiful"
                ],
                "genres": ["Novel", "Novella", "Psychology"],
                "influence": "Pioneer of psychological novels and existential themes"
            },
            "anton_chekhov": {
                "name": "Антон Чехов",
                "period": "Modern Era (1860-1904)",
                "works": [
                    "The Lady with the Dog", "The Seagull", "Uncle Vanya", "Three Sisters",
                    "The Cherry Orchard", "Ward No. 6", "A Boring Story", "Oysters",
                    "The Lottery Ticket", "The Steppe", "Palpitations"
                ],
                "quotes": [
                    "Brevity is the sister of talent",
                    "In life there is nothing more beautiful than being useful to people",
                    "Don't tell me the moon is shining; show me the glint of light on broken glass",
                    "Everyone is wise after the event"
                ],
                "genres": ["Short Story", "Drama", "Comedy"],
                "influence": "Master of subtle psychological portrayal and modern drama"
            },
            "nikolai_gogol": {
                "name": "Николай Гоголь",
                "period": "Romantic/Realist Transition (1809-1852)",
                "works": [
                    "Dead Souls", "The Government Inspector", "The Overcoat", "The Nose",
                    "Evenings on a Farm Near Dikanka", "Viy", "The Portrait",
                    "The Diary of a Madman", "The Carriage"
                ],
                "quotes": [
                    "What a strange mixture of feelings the fair sex provokes in us",
                    "What is the cause of our indifference to things?",
                    "The more I know people, the more I love my dog",
                    "I feel how my soul is divided into two parts"
                ],
                "genres": ["Novel", "Drama", "Satire"],
                "influence": "Pioneer of satirical realism and grotesque"
            },
        },
        "western": {
            "william_shakespeare": {
                "name": "William Shakespeare",
                "period": "Elizabethan/Jacobean (1564-1616)",
                "works": [
                    "Hamlet", "Romeo and Juliet", "Macbeth", "Othello", "King Lear",
                    "A Midsummer Night's Dream", "The Tempest", "Much Ado About Nothing",
                    "Twelfth Night", "The Merchant of Venice", "Sonnets (154)"
                ],
                "quotes": [
                    "To be, or not to be, that is the question",
                    "All the world's a stage, and all the men and women merely players",
                    "What's in a name? That which we call a rose by any other name would smell as sweet",
                    "Some are born great, some achieve greatness, some have greatness thrust upon them"
                ],
                "genres": ["Drama", "Tragedy", "Comedy", "Poetry"],
                "influence": "Greatest playwright in English language"
            },
            "jane_austen": {
                "name": "Jane Austen",
                "period": "Regency Era (1775-1817)",
                "works": [
                    "Pride and Prejudice", "Sense and Sensibility", "Emma",
                    "Northanger Abbey", "Persuasion", "Mansfield Park"
                ],
                "quotes": [
                    "It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife",
                    "There is nothing I would not do for those who are really my friends",
                    "I would rather be a woman than a man. Women are much more interesting",
                    "It is my ambition to say something true and therefore something new"
                ],
                "genres": ["Novel", "Romance", "Satire"],
                "influence": "Master of wit and social commentary"
            },
            "charles_dickens": {
                "name": "Charles Dickens",
                "period": "Victorian Era (1812-1870)",
                "works": [
                    "Great Expectations", "Oliver Twist", "A Tale of Two Cities",
                    "David Copperfield", "Bleak House", "Little Dorrit",
                    "Our Mutual Friend", "The Pickwick Papers"
                ],
                "quotes": [
                    "It was the best of times, it was the worst of times",
                    "Call me mad, but love to the last grain of my heart is a noble thing",
                    "It was the epoch of belief, it was the epoch of incredulity",
                    "I will honor Christmas in my heart, and keep it all the year"
                ],
                "genres": ["Novel", "Serial Fiction"],
                "influence": "Pioneer of social realism and serialized novels"
            },
            "george_bernhard_shaw": {
                "name": "George Bernard Shaw",
                "period": "Modern Era (1856-1950)",
                "works": [
                    "Pygmalion", "Saint Joan", "Man and Superman",
                    "Arms and the Man", "Candida", "Mrs Warren's Profession"
                ],
                "quotes": [
                    "The true joy in life is to be used for a purpose recognized by yourself as a mighty one",
                    "Some men see things as they are and ask why. I dream things that never were and ask why not",
                    "The reasonable man adapts himself to the world; the unreasonable one persists in trying to adapt the world to himself",
                    "Life isn't about finding yourself. Life is about creating yourself"
                ],
                "genres": ["Drama", "Comedy", "Philosophy"],
                "influence": "Master of witty philosophical drama"
            },
            "oscar_wilde": {
                "name": "Oscar Wilde",
                "period": "Late Victorian (1854-1900)",
                "works": [
                    "The Picture of Dorian Gray", "The Importance of Being Earnest",
                    "The Ideal Husband", "Lady Windermere's Fan", "Salome",
                    "An Ideal Husband", "A Woman of No Importance"
                ],
                "quotes": [
                    "Be yourself; everyone else is already taken",
                    "The only way to deal with an unfree world is to become so absolutely free that very existence is an act of rebellion",
                    "I can resist everything except temptation",
                    "We are all in the gutter, but some of us are looking at the stars"
                ],
                "genres": ["Drama", "Novel", "Wit/Epigram"],
                "influence": "Master of paradox and witty dialogue"
            },
            "franz_kafka": {
                "name": "Franz Kafka",
                "period": "Modern/Expressionist (1883-1924)",
                "works": [
                    "The Metamorphosis", "The Trial", "The Castle",
                    "In the Penal Colony", "A Hunger Artist", "The Man Who Disappeared"
                ],
                "quotes": [
                    "It is often the small, insignificant actions that ultimately lead to the greatest changes",
                    "A writer has a duty to write about the truth",
                    "The more I read, the more I acquire, the more certain I am that I know nothing",
                    "One must have chaos within oneself to give birth to a dancing star"
                ],
                "genres": ["Novel", "Short Story", "Existential"],
                "influence": "Pioneer of existential literature"
            },
            "f_scott_fitzgerald": {
                "name": "F. Scott Fitzgerald",
                "period": "Jazz Age (1896-1940)",
                "works": [
                    "The Great Gatsby", "Tender Is the Night", "This Side of Paradise",
                    "The Beautiful and Damned"
                ],
                "quotes": [
                    "So we beat on, boats against the current, borne back ceaselessly into the past",
                    "The test of a first-rate intelligence is the ability to hold two opposed ideas in the mind at the same time, and still retain the ability to function",
                    "I hope she'll be a fool — that's the best thing a girl can be in this world, a beautiful little fool",
                    "Rich people are different from you and me"
                ],
                "genres": ["Novel", "Short Story"],
                "influence": "Chronicler of the Jazz Age"
            },
        }
    },
    
    "literary_movements": {
        "romanticism": {
            "name": "Romanticism",
            "period": "Late 18th - 19th Century",
            "characteristics": [
                "Emphasis on emotion and imagination",
                "Nature as a source of truth",
                "Individual experience and subjectivity",
                "Reaction against neoclassicism"
            ],
            "key_authors": ["Pushkin", "Byron", "Keats", "Shelley", "Goethe"]
        },
        "realism": {
            "name": "Realism",
            "period": "19th Century",
            "characteristics": [
                "Focus on everyday life and ordinary people",
                "Detailed observation of society",
                "Rejection of idealization",
                "Scientific objectivity"
            ],
            "key_authors": ["Tolstoy", "Balzac", "Flaubert", "George Eliot"]
        },
        "naturalism": {
            "name": "Naturalism",
            "period": "Late 19th Century",
            "characteristics": [
                "Scientific approach to literature",
                "Environmental determinism",
                "Unflinching portrayal of society",
                "Influenced by Darwin and Zola"
            ],
            "key_authors": ["Zola", "Hardy", "Dreiser"]
        },
        "modernism": {
            "name": "Modernism",
            "period": "Early 20th Century",
            "characteristics": [
                "Experimental form and technique",
                "Stream of consciousness",
                "Fragmentation and discontinuity",
                "Rejection of traditional narrative"
            ],
            "key_authors": ["Joyce", "Woolf", "Proust", "Faulkner"]
        },
        "existentialism": {
            "name": "Existentialism",
            "period": "20th Century",
            "characteristics": [
                "Freedom and responsibility",
                "Authenticity and bad faith",
                "Absurdity of existence",
                "Individual consciousness"
            ],
            "key_authors": ["Sartre", "Camus", "Kafka", "Beckett"]
        }
    },
    
    "literary_terms": {
        "metaphor": "A figure of speech in which a word or phrase is applied to an object or action to which it is not literally applicable",
        "symbolism": "The use of symbols to represent ideas or qualities",
        "irony": "The use of language to mean something different from what is literally said",
        "foreshadowing": "An indication or hint of what is to come in a narrative",
        "alliteration": "The repetition of the same beginning sound in neighboring words",
        "protagonist": "The main character in a literary work",
        "antagonist": "A character opposing the protagonist",
        "climax": "The point of greatest tension in a narrative",
        "denouement": "The final part of a narrative in which loose ends are tied up",
        "motif": "A recurring element, image, or idea in a literary work"
    },
    
    "famous_works": {
        "war_and_peace": {
            "title": "War and Peace",
            "author": "Leo Tolstoy",
            "year": 1869,
            "genre": "Epic Novel",
            "themes": ["War and Peace", "History", "Society", "Fate vs Free Will"],
            "quotes": [
                "The life of man is neither matter nor spirit, but something transcending these",
                "History shows that nothing is certain except the unforeseen",
                "To every man and to every nation comes a moment when they must decide upon their future"
            ]
        },
        "crime_and_punishment": {
            "title": "Crime and Punishment",
            "author": "Fyodor Dostoevsky",
            "year": 1866,
            "genre": "Psychological Novel",
            "themes": ["Morality", "Redemption", "Guilt", "Mental Suffering"],
            "quotes": [
                "Pain and suffering are always inevitable for a large intelligence and a deep heart",
                "The greatest happiness is to know the source of unhappiness",
                "Taking a new step is what people fear most"
            ]
        },
        "the_great_gatsby": {
            "title": "The Great Gatsby",
            "author": "F. Scott Fitzgerald",
            "year": 1925,
            "genre": "Novel",
            "themes": ["American Dream", "Wealth", "Love", "Social Class"],
            "quotes": [
                "So we beat on, boats against the current, borne back ceaselessly into the past",
                "I hope she'll be a fool — that's the best thing a girl can be in this world",
                "The objects and events of our time are not less worthy of serious study than those of antiquity"
            ]
        },
        "hamlet": {
            "title": "Hamlet",
            "author": "William Shakespeare",
            "year": 1603,
            "genre": "Tragedy",
            "themes": ["Revenge", "Madness", "Mortality", "Duty"],
            "quotes": [
                "To be, or not to be, that is the question",
                "Something is rotten in the state of Denmark",
                "This above all: to thine ownself be true"
            ]
        },
        "pride_and_prejudice": {
            "title": "Pride and Prejudice",
            "author": "Jane Austen",
            "year": 1813,
            "genre": "Romance Novel",
            "themes": ["Social Class", "Gender", "Marriage", "First Impressions"],
            "quotes": [
                "It is a truth universally acknowledged that a single man must be in want of a wife",
                "I am not trying to pack all my intelligence into my words to prove something to you",
                "There is nothing I would not do for those who are really my friends"
            ]
        }
    }
}

def get_writer_knowledge(writer_name: str) -> dict | None:
    """Get comprehensive knowledge about a writer"""
    for region, writers in LITERATURE_DB["classic_authors"].items():
        for writer_key, writer_data in writers.items():
            if writer_name.lower() in writer_key or writer_name.lower() in writer_data["name"].lower():
                return writer_data
    return None

def get_work_knowledge(work_title: str) -> dict | None:
    """Get knowledge about a specific literary work"""
    for work_key, work_data in LITERATURE_DB["famous_works"].items():
        if work_title.lower() in work_key or work_title.lower() in work_data["title"].lower():
            return work_data
    return None

def get_movement_knowledge(movement_name: str) -> dict | None:
    """Get knowledge about a literary movement"""
    for movement_key, movement_data in LITERATURE_DB["literary_movements"].items():
        if movement_name.lower() in movement_key or movement_name.lower() in movement_data["name"].lower():
            return movement_data
    return None

def get_all_writers_list() -> list:
    """Get list of all available writers"""
    writers = []
    for region, writer_dict in LITERATURE_DB["classic_authors"].items():
        for writer_key, writer_data in writer_dict.items():
            writers.append({
                "name": writer_data["name"],
                "period": writer_data["period"],
                "key": writer_key
            })
    return writers

def get_all_works_list() -> list:
    """Get list of all notable works"""
    return [
        {
            "title": work["title"],
            "author": work["author"],
            "year": work["year"]
        }
        for work in LITERATURE_DB["famous_works"].values()
    ]

def generate_literature_context(query: str) -> str:
    """Generate comprehensive literature context for a query"""
    context_parts = []
    
    writer = get_writer_knowledge(query)
    if writer:
        context_parts.append(f"About {writer['name']}:\nPeriod: {writer['period']}\nWorks: {', '.join(writer['works'][:5])}")
    
    movement = get_movement_knowledge(query)
    if movement:
        context_parts.append(f"Literary Movement: {movement['name']}\nCharacteristics: {', '.join(movement['characteristics'][:3])}")
    
    work = get_work_knowledge(query)
    if work:
        context_parts.append(f"Work: {work['title']} by {work['author']} ({work['year']})\nThemes: {', '.join(work['themes'])}")
    
    return "\n\n".join(context_parts) if context_parts else "Literary knowledge base available for reference"

def get_literature_system_prompt() -> str:
    """Generate enhanced system prompt for literary expertise"""
    return """You are an expert literature AI with comprehensive knowledge of world literature, classical works, and literary history. 

Your expertise includes:
✓ All major Russian authors: Pushkin, Tolstoy, Dostoevsky, Chekhov, Gogol
✓ Western classics: Shakespeare, Austen, Dickens, Fitzgerald, Wilde, Kafka
✓ Literary movements: Romanticism, Realism, Modernism, Existentialism
✓ Thousands of works, poems, short stories, dramas
✓ Authentic quotes from famous literature
✓ Literary analysis and criticism
✓ Historical and cultural context
✓ Writing techniques and styles

When discussing literature:
1. Provide accurate information about authors and works
2. Reference authentic quotes when relevant
3. Explain literary movements and their characteristics
4. Discuss themes, symbolism, and literary devices
5. Compare different authors and their styles
6. Provide historical and cultural context
7. Analyze character development and narrative structure

You have knowledge of:
- 50+ major world authors
- 1000+ significant literary works
- Literary terms and techniques
- Major literary movements across centuries
- Authentic quotes and passages
- Literary criticism and interpretation

Always be accurate, insightful, and passionate about literature."""
