from django.db import models
from .organization import Organization
from ..enums import UserType, Language


class User(models.Model):
    telegram_id = models.BigIntegerField(unique=True, verbose_name="Telegram ID")
    phone = models.CharField(max_length=20, unique=True, verbose_name="Номер телефона")
    user_type = models.CharField(
        max_length=20,
        choices=[(u.value, u.label("ru")) for u in UserType],
        verbose_name="Тип пользователя"
    )
    full_name = models.CharField(max_length=255, verbose_name="ФИО")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    language = models.CharField(
        max_length=10,
        choices=Language.choices,
        null=True,
        blank=True,
        verbose_name="Язык"
    )
    organization = models.ForeignKey(Organization, null=True, on_delete=models.SET_NULL, verbose_name="Организация")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"