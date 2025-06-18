from django.db import models

from app.enums import ReceiptType, ReceiptStatus
from app.models.admin_user import Admin
from app.models.organization import Organization
from app.models.user import User


class Receipt(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, verbose_name="Пользователь")
    organization = models.ForeignKey(Organization, null=True, on_delete=models.SET_NULL, verbose_name="Организация")
    photo = models.CharField(max_length=255, verbose_name="Фото")
    ofd_url = models.CharField(max_length=255, null=True, blank=True, verbose_name="Ссылка Soliq")
    items = models.JSONField(null=True, blank=True, verbose_name="Продукты")
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Сумма")
    quantity = models.PositiveIntegerField(null=True, blank=True, verbose_name="Количество")
    type = models.CharField(
        max_length=20,
        choices=ReceiptType.choices,
        null=True,
        blank=True,
        verbose_name="Тип"
    )
    status = models.CharField(
        max_length=20,
        choices=ReceiptStatus.choices,
        default=ReceiptStatus.PENDING,
        verbose_name="Статус"
    )
    updated_by = models.ForeignKey(Admin, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Кем обновлено")
    comment = models.CharField(max_length=255, null=True, blank=True, verbose_name="Комментарий")
    created_at = models.DateTimeField(verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Рецепт/Чек"
        verbose_name_plural = "Рецепты/Чеки"