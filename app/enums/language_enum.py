from django.db.models import TextChoices

class Language(TextChoices):
    RU = 'ru', 'Russian'
    UZ = 'uz', 'Uzbek'