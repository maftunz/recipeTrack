import os
import asyncio
import django
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.fsm.strategy import FSMStrategy
from aiogram.fsm.storage.memory import MemoryStorage

from botapp.handlers.registration import registration_router

# Настройка Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "recipe_track.settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()

# Загрузка токена
load_dotenv()
API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")

# Создание бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage, fsm_strategy=FSMStrategy.CHAT)

# Подключение маршрутов
dp.include_router(registration_router)

# Основной запуск
async def main():
    print("Bot is starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())