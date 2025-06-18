from django.contrib import admin
from ..models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'telegram_id', 'phone', 'user_type', 'organization', 'is_active')
    list_filter = ('user_type', 'is_active', 'language')
    search_fields = ('full_name', 'phone', 'telegram_id')
    actions = None
    ordering = ("-created_at",)
