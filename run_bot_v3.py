#!/usr/bin/env python3
"""
Quick launcher for Bot v3.0
Быстрый запуск бота v3.0
"""
import sys
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("\n" + "="*80)
print("🚀 LITERARY BOT v3.0 - LAUNCHING")
print("="*80)

try:
    from bot_v3 import main, bot, dp
    from config import BOT_TOKEN
    
    print("\n✅ Imports successful")
    print("✅ Bot components loaded")
    
    if not BOT_TOKEN:
        print("\n❌ ERROR: BOT_TOKEN not set!")
        print("Please set your Telegram bot token in config.py")
        sys.exit(1)
    
    print("✅ Bot token found")
    print("\n" + "="*80)
    print("🧠 FEATURES ENABLED:")
    print("="*80)
    print("""
✅ Statistics Tracking - All user actions recorded
✅ Quiz Mode - Interactive literature questions  
✅ Recommendations - Personalized suggestions
✅ Achievements - Badge & reward system
✅ User Database - Persistent storage (user_data.json)
✅ History - All conversations saved
✅ FSM States - Smart conversation management
✅ Enhanced UI - Beautiful formatted messages
    """)
    
    print("="*80)
    print("🎮 AVAILABLE COMMANDS:")
    print("="*80)
    print("""
/start          - Main menu
/help           - Show help
/back           - Back to menu  
/stats          - Quick statistics
/clear          - Clear history
/quit           - Exit bot
    """)
    
    print("="*80)
    print("🎯 MODES:")
    print("="*80)
    print("""
❓ Questions       - Ask about literature
👥 Writers         - Talk with classics
🎯 Quiz            - Take quizzes
💡 Recommendations - Get suggestions
📊 Statistics      - View progress
🏆 Achievements    - Unlock badges
    """)
    
    print("="*80)
    print("▶️  STARTING BOT...")
    print("="*80 + "\n")
    
    asyncio.run(main())
    
except ImportError as e:
    print(f"\n❌ Import Error: {e}")
    print("Make sure all files are in the same directory")
    sys.exit(1)
except KeyboardInterrupt:
    print("\n\n👋 Bot stopped by user")
    sys.exit(0)
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

