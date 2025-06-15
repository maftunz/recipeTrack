from django.db import models
from django.contrib.auth.models import User as AuthUser
from .enums import ReceiptStatus
from .enums import UserType
from .enums import OrganizationType
from .enums import Language


class Admin(models.Model):
    user = models.OneToOneField(AuthUser, on_delete=models.CASCADE, null=True, blank=True)
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True)
    full_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=128)
    language = models.CharField(
        max_length=10,
        choices=Language.choices,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username


class Region(models.Model):
    name_ru = models.CharField(max_length=100, unique=True)
    name_uz = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name_ru


class Organization(models.Model):
    name = models.CharField(max_length=255, unique=True)
    type = models.CharField(max_length=50, choices=OrganizationType.choices)
    region = models.ForeignKey(Region, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class User(models.Model):
    telegram_id = models.BigIntegerField(unique=True)
    phone = models.CharField(max_length=20, unique=True)
    user_type = models.CharField(
        max_length=20,
        choices=[(u.value, u.label("ru")) for u in UserType],  # default lang for display
    )
    full_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    language = models.CharField(
        max_length=10,
        choices=Language.choices,
        null=True,
        blank=True
    )
    organization = models.ForeignKey(Organization, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name


class Receipt(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    organization = models.ForeignKey(Organization, null=True, on_delete=models.SET_NULL)
    photo = models.CharField(max_length=255)
    ofd_url = models.CharField(max_length=255, null=True, blank=True)
    items = models.JSONField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=ReceiptStatus.choices,
        default=ReceiptStatus.PENDING
    )
    updated_by = models.ForeignKey(Admin, null=True, blank=True, on_delete=models.SET_NULL)
    comment = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class InviteLink(models.Model):
    token = models.UUIDField(unique=True)
    invited_by = models.ForeignKey(Admin, null=True, blank=True, on_delete=models.SET_NULL, related_name='invites_created')
    used = models.BooleanField(default=False)
    used_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    organization = models.ForeignKey(Organization, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Product(models.Model):
    name = models.CharField(max_length=255, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} – {self.price}"