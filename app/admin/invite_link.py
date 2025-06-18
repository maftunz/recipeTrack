from django.contrib import admin
from django import forms
from django.utils.html import format_html
import uuid

from ..models import InviteLink, Organization, Admin

bot_username = 'dorixonasoft_bot'

class InviteLinkForm(forms.ModelForm):
    class Meta:
        model = InviteLink
        fields = ['organization']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['organization'].queryset = Organization.objects.all()

@admin.register(InviteLink)
class InviteLinkAdmin(admin.ModelAdmin):
    form = InviteLinkForm
    list_display = ('id', 'invite_link', 'token', 'invited_by', 'organization', 'used', 'used_by', 'created_at')
    list_filter = ('used', 'organization')
    search_fields = ('token', 'used_by__full_name')
    readonly_fields = ('token', 'created_at', 'updated_at')
    actions = None
    ordering = ("-created_at",)

    def invite_link(self, obj):
        return format_html(
            f'<a href="https://t.me/{bot_username}?start={obj.token}" target="_blank">Invite Link</a>'
        )

    invite_link.short_description = "Invite Link"

    def save_model(self, request, obj, form, change):
        if not obj.token:
            obj.token = uuid.uuid4()

        if not obj.invited_by:
            try:
                obj.invited_by = Admin.objects.filter(username=request.user.username).first();
            except Admin.DoesNotExist:
                pass

        super().save_model(request, obj, form, change)
