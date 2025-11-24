import { Telegraf } from 'telegraf';
import { writersKnowledge, systemPromptTemplate } from './writers-knowledge.js';
import { trainingData, learningSystem } from './training-data.js';
import { worldLiterature, literatureSynthesis } from './world-literature.js';
import { OpenAI } from 'openai';

const bot = new Telegraf(process.env.TELEGRAM_BOT_TOKEN);

const openai = new OpenAI({
  apiKey: process.env.OPENROUTER_API_KEY,
  baseURL: 'https://openrouter.io/api/v1',
  defaultHeaders: {
    'HTTP-Referer': 'https://replit.com',
    'X-Title': 'Writer Chat Bot'
  }
});

// Store user sessions
const userSessions = {}; // { userId: { writerId, conversationHistory, corrections } }
const userCorrections = {}; // { userId: [ corrections with HIGH priority ] }
const globalLearnings = {}; // { writerId: [ all learned facts ] } - persistent learning

// Get writer list
const writers = Object.keys(writersKnowledge).map(key => ({
  id: key,
  name: writersKnowledge[key].name
}));

// Enhanced system prompt with aggressive self-correction and learning
const enhancedSystemPrompt = (writerId, learningContext, userLearnings) => {
  const basePrompt = systemPromptTemplate(writerId, learningContext);
  const training = trainingData[writerId];
  
  // Get world literature context - about other writers and genres
  let worldLitContext = '';
  if (trainingData[writerId]) {
    // Get related world literature knowledge
    const writerLit = worldLiterature.ancient || {};
    const hasInfo = Object.keys(worldLiterature).filter(k => k !== 'ancient' && k !== 'renaissance' && k !== 'enlightenment_romanticism' && k !== 'realism_19' && k !== 'russian_golden_age' && k !== 'twentieth_century' && k !== 'global_literature' && k !== 'literary_movements' && k !== 'genres' && k !== 'universal_themes' && k !== 'contemporary_21st' && k !== 'famous_quotes' && k !== 'literatureSynthesis');
    
    worldLitContext = `\n\nWORLD LITERATURE CONTEXT:
You have comprehensive knowledge of world literature including:
- Ancient literature: Homer (Iliad, Odyssey), Dante, Greek dramatists
- Renaissance & Enlightenment: Goethe, Austen, Molière
- 19th Century Realism: Balzac, Dickens, Flaubert
- Russian Golden Age: Tolstoy, Dostoevsky, Chekhov
- Modernism: Joyce, Woolf, Kafka, Faulkner, Hemingway
- Latin American & Global: Márquez, Borges, Achebe, Morrison
- Universal themes: Love, death, power, freedom, identity, redemption

You can discuss how this writer relates to other writers and literary movements.`;
  }
  
  return `${basePrompt}

MANDATORY TRAINING DATA FOR THIS WRITER:
${training ? Object.entries(training.dates || {}).map(([work, dates]) => 
  `• ${work}: ${JSON.stringify(dates)}`).join('\n') : ''}

${training && training.detailedFacts ? `CRITICAL BIOGRAPHICAL FACTS:
${training.detailedFacts.slice(0, 8).map(f => `✓ ${f}`).join('\n')}
` : ''}

${training && training.characters ? `CHARACTER KNOWLEDGE:
${Object.entries(training.characters).map(([work, chars]) => 
  `• ${work}: ${chars.join(', ')}`).join('\n')}
` : ''}${worldLitContext}

SELF-CORRECTION & LEARNING PROTOCOL:
1. BEFORE answering ANY factual question - VERIFY against your knowledge
2. Check dates, names, character names, plot details - be PRECISE
3. If uncertain - ADMIT IT rather than guess
4. If you made an error in previous responses - SELF-CORRECT immediately
5. Use phrases: "Upon reflection...", "Let me verify...", "I should clarify..."
6. Learn from user corrections - integrate them into ALL future responses
7. If user corrects you - acknowledge and remember for similar questions

AGGRESSIVE ACCURACY MODE:
- You are trusted to teach people about these writers and world literature
- Factual errors are NOT acceptable
- Always prioritize accuracy over brevity
- Double-check information from the training data above
- When discussing other writers, ensure accuracy to your best knowledge`;
};

// Start command
bot.start((ctx) => {
  ctx.reply(
    '👋 Добро пожаловать! Я помогу вам поговорить с великими писателями.\n\n' +
    '📚 Выберите писателя для беседы:',
    {
      reply_markup: {
        inline_keyboard: writers.map(writer => [
          { text: writer.name, callback_data: `writer_${writer.id}` }
        ])
      }
    }
  );
});

