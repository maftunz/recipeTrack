from django.db.models import TextChoices

class GiveawayUserType(TextChoices):
    ALL = 'all', 'Все'
    DOCTOR = "doctor", 'Врачи'
    PHARMACIST = "pharmacist", 'Фармацевты'