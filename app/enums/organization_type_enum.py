from django.db.models import TextChoices

class OrganizationType(TextChoices):
    PHARMACY = 'pharmacy', 'Аптека'
    MEDICAL_INSTITUTION = 'medical_institution', 'Медицинское учреждение'