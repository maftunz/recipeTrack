from django.db import models
from django.contrib.auth.models import User as AuthUser

from app.enums import Language


class Admin(models.Model):
    user = models.OneToOneField(AuthUser, on_delete=models.CASCADE, null=True, blank=True)
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True, verbose_name="Telegram ID")
    full_name = models.CharField(max_length=255, verbose_name="ФИО")
    username = models.CharField(max_length=255, verbose_name="Юзернейм")
    password = models.CharField(max_length=128, verbose_name="Пароль")
    language = models.CharField(
        max_length=10,
        choices=Language.choices,
        null=True,
        blank=True,
        verbose_name = "Язык"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Админ"
        verbose_name_plural = "Админы"