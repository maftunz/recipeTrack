from django.db.models import TextChoices

class ReceiptType(TextChoices):
    PRESCRIPTION = 'prescription', 'Рецепт'
    CHECK = 'check', 'Чек'