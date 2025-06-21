from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)

def start():
    scheduler = BackgroundScheduler(timezone="Asia/Tashkent")
    scheduler.add_job(
        select_giveaway_winners_job,
        trigger='cron',
        # hour=1,  # каждый день в 01:00
        # minute=0
        minute='*',
        second='10'
    )
    # scheduler.start()
    logger.info("APScheduler started.")

def select_giveaway_winners_job():
    try:
        call_command('select_giveaway_winners')
        logger.info("Розыгрыш завершён успешно.")
    except Exception as e:
        logger.error(f"Ошибка при запуске розыгрыша: {e}")
        raise e