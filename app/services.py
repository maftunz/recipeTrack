import os

from aiogram import Bot

from app.models import User


async def send_message_to_user(user_id: int, message: str):
    tg_bot = Bot(token=os.getenv("TELEGRAM_API_TOKEN"))
    user = User.objects.filter(id=user_id).first()
    if user.telegram_id:
        try:
            await tg_bot.send_message(chat_id=user.telegram_id, text=message)
        except Exception as e:
            print(f"Ошибка отправки Telegram-сообщения для {user.full_name}: {e}")