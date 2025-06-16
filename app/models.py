from django.db import models
from django.contrib.auth.models import User as AuthUser
from .enums import ReceiptStatus, ReceiptType, WinnerCriteria, GiveawayUserType
from .enums import UserType
from .enums import OrganizationType
from .enums import Language


class Admin(models.Model):
    user = models.OneToOneField(AuthUser, on_delete=models.CASCADE, null=True, blank=True)
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True, verbose_name="Telegram ID")
    full_name = models.CharField(max_length=255, verbose_name="ФИО")
    username = models.CharField(max_length=255, verbose_name="Юзернейм")
    password = models.CharField(max_length=128, verbose_name="Пароль")
    language = models.CharField(
        max_length=10,
        choices=Language.choices,
        null=True,
        blank=True,
        verbose_name = "Язык"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Админ"
        verbose_name_plural = "Админы"


class Region(models.Model):
    name_ru = models.CharField(max_length=100, unique=True, verbose_name="Название Ру")
    name_uz = models.CharField(max_length=100, unique=True, verbose_name="Название Уз")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return self.name_ru

    class Meta:
        verbose_name = "Регион"
        verbose_name_plural = "Регионы"


class Organization(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Дата создания")
    type = models.CharField(max_length=50, choices=OrganizationType.choices, verbose_name="Тип организации")
    region = models.ForeignKey(Region, null=True, on_delete=models.SET_NULL, verbose_name="Регион")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Организация"
        verbose_name_plural = "Ораганизации"


class User(models.Model):
    telegram_id = models.BigIntegerField(unique=True, verbose_name="Telegram ID")
    phone = models.CharField(max_length=20, unique=True, verbose_name="Номер телефона")
    user_type = models.CharField(
        max_length=20,
        choices=[(u.value, u.label("ru")) for u in UserType],
        verbose_name="Тип пользователя"
    )
    full_name = models.CharField(max_length=255, verbose_name="ФИО")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    language = models.CharField(
        max_length=10,
        choices=Language.choices,
        null=True,
        blank=True,
        verbose_name="Язык"
    )
    organization = models.ForeignKey(Organization, null=True, on_delete=models.SET_NULL, verbose_name="Организация")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Receipt(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, verbose_name="Пользователь")
    organization = models.ForeignKey(Organization, null=True, on_delete=models.SET_NULL, verbose_name="Организация")
    photo = models.CharField(max_length=255, verbose_name="Фото")
    ofd_url = models.CharField(max_length=255, null=True, blank=True, verbose_name="Ссылка Soliq")
    items = models.JSONField(null=True, blank=True, verbose_name="Продукты")
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Сумма")
    quantity = models.PositiveIntegerField(null=True, blank=True, verbose_name="Количество")
    type = models.CharField(
        max_length=20,
        choices=ReceiptType.choices,
        null=True,
        blank=True,
        verbose_name="Тип"
    )
    status = models.CharField(
        max_length=20,
        choices=ReceiptStatus.choices,
        default=ReceiptStatus.PENDING,
        verbose_name="Статус"
    )
    updated_by = models.ForeignKey(Admin, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Кем обновлено")
    comment = models.CharField(max_length=255, null=True, blank=True, verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Рецепт/Чек"
        verbose_name_plural = "Рецепты/Чеки"


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


class Product(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Название продукта")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return f"{self.name} – {self.price}"

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"


class Giveaway(models.Model):
    title = models.CharField(max_length=255,
                             null=True,
                             blank=True,
                             verbose_name="Название розыгрыша")
    prize_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма приза")
    date_from = models.DateField(verbose_name="Начало периода")
    date_to = models.DateField(verbose_name="Конец периода")

    winner_criteria = models.CharField(
        max_length=20,
        choices=WinnerCriteria.choices,
        null=True,
        blank=True,
        verbose_name="Критерий выбора"
    )

    user_type = models.CharField(
        max_length=20,
        choices=GiveawayUserType.choices,
        default=GiveawayUserType.ALL,
        verbose_name="Участники"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Розыгрыш"
        verbose_name_plural = "Розыгрыши"