// Help command
bot.help((ctx) => {
  ctx.reply(
    '📚 *Команды:*\n\n' +
    '/start - Выбрать писателя\n' +
    '/help - Справка\n' +
    '/stats - Статистика\n' +
    '/about - О писателе\n\n' +
    '*Обучение нейронки:*\n' +
    '✅ - Ответ правильный\n' +
    '❌ [ответ] - Исправление\n\n' +
    '*🌍 База знаний бота включает:*\n' +
    '• 5 основных писателей\n' +
    '• Древнюю литературу (Гомер, Данте)\n' +
    '• Эпоху Возрождения (Шекспир, Мольер)\n' +
    '• Просвещение (Гёте, Остен, Гюго)\n' +
    '• XIX век (Балзак, Диккенс, Флобер)\n' +
    '• Модернизм (Кафка, Джойс, Вулф)\n' +
    '• XX-XXI века (Маркес, Мураками)\n' +
    '• Африканскую, латиноамериканскую, азиатскую литературу\n\n' +
    '_Примечание: нейронка самокорректируется и учится от вас_',
    { parse_mode: 'Markdown' }
  );
});

// Stats command
bot.command('stats', (ctx) => {
  const userId = ctx.from.id;
  const corrections = userCorrections[userId] || [];
  const currentWriter = userSessions[userId]?.writerId;
  
  let statsText = `📊 *Статистика обучения:*\n\n`;
  statsText += `Всего исправлений: ${corrections.length}\n`;
  
  if (currentWriter) {
    const writerCorrections = corrections.filter(c => c.writerId === currentWriter);
    statsText += `Исправлений для ${writersKnowledge[currentWriter].name}: ${writerCorrections.length}\n`;
  }
  
  if (corrections.length > 0) {
    statsText += `\n_Нейронка улучшается!_ 🧠`;
  }
  
  ctx.reply(statsText, { parse_mode: 'Markdown' });
});

// About command
bot.command('about', (ctx) => {
  const userId = ctx.from.id;
  const session = userSessions[userId];
  
  if (!session || !session.writerId) {
    ctx.reply('Выберите писателя сначала с /start');
    return;
  }
  
  const writer = writersKnowledge[session.writerId];
  let aboutText = `*${writer.name}*\n\n`;
  aboutText += `${writer.fullBio}\n\n`;
  aboutText += `*Произведения:*\n`;
  aboutText += Object.keys(writer.majorWorks).slice(0, 5).join(', ');
  
  ctx.reply(aboutText, { parse_mode: 'Markdown' });
});

// Writer selection
bot.on('callback_query', async (ctx) => {
  const data = ctx.callbackQuery.data;
  const userId = ctx.from.id;
  
  if (data.startsWith('writer_')) {
    const writerId = data.replace('writer_', '');
    
    if (!writersKnowledge[writerId]) {
      ctx.answerCbQuery('❌ Писатель не найден');
      return;
    }
    
    // Initialize user session
    userSessions[userId] = {
      writerId,
      conversationHistory: []
    };
    
    if (!userCorrections[userId]) {
      userCorrections[userId] = [];
    }
    
    const writer = writersKnowledge[writerId];
    const greeting = `Здравствуйте! Я ${writer.name}. Рад познакомиться с вами. Чем я могу вам помочь? Спрашивайте о моих произведениях, жизни или литературе в целом!`;
    
    userSessions[userId].conversationHistory.push({
      role: 'assistant',
      content: greeting
    });
    
    ctx.answerCbQuery('✅ Писатель выбран');
    ctx.reply(`✨ *${writer.name}*\n\n${greeting}`, {
      parse_mode: 'Markdown'
    });
  }
  
  if (data.startsWith('feedback_')) {
    const [, action] = data.split('_');
    ctx.answerCbQuery();
    
    if (action === 'correct') {
      ctx.reply('✅ Спасибо за подтверждение! Я рад, что мой ответ был полезен.');
    } else if (action === 'incorrect') {
      ctx.reply(
        '❌ Помогите мне улучшиться! Ответьте в формате:\n\n' +
        '`❌ [ваш правильный ответ или уточнение]`\n\n' +
        '_Например: ❌ На самом деле это произведение написано в 1860 году_',
        { parse_mode: 'Markdown' }
      );
    }
  }
});

