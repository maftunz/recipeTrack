from django.contrib import admin
from django.shortcuts import redirect
from app.models.statistics import UserStatisticsProxy

@admin.register(UserStatisticsProxy)
class UserStatisticsAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        return redirect('user_statistics')  # Переход по имени URL

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_model_perms(self, request):
        # Всегда отображать в админке
        return {'view': True}