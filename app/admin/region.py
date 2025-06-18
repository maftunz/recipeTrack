from django.contrib import admin
from ..models import Region

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_ru', 'name_uz')
    search_fields = ('name_ru', 'name_uz')
    readonly_fields = ('created_at', 'updated_at')
    actions = None
    ordering = ("-created_at",)
