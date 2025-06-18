from django.contrib.admin.views.decorators import staff_member_required
from django.template.response import TemplateResponse
from django.db.models import Count
from datetime import datetime

from app.models import Receipt

@staff_member_required
def statistics_view(request):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    receipts = Receipt.objects.select_related("user").all()

    if start_date_str:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        receipts = receipts.filter(created_at__date__gte=start_date)

    if end_date_str:
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        receipts = receipts.filter(created_at__date__lte=end_date)

    user_stats = receipts.values('user__id', 'user__full_name').annotate(
        total_receipts=Count('id')
    ).order_by('-total_receipts')

    context = {
        "user_stats": user_stats,
        "start_date": start_date_str or '',
        "end_date": end_date_str or '',
        "title": "Статистика по врачам"
    }
    return TemplateResponse(request, "admin/statistics/custom_statistics.html", context)