from django.db import models

class Region(models.Model):
    name_ru = models.CharField(max_length=100, unique=True, verbose_name="Название Ру")
    name_uz = models.CharField(max_length=100, unique=True, verbose_name="Название Уз")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return self.name_ru

    class Meta:
        verbose_name = "Регион"
        verbose_name_plural = "Регионы"