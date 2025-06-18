from django.db import models

from app.enums import WinnerCriteria, GiveawayUserType


class Giveaway(models.Model):
    title = models.CharField(max_length=255,
                             null=True,
                             blank=True,
                             verbose_name="Название розыгрыша")
    prize_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма приза")
    date_from = models.DateField(verbose_name="Начало розыгрыша")
    date_to = models.DateField(verbose_name="Конец розыгрыша")

    winner_count = models.PositiveIntegerField(
        default=1,
        verbose_name="Количество победителей"
    )

    winner_criteria = models.CharField(
        max_length=20,
        choices=WinnerCriteria.choices,
        null=True,
        blank=True,
        verbose_name="Критерий выбора победителя"
    )

    user_type = models.CharField(
        max_length=20,
        choices=GiveawayUserType.choices,
        default=GiveawayUserType.ALL,
        verbose_name="Участники"
    )

    winner_data = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Победители"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Розыгрыш"
        verbose_name_plural = "Розыгрыши"