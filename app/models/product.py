from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Название продукта")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return f"{self.name} – {self.price}"

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"