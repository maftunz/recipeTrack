from app.models import User

class UserStatisticsProxy(User):
    class Meta:
        proxy = True
        verbose_name = "Статистика"
        verbose_name_plural = "Статистика"