import { Telegraf } from 'telegraf';
import { writersKnowledge, systemPromptTemplate } from './writers-knowledge.js';
import { OpenAI } from 'openai';

const bot = new Telegraf(process.env.TELEGRAM_BOT_TOKEN);

const openai = new OpenAI({
  apiKey: process.env.OPENROUTER_API_KEY,
  baseURL: 'https://openrouter.io/api/v1',
});

// Store user sessions
const userSessions = {}; // { userId: { writerId, conversationHistory, corrections } }
const userCorrections = {}; // { userId: [ corrections ] }

// Get writer list
const writers = Object.keys(writersKnowledge).map(key => ({
  id: key,
  name: writersKnowledge[key].name
}));

// Start command
bot.start((ctx) => {
  ctx.reply(
    '👋 Добро пожаловать! Я могу познакомить вас с великими писателями.\n\n' +
    'Выберите писателя для беседы:',
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
    '/start - Начать беседу с писателем\n' +
    '/help - Эта справка\n' +
    '/stats - Статистика обучений\n' +
    '/about - Информация о текущем писателе\n\n' +
    '*Система обучения:*\n' +
    'Если я ошибся, ответьте: ❌ [правильный ответ]\n' +
    'Если ответ был верный: ✅\n',
    { parse_mode: 'Markdown' }
  );
});

// Stats command
bot.command('stats', (ctx) => {
  const userId = ctx.from.id;
  const corrections = userCorrections[userId] || [];
  
  ctx.reply(
    `📊 *Статистика:*\n\n` +
    `Всего исправлений: ${corrections.length}\n` +
    `Текущий писатель: ${userSessions[userId]?.writerId ? writersKnowledge[userSessions[userId].writerId].name : 'Не выбран'}\n`,
    { parse_mode: 'Markdown' }
  );
});

// About command
bot.command('about', (ctx) => {
  const userId = ctx.from.id;
  const session = userSessions[userId];
  
  if (!session || !session.writerId) {
    ctx.reply('Выберите писателя сначала!');
    return;
  }
  
  const writer = writersKnowledge[session.writerId];
  ctx.reply(
    `*${writer.name}*\n\n` +
    `${writer.fullBio}\n\n` +
    `*Основные произведения:*\n${Object.keys(writer.majorWorks).join(', ')}\n\n` +
    `*Темы:*\n${writer.themes.join(', ')}`,
    { parse_mode: 'Markdown' }
  );
});

// Writer selection
bot.on('callback_query', async (ctx) => {
  const data = ctx.callbackQuery.data;
  const userId = ctx.from.id;
  
  if (data.startsWith('writer_')) {
    const writerId = data.replace('writer_', '');
    
    if (!writersKnowledge[writerId]) {
      ctx.answerCbQuery('Писатель не найден');
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
    
    ctx.answerCbQuery();
    ctx.reply(`✅ Вы выбрали *${writer.name}*\n\n${greeting}`, {
      parse_mode: 'Markdown'
    });
  }
  
  if (data.startsWith('feedback_')) {
    const [, action, msgId] = data.split('_');
    ctx.answerCbQuery();
    
    if (action === 'correct') {
      ctx.reply('✅ Спасибо! Ответ был верным.');
    } else if (action === 'incorrect') {
      ctx.reply(
        'Понял, я ошибся. Напишите правильный ответ в формате:\n' +
        '❌ [правильный ответ]'
      );
    }
  }
});

// Handle text messages
bot.on('message', async (ctx) => {
  const userId = ctx.from.id;
  const message = ctx.message.text;
  
  // Handle feedback
  if (message.startsWith('✅')) {
    ctx.reply('Спасибо за подтверждение! 😊');
    return;
  }
  
  if (message.startsWith('❌')) {
    const correction = message.replace('❌', '').trim();
    
    const session = userSessions[userId];
    if (!session || !session.writerId) {
      ctx.reply('Выберите писателя сначала с /start');
      return;
    }
    
    if (!correction) {
      ctx.reply('Пожалуйста, напишите правильный ответ после ❌');
      return;
    }
    
    // Store correction
    if (!userCorrections[userId]) {
      userCorrections[userId] = [];
    }
    
    userCorrections[userId].push({
      writerId: session.writerId,
      correction,
      timestamp: new Date().toISOString()
    });
    
    ctx.reply(
      `✅ Спасибо за исправление! Я запомнил это и буду учитывать в будущих ответах.\n\n` +
      `📚 Всего исправлений: ${userCorrections[userId].length}`
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
  ctx.sendChatAction('typing');
  
  try {
    // Build learning context
    let learningContext = '';
    const corrections = userCorrections[userId] || [];
    const writerCorrections = corrections
      .filter(c => c.writerId === session.writerId)
      .slice(-5);
    
    if (writerCorrections.length > 0) {
      learningContext = `PREVIOUS CORRECTIONS FROM USER (LEARN FROM THESE):\n${writerCorrections
        .map(c => `- Correct answer: "${c.correction}"`)
        .join('\n')}\n`;
    }
    
    // Create system prompt
    const systemPrompt = systemPromptTemplate(session.writerId, learningContext);
    
    // Prepare messages
    const messages = [
      ...session.conversationHistory.slice(-10), // Keep last 10 messages for context
      { role: 'user', content: message }
    ];
    
    // Get response from Claude
    const response = await openai.chat.completions.create({
      model: 'anthropic/claude-3.5-sonnet',
      messages: [
        { role: 'system', content: systemPrompt },
        ...messages
      ],
      temperature: 0.8,
      max_tokens: 1500,
    });
    
    const assistantMessage = response.choices[0].message.content;
    
    // Store in conversation history
    session.conversationHistory.push({
      role: 'user',
      content: message
    });
    session.conversationHistory.push({
      role: 'assistant',
      content: assistantMessage
    });
    
    // Split long messages if needed (Telegram has character limit)
    const chunks = chunkMessage(assistantMessage, 4096);
    
    for (const chunk of chunks) {
      await ctx.reply(chunk, {
        reply_markup: {
          inline_keyboard: [
            [
              { text: '✅ Верно', callback_data: `feedback_correct_${Date.now()}` },
              { text: '❌ Ошибка', callback_data: `feedback_incorrect_${Date.now()}` }
            ]
          ]
        }
      });
    }
    
  } catch (error) {
    console.error('Error:', error);
    ctx.reply('❌ Произошла ошибка при обработке вашего сообщения. Попробуйте ещё раз.');
  }
});

// Helper function to split long messages
function chunkMessage(text, maxLength) {
  const chunks = [];
  let currentChunk = '';
  
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
  
  return chunks.length > 0 ? chunks : [text];
}

// Start bot
console.log('🤖 Telegram bot запускается...');
bot.launch();

console.log('✅ Telegram бот запущен!');
console.log('Бот ожидает сообщений...');

// Enable graceful stop
process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));
