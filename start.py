#!/usr/bin/env python3
import subprocess
import sys

# Устанавливаем зависимости
print("📦 Installing dependencies...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

# Запускаем бота
print("🚀 Starting bot...")
from bot import main
if __name__ == "__main__":
    main()
