from django.db import models

from app.enums import OrganizationType
from app.models.region import Region


class Organization(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Дата создания")
    type = models.CharField(max_length=50, choices=OrganizationType.choices, verbose_name="Тип организации")
    region = models.ForeignKey(Region, null=True, on_delete=models.SET_NULL, verbose_name="Регион")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Организация"
        verbose_name_plural = "Ораганизации"