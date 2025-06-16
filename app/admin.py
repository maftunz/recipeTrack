from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import User as AuthUser
from django.utils.html import format_html, format_html_join
from django_json_widget.widgets import JSONEditorWidget
from django import forms
import uuid
from .models import (
    Region, Organization, User, Admin, Receipt, InviteLink, Giveaway, Product
)
import django.contrib.auth.models as auth_models

bot_username = 'shifokor_soft_bot'

admin.site.unregister(auth_models.Group)
admin.site.unregister(auth_models.User)


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_ru', 'name_uz')
    search_fields = ('name_ru', 'name_uz')
    readonly_fields = ('created_at', 'updated_at')
    actions = None
    ordering = ("-created_at",)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'region', 'type', 'created_at')
    list_filter = ('type', 'region')
    search_fields = ('name',)
    actions = None
    ordering = ("-created_at",)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'telegram_id', 'phone', 'user_type', 'organization', 'is_active')
    list_filter = ('user_type', 'is_active', 'language')
    search_fields = ('full_name', 'phone', 'telegram_id')
    actions = None
    ordering = ("-created_at",)

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
    actions = None
    ordering = ("-created_at",)

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


class ReceiptAdminForm(forms.ModelForm):
    class Meta:
        model = Receipt
        fields = "__all__"
        widgets = {
            "items": JSONEditorWidget
        }

@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    # form = ReceiptAdminForm
    list_display = ('id', 'user', 'organization', 'display_items', 'type', 'status', 'quantity', 'amount', 'ofd_url',
                    'updated_by', 'comment', 'created_at')
    list_filter = ('status', 'type',)
    search_fields = ('user__full_name',)
    readonly_fields = ('display_items', 'photo_preview', 'created_at', 'updated_at')
    exclude = ('updated_by',)
    actions = None
    ordering = ("-created_at",)

    def save_model(self, request, obj, form, change):
        if change:
            admin_user = Admin.objects.filter(user=request.user).first()
            if admin_user:
                obj.updated_by = admin_user
        super().save_model(request, obj, form, change)

    def photo_preview(self, obj):
        if obj.photo:
            photo_path = obj.photo
            if photo_path.startswith("media/"):
                photo_path = photo_path[len("media/"):]
            return format_html(
                '<img src="{}{}" style="max-height: 600px;" />',
                settings.MEDIA_URL,
                photo_path
            )
        return "Нет изображения"

    def display_items(self, obj):
        if not obj.items:
            return "-"
        return format_html_join(
            '<br>',
            '{} (x{}, {} сум)',
            ((item['name'], item['qty'], item['price_sum']) for item in obj.items)
        )

    display_items.short_description = "Продукты"
    photo_preview.short_description = "Фото чека/рецепта"


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


@admin.register(Giveaway)
class GiveawayAdmin(admin.ModelAdmin):
    list_display = ("title", "prize_amount", "winner_criteria", "user_type", "date_from", "date_to", "created_at")
    list_filter = ("winner_criteria", "user_type", "date_from", "date_to")
    search_fields = ("title",)
    ordering = ("-created_at",)
    actions = None

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('-created_at',)
    actions = None