// Handle text messages
bot.on('message', async (ctx) => {
  const userId = ctx.from.id;
  const message = ctx.message.text;
  
  if (!message) return;
  
  // Handle feedback
  if (message.startsWith('✅')) {
    ctx.reply('Спасибо за подтверждение! 😊');
    return;
  }
  
  if (message.startsWith('❌')) {
    const fullText = message.replace('❌', '').trim();
    
    const session = userSessions[userId];
    if (!session || !session.writerId) {
      ctx.reply('Выберите писателя сначала с /start');
      return;
    }
    
    if (!fullText) {
      ctx.reply('Пожалуйста, напишите правильный ответ после ❌');
      return;
    }
    
    // Store correction with user's original question
    if (!userCorrections[userId]) {
      userCorrections[userId] = [];
    }
    
    // Get the last user question from conversation history
    let lastQuestion = 'Вопрос неизвестен';
    if (session.conversationHistory && session.conversationHistory.length > 0) {
      for (let i = session.conversationHistory.length - 1; i >= 0; i--) {
        if (session.conversationHistory[i].role === 'user') {
          lastQuestion = session.conversationHistory[i].content;
          break;
        }
      }
    }
    
    const correction = {
      writerId: session.writerId,
      userMessage: lastQuestion,
      correction: fullText,
      timestamp: new Date().toISOString(),
      userId: userId,
      priority: 'critical'
    };
    
    userCorrections[userId].push(correction);
    
    // Also store in global learnings for all users
    if (!globalLearnings[session.writerId]) {
      globalLearnings[session.writerId] = [];
    }
    globalLearnings[session.writerId].push(`When asked about: "${lastQuestion}" → Answer: "${fullText}"`);
    
    const totalCorrections = userCorrections[userId].length;
    const writerCorrections = userCorrections[userId].filter(c => c.writerId === session.writerId).length;
    
    ctx.reply(
      `✅ *Спасибо за исправление!* Я запомнил это.\n\n` +
      `📊 *Статистика обучения:*\n` +
      `• Ваши исправления: ${totalCorrections}\n` +
      `• Для ${writersKnowledge[session.writerId].name}: ${writerCorrections}\n\n` +
      `🧠 *Я стану более точным благодаря вам!*\n` +
      `💡 Это исправление будет использоваться в следующих ответах`,
      { parse_mode: 'Markdown' }
    );
    return;
  }
  
  // Regular message - get response from AI
  const session = userSessions[userId];
  if (!session || !session.writerId) {
    ctx.reply(
      'Выберите писателя для начала беседы:',
      {
        reply_markup: {
          inline_keyboard: writers.map(writer => [
            { text: writer.name, callback_data: `writer_${writer.id}` }
          ])
        }
      }
    );
    return;
  }
  
  // Show typing indicator
  await ctx.sendChatAction('typing');
  
  try {
    // Build learning context with MAXIMUM emphasis on corrections
    let learningContext = '';
    let globalContext = '';
    
    const corrections = userCorrections[userId] || [];
    const writerCorrections = corrections
      .filter(c => c.writerId === session.writerId)
      .slice(-15); // Use last 15 corrections for better learning
    
    // Global learnings across all users
    const globalWriterLearnings = globalLearnings[session.writerId] || [];
    
    if (writerCorrections.length > 0) {
      learningContext = `CRITICAL - USER'S PERSONAL CORRECTIONS (HIGHEST PRIORITY):\n`;
      writerCorrections.forEach((c, idx) => {
        learningContext += `${idx + 1}. USER SAID: "${c.userMessage}"\n`;
        learningContext += `   CORRECT ANSWER: "${c.correction}"\n`;
        learningContext += `   → USE THIS IN ALL SIMILAR QUESTIONS\n\n`;
      });
    }
    
    if (globalWriterLearnings.length > 0) {
      globalContext = `GLOBAL COMMUNITY CORRECTIONS (EVERYONE'S LEARNINGS):\n`;
      globalWriterLearnings.slice(-5).forEach((fact, idx) => {
        globalContext += `${idx + 1}. ${fact}\n`;
      });
    }
    
    const finalContext = learningContext + (globalContext ? '\n' + globalContext : '');
    
    // Create enhanced system prompt with training data
    const systemPrompt = enhancedSystemPrompt(session.writerId, finalContext, globalWriterLearnings);
    
    // Prepare messages - include more conversation history for better context
    const messages = [
      ...session.conversationHistory.slice(-15), // Increased from 10 to 15
      { role: 'user', content: message }
    ];
    
    // Get response from Claude with retry logic
    let response;
    let retries = 3;
    
    while (retries > 0) {
      try {
        response = await openai.chat.completions.create({
          model: 'anthropic/claude-3.5-sonnet',
          messages: [
            { role: 'system', content: systemPrompt },
            ...messages
          ],
          temperature: 0.7, // Slightly lower for more accuracy
          max_tokens: 2000, // Increased to allow self-corrections
        });
        break;
      } catch (apiError) {
        retries--;
        if (retries === 0) throw apiError;
        console.log(`Retry attempt, ${retries} left...`);
        await new Promise(r => setTimeout(r, 1000)); // Wait before retry
      }
    }
    
    let assistantMessage = response.choices[0].message.content;
    
    // Post-process: Check if AI made obvious corrections
    if (assistantMessage.toLowerCase().includes('upon reflection') ||
        assistantMessage.toLowerCase().includes('let me correct') ||
        assistantMessage.toLowerCase().includes('i should clarify')) {
      // AI already self-corrected, good!
      console.log('AI self-corrected message');
    }
    
    // Store in conversation history
    session.conversationHistory.push({
      role: 'user',
      content: message
    });
    session.conversationHistory.push({
      role: 'assistant',
      content: assistantMessage
    });
    
    // Limit conversation history to prevent memory issues
    if (session.conversationHistory.length > 50) {
      session.conversationHistory = session.conversationHistory.slice(-50);
    }
    
    // Split long messages if needed
    const chunks = chunkMessage(assistantMessage, 4090);
    
    for (const chunk of chunks) {
      await ctx.reply(chunk, {
        parse_mode: 'Markdown',
        reply_markup: {
          inline_keyboard: [
            [
              { text: '✅ Верно', callback_data: `feedback_correct_${Date.now()}` },
              { text: '❌ Ошибка', callback_data: `feedback_incorrect_${Date.now()}` }
            ]
          ]
        }
      });
      
      // Small delay between messages to avoid rate limiting
      await new Promise(r => setTimeout(r, 100));
    }
    
  } catch (error) {
    console.error('Error:', error);
    let errorMsg = '❌ Произошла ошибка при обработке вашего сообщения.';
    
    if (error.status === 405) {
      errorMsg += '\n\n⚠️ Ошибка API (405). Проверьте конфигурацию.';
    } else if (error.status === 401) {
      errorMsg += '\n\n⚠️ Ошибка аутентификации. Проверьте токен OpenRouter.';
    }
    
    await ctx.reply(errorMsg);
  }
});

