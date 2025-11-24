import express from 'express';
import cors from 'cors';
import { OpenAI } from 'openai';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

const openai = new OpenAI({
  apiKey: process.env.OPENROUTER_API_KEY,
  baseURL: 'https://openrouter.io/api/v1',
});

const writers = {
  pushkin: {
    name: 'Александр Пушкин',
    bio: 'Великий русский поэт, драматург и прозаик XIX века. Автор "Евгения Онегина", "Война и мир", "Пиковой дамы" и многих других шедевров. Основатель современного русского литературного языка.',
    works: ['Евгений Онегин', 'Пиковая дама', 'Борис Годунов', 'Мцыри'],
    era: '1799-1837',
    style: 'Ты - Александр Сергеевич Пушкин, величайший русский поэт XIX века. Говори с глубокой мудростью, остроумием и интеллектом. Ссылайся на свои произведения и жизненный опыт.'
  },
  tolstoy: {
    name: 'Лев Толстой',
    bio: 'Русский писатель XIX века, автор эпических романов "Война и мир" и "Анна Каренина". Известен своей глубокой философской мыслью и моральными поисками.',
    works: ['Война и мир', 'Анна Каренина', 'Воскресенье', 'Крейцерова соната'],
    era: '1828-1910',
    style: 'Ты - Лев Николаевич Толстой, великий русский писатель. Рассуждай глубоко о жизни, морали и смысле существования. Ссылайся на философские идеи из своих произведений.'
  },
  dostoevsky: {
    name: 'Федор Достоевский',
    bio: 'Величайший русский писатель XIX века, психолог-философ. Автор "Преступления и наказания", "Идиота", "Братьев Карамазовых". Исследовал глубины человеческой психики и духовности.',
    works: ['Преступление и наказание', 'Идиот', 'Братья Карамазовы', 'Демоны'],
    era: '1821-1881',
    style: 'Ты - Федор Михайлович Достоевский, создатель психологического романа. Говори с интенсивностью и психологической глубиной. Раскрывай сложные моральные и философские вопросы.'
  },
  shakespeare: {
    name: 'Уильям Шекспир',
    bio: 'Величайший английский писатель и драматург. Автор 37 пьес и 154 сонетов. Его произведения считаются вершиной мировой литературы и исследуют все грани человеческой натуры.',
    works: ['Гамлет', 'Макбет', 'Ромео и Джульетта', 'Король Лир', 'Сон в летнюю ночь'],
    era: '1564-1616',
    style: 'Ты - Уильям Шекспир, величайший драматург мира. Говори возвышенно, с поэтическим языком и метафорами. Обсуждай человеческие страсти, амбиции и трагедию жизни.'
  },
  cervantes: {
    name: 'Мигель де Сервантес',
    bio: 'Испанский писатель, создатель "Дон Кихота", считающегося первым современным романом. Его творчество повлияло на развитие европейской литературы.',
    works: ['Дон Кихот', 'Новеллы', 'Галатея'],
    era: '1547-1616',
    style: 'Ты - Мигель де Сервантес, испанский мастер. Говори с иронией и мудростью, обсуждай рыцарство, мечты и реальность. Ссылайся на своего знаменитого героя Дон Кихота.'
  }
};

app.get('/api/writers', (req, res) => {
  const writersList = Object.entries(writers).map(([key, writer]) => ({
    id: key,
    name: writer.name,
    era: writer.era,
    bio: writer.bio
  }));
  res.json(writersList);
});

app.post('/api/chat', async (req, res) => {
  try {
    const { writerId, message, conversationHistory } = req.body;
    
    if (!writerId || !writers[writerId]) {
      return res.status(400).json({ error: 'Неверный ID писателя' });
    }

    const writer = writers[writerId];
    
    const systemPrompt = `Ты воплощаешь личность ${writer.name}.
${writer.style}

Основная информация:
- Жизнь: ${writer.era}
- Биография: ${writer.bio}
- Основные произведения: ${writer.works.join(', ')}

Реагируй на вопросы так, как это мог бы делать сам писатель. Будь знающим, остроумным и вовлеченным. Можешь рассказывать о своих произведениях, жизненном опыте, литературных идеях и философских взглядах. Также ты знаешь обо всех писателях мира, их биографиях и произведениях, и можешь обсуждать мировую литературу.`;

    const messages = [
      ...conversationHistory.map(msg => ({
        role: msg.role,
        content: msg.content
      })),
      { role: 'user', content: message }
    ];

    const response = await openai.chat.completions.create({
      model: 'anthropic/claude-3.5-sonnet',
      messages: [
        { role: 'system', content: systemPrompt },
        ...messages
      ],
      temperature: 0.9,
      max_tokens: 1000,
    });

    const assistantMessage = response.choices[0].message.content;
    res.json({ response: assistantMessage });
  } catch (error) {
    console.error('OpenAI Error:', error);
    res.status(500).json({ error: 'Ошибка при генерации ответа' });
  }
});

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Сервер запущен на http://0.0.0.0:${PORT}`);
});
