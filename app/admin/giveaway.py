from django.contrib import admin
from django.utils.html import format_html_join
from ..models import Giveaway

@admin.register(Giveaway)
class GiveawayAdmin(admin.ModelAdmin):
    list_display = ("title", "prize_amount", "winner_criteria", "user_type", "winner_count",
                    "date_from", "date_to", "display_winners", "created_at", "updated_at")
    list_filter = ("winner_criteria", "user_type", "date_from", "date_to")
    search_fields = ("title",)
    readonly_fields = ('display_winners',)
    ordering = ("-created_at",)
    actions = None

    def display_winners(self, obj):
        if not obj.winner_data:
            return "-"
        return format_html_join(
            '<br>',
            '{} ({} шт, {} сум)',
            ((winner['full_name'], winner['total_receipts'], winner['total_amount']) for winner in obj.winner_data)
        )

    display_winners.short_description = "Победители"
