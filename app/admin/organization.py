from django.contrib import admin
from ..models import Organization

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'region', 'type', 'created_at')
    list_filter = ('type', 'region')
    search_fields = ('name',)
    actions = None
    ordering = ("-created_at",)
