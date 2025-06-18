from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext_lazy as _

from app.enums import UserType


class UserTypeFilter(SimpleListFilter):
    title = _('Тип пользователя')
    parameter_name = 'user__user_type'

    def lookups(self, request, model_admin):
        return [(u.value, u.label("ru")) for u in UserType]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(user__user_type=self.value())
        return queryset