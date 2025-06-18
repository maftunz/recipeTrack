from django.contrib import admin
from django.contrib.auth.models import User as AuthUser
from django import forms
from ..models import Admin

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
