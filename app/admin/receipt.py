from django.conf import settings
from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.db.models import Sum, Count
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html, format_html_join
from django_json_widget.widgets import JSONEditorWidget
from django import forms

from rangefilter.filters import DateRangeFilter

from .filters import UserTypeFilter
from ..models import Receipt, Admin


class ReceiptChangeList(ChangeList):
    def get_results(self, *args, **kwargs):
        super().get_results(*args, **kwargs)

        # Агрегируем только отфильтрованные queryset'ы
        qs = self.result_list
        totals = qs.aggregate(
            total_amount=Sum("amount"),
            total_quantity=Sum("quantity")
        )

        self.total_amount = totals["total_amount"] or 0
        self.total_quantity = totals["total_quantity"] or 0

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
    list_display = ('id', 'user_link', 'organization', 'display_items', 'type', 'status', 'quantity', 'amount', 'ofd_url',
                    'updated_by_link', 'comment', 'created_at', 'updated_at')
    list_filter = (
        'status',
        'type',
        UserTypeFilter,
        ('created_at', DateRangeFilter),
    )
    search_fields = ('user__full_name',)
    readonly_fields = ('display_items', 'photo_preview', 'updated_by','created_at', 'updated_at')
    actions = None
    ordering = ("-created_at",)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('aggregated/', self.admin_site.admin_view(self.aggregated_view), name='receipts_aggregated'),
        ]
        return custom_urls + urls

    def save_model(self, request, obj, form, change):
        if change:
            admin_user = Admin.objects.filter(user_id=request.user.id).first()

            if admin_user:
                obj.updated_by = admin_user
            obj.updated_at = timezone.now()
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

    def updated_by_link(self, obj):
        if obj.updated_by:
            admin_obj = obj.updated_by
            url = reverse("admin:app_admin_change", args=[admin_obj.id])
            return format_html('<a href="{}">{}</a>', url, admin_obj.full_name)
        return "-"

    updated_by_link.short_description = "Обновил"
    updated_by_link.admin_order_field = 'updated_by'

    def user_link(self, obj):
        if obj.user:
            url = reverse("admin:app_user_change", args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.full_name)

        return "-"

    user_link.short_description = "Пользователь"
    user_link.admin_order_field = 'user'

    def get_changelist(self, request, **kwargs):
        return ReceiptChangeList

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        cl = self.get_changelist_instance(request)
        extra_context['total_amount'] = cl.total_amount
        extra_context['total_quantity'] = cl.total_quantity

        if request.GET.get('aggregate') == '1':
            return self.aggregated_view(request)

        aggregate_url = f"{request.path}?aggregate=1"
        extra_context['additional_button'] = format_html(
            '<a class="button" href="{}">Показать сгруппированные по врачам</a>', aggregate_url
        )
        return super().changelist_view(request, extra_context=extra_context)

    def aggregated_view(self, request):
        qs = Receipt.objects.select_related('user').values(
            'user__id',
            'user__full_name'
        ).annotate(
            total_receipts=Count('id'),
            total_amount=Sum('amount')
        ).order_by('-total_receipts')

        context = dict(
            self.admin_site.each_context(request),
            title='Сгруппированная статистика по врачам',
            user_stats=qs,
            opts=self.model._meta,
            back_url=reverse(f'admin:{self.model._meta.app_label}_{self.model._meta.model_name}_changelist')
        )
        return TemplateResponse(request, "admin/statistics/receipts_aggregated.html", context)
