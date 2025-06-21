from django.db.models import Sum
from app.enums import WinnerCriteria, GiveawayUserType
from app.models import Receipt
from app.services import send_message_to_user
import asyncio


class NotifyGiveawayParticipantsUseCase:
    def __init__(self, giveaway):
        self.giveaway = giveaway

    def run(self):
        # Все участники, которые отправляли чеки/рецепты
        all_receipts = Receipt.objects.filter(
            user__user_type=self.giveaway.user_type,
            created_at__date__range=(self.giveaway.date_from, self.giveaway.date_to)
        )

        if self.giveaway.winner_criteria == WinnerCriteria.BY_COUNT:
            stats = all_receipts.filter(quantity__isnull=False).values('user_id', 'user__full_name').annotate(
                total=Sum('quantity')
            )
            sum_text = 'нужное количество'
            winner_text = 'количество'
        elif self.giveaway.winner_criteria == WinnerCriteria.BY_TOTAL_AMOUNT:
            stats = all_receipts.filter(amount__isnull=False).values('user_id', 'user__full_name').annotate(
                total=Sum('amount')
            )
            sum_text = 'нужную сумму'
            winner_text = 'сумму'
        else:
            return

        if self.giveaway.user_type == GiveawayUserType.DOCTOR:
            if self.giveaway.winner_criteria == WinnerCriteria.BY_COUNT:
                sum_text = 'нужное количество рецептов'
                winner_text = 'количество рецептов'
            elif self.giveaway.winner_criteria == WinnerCriteria.BY_TOTAL_AMOUNT:
                sum_text = 'нужную сумму рецептов'
                winner_text = 'сумму рецептов'
        elif self.giveaway.user_type == GiveawayUserType.PHARMACIST:
            if self.giveaway.winner_criteria == WinnerCriteria.BY_COUNT:
                sum_text = 'нужное количество чеков'
                winner_text = 'количество чеков'
            elif self.giveaway.winner_criteria == WinnerCriteria.BY_TOTAL_AMOUNT:
                sum_text = 'нужную сумму чеков'
                winner_text = 'сумму чеков'
        else:
            if self.giveaway.winner_criteria == WinnerCriteria.BY_COUNT:
                sum_text = 'нужное количество'
                winner_text = 'количество'
            elif self.giveaway.winner_criteria == WinnerCriteria.BY_TOTAL_AMOUNT:
                sum_text = 'нужную сумму'
                winner_text = 'сумму'

        # Формируем словарь user_id -> total
        user_totals = {s['user_id']: s['total'] for s in stats}
        top_total = max(user_totals.values(), default=0)

        winners_ids = {w['user_id'] for w in self.giveaway.winner_data}

        for stat in stats:
            user_id = stat['user_id']
            full_name = stat['user__full_name']
            total = stat['total']
            message = ""

            if user_id in winners_ids:

                message = (
                    f"🎉 Поздравляем, {full_name}!\n"
                    f"Вы стали победителем розыгрыша «{self.giveaway.title}»!\n"
                    f"Ваш результат: {total}\n"
                    f"В качестве приза вы получаете: {self.giveaway.prize_amount} сум\n"
                    f"В ближайшее время ваш агент свяжется с вами для передачи приза 🎁"
                )
            else:
                message = (
                    f"Спасибо за участие, {full_name}!\n\n"
                    f"К сожалению, в этом месяце вы не набрали {sum_text}.\n"
                    f"Не отчаивайтесь, у вас есть все шансы на следующий месяц!\n\n"
                    f"В этом месяце победитель набрал {top_total} {winner_text}."
                )

            asyncio.run(send_message_to_user(user_id, message))