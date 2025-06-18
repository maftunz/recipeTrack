from django.db.models import TextChoices

class WinnerCriteria(TextChoices):
    BY_COUNT = 'count', 'По количеству'
    BY_TOTAL_AMOUNT = 'total_amount', 'По сумме'