from django.utils.html import format_html

from django.contrib import admin
from django.contrib.auth.models import User as AuthUser
from django import forms
import uuid
from .models import (
    Region, Organization, User, Admin, Receipt, InviteLink
)

bot_username = 'recipe_track_bot'


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_ru', 'name_uz')
    search_fields = ('name_ru', 'name_uz')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'region', 'type', 'created_at')
    list_filter = ('type', 'region')
    search_fields = ('name',)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'telegram_id', 'phone', 'user_type', 'organization', 'is_active')
    list_filter = ('user_type', 'is_active', 'language')
    search_fields = ('full_name', 'phone', 'telegram_id')

class AdminCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), label="Password")

    class Meta:
        model = Admin
        fields = ['telegram_id', 'full_name', 'username', 'password', 'language']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['telegram_id'].required = False

@admin.register(Admin)
class AdminAdmin(admin.ModelAdmin):
    form = AdminCreationForm
    list_display = ('id', 'username', 'full_name', 'telegram_id', 'language')
    search_fields = ('username', 'full_name', 'telegram_id')

    def save_model(self, request, obj, form, change):
        if not obj.user:
            auth_user = AuthUser(
                username=obj.username,
                is_staff = True,  # даём доступ в админку
                is_superuser = True  # если нужно сделать суперюзером — поставь True
            )
            auth_user.set_password(form.cleaned_data['password'])
            auth_user.save()
            obj.user = auth_user

        super().save_model(request, obj, form, change)


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'amount', 'updated_by', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__full_name',)
    readonly_fields = ('created_at', 'updated_at')


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