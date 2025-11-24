# Literary Genius Bot

## Overview
A Telegram bot that serves as an expert guide to world literature, providing in-depth knowledge about great writers, their works, and literary movements. The bot offers two modes: Expert mode for scholarly discussions and Dialogue mode to converse with writers as historical figures.

## Project Structure
- `bot.py` - Main Telegram bot handler with command routing
- `start.py` - Entry point for running the bot
- `universal_brain.py` - AI brain using Claude 3.5 Sonnet via OpenRouter API
- `literary_knowledge.py` - Literature search and analysis functions
- `coprehensive_knowledge.py` - Comprehensive database of writers and works
- `writers/` - JSON files with detailed information about each writer
- `config.py` - Configuration and environment variables
- `ai_openrouter.py` - OpenRouter API integration
- `neural_writer.py` - Advanced writer styling module
- `wikipedia_loader.py` - Wikipedia data integration
- `keep_alive.py` - Server keep-alive functionality

## Current Status
- ✅ All Python dependencies installed
- ✅ Project structure verified
- ⏳ Awaiting Telegram BOT_TOKEN and OpenRouter API key setup

## Recent Changes
- Created literary_knowledge.py module
- Fixed import structure for bot.py
- Updated .gitignore for Python project

## Next Steps
1. User must provide BOT_TOKEN (Telegram) and OPENROUTER_API_KEY
2. Start the bot with `python start.py`
3. Test with Telegram

## Dependencies
- aiogram 3.22.0 - Telegram bot framework
- python-dotenv 1.2.1 - Environment variable management
- aiohttp 3.12.15 - Async HTTP client
- beautifulsoup4 4.14.2 - HTML parsing
- wikipedia-api 0.8.1 - Wikipedia data access
- requests 2.32.5 - HTTP requests
- flask 2.3.3 - Web framework

## User Preferences
- Language: Russian
- Bot personality: Expert in world literature
- Architecture: Async Python with Telegram bot framework
