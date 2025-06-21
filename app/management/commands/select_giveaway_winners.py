from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Sum

from app.models import Giveaway, Receipt, User
from app.enums import WinnerCriteria, GiveawayUserType

from app.usecases.notify_giveaway_participants import NotifyGiveawayParticipantsUseCase


class Command(BaseCommand):
    help = "Определяет победителей розыгрыша, срок действия которых завершён"

    def handle(self, *args, **options):
        now = timezone.now().date()

        giveaways = Giveaway.objects.filter(
            date_to__lt=now,
            winner_data__isnull=True
        )

        if not giveaways.exists():
            self.stdout.write(self.style.WARNING("Нет завершённых розыгрышей без победителей."))
            return

        for giveaway in giveaways:
            self.stdout.write(f"Обработка розыгрыша: {giveaway.title}")

            users_qs = User.objects.all()

            if giveaway.user_type == GiveawayUserType.DOCTOR:
                users_qs = users_qs.filter(user_type='doctor')
            elif giveaway.user_type == GiveawayUserType.PHARMACIST:
                users_qs = users_qs.filter(user_type='pharmacist')
            else:
                users_qs = users_qs

            winner_count = giveaway.winner_count

            receipts = Receipt.objects.filter(
                user__in=users_qs,
                created_at__date__range=(giveaway.date_from, giveaway.date_to)
            )

            # Определение победителей по критерию

            if giveaway.winner_criteria == WinnerCriteria.BY_COUNT:
                top_users = receipts.filter(quantity__isnull=False).values('user_id', 'user__full_name').annotate(
                    total=Sum('quantity')
                ).order_by('-total')[:winner_count]

            elif giveaway.winner_criteria == WinnerCriteria.BY_TOTAL_AMOUNT:
                top_users = receipts.filter(amount__isnull=False).values('user_id', 'user__full_name').annotate(
                    total=Sum('amount')
                ).order_by('-total')[:winner_count]

            else:
                self.stdout.write(self.style.WARNING(f"Неизвестный критерий для {giveaway.title}, пропущено."))
                continue

            winners = list(top_users)

            giveaway.winner_data = winners
            giveaway.save(update_fields=['winner_data'])

            NotifyGiveawayParticipantsUseCase(giveaway).run()

            self.stdout.write(self.style.SUCCESS(f"Победители выбраны: {winners}"))