// Helper function to split long messages
function chunkMessage(text, maxLength) {
  if (text.length <= maxLength) return [text];
  
  const chunks = [];
  let currentChunk = '';
  
  // Try to split by paragraphs first
  const paragraphs = text.split('\n\n');
  
  for (const paragraph of paragraphs) {
    if ((currentChunk + paragraph + '\n\n').length > maxLength) {
      if (currentChunk) chunks.push(currentChunk.trim());
      currentChunk = paragraph + '\n\n';
    } else {
      currentChunk += paragraph + '\n\n';
    }
  }
  
  if (currentChunk) chunks.push(currentChunk.trim());
  
  // If still too long, split by sentences
  if (chunks.some(c => c.length > maxLength)) {
    chunks = [];
    currentChunk = '';
    const sentences = text.match(/[^.!?]+[.!?]+/g) || [text];
    
    for (const sentence of sentences) {
      if ((currentChunk + sentence).length > maxLength) {
        if (currentChunk) chunks.push(currentChunk.trim());
        currentChunk = sentence;
      } else {
        currentChunk += sentence;
      }
    }
    if (currentChunk) chunks.push(currentChunk.trim());
  }
  
  return chunks.length > 0 ? chunks : [text];
}

// Start bot with error handling
console.log('🤖 Telegram бот запускается...');

bot.launch({
  polling: {
    timeout: 30,
    limit: 100,
    allowed_updates: ['message', 'callback_query']
  }
});

console.log('✅ Telegram бот запущен и слушает сообщения!');
console.log('📚 Писатели: ' + writers.map(w => w.name).join(', '));

// Enable graceful stop
process.once('SIGINT', () => {
  console.log('Shutting down bot...');
  bot.stop('SIGINT');
});
process.once('SIGTERM', () => {
  console.log('Shutting down bot...');
  bot.stop('SIGTERM');
});
