from django.db import models
from app.models.admin_user import Admin
from app.models.organization import Organization
from app.models.user import User


class InviteLink(models.Model):
    token = models.UUIDField(unique=True, verbose_name="Токен")
    invited_by = models.ForeignKey(Admin, null=True, blank=True, on_delete=models.SET_NULL,
                                   related_name='invites_created', verbose_name="Кем приглашен")
    used = models.BooleanField(default=False, verbose_name="Использовано")
    used_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Кем использовано")
    organization = models.ForeignKey(Organization, null=True, blank=True, on_delete=models.SET_NULL,
                                     verbose_name="Организация")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Приглашение"
        verbose_name_plural = "Приглашения"