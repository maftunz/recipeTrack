from django.contrib import admin
import django.contrib.auth.models as auth_models

admin.site.unregister(auth_models.Group)
admin.site.unregister(auth_models.User)

admin.site.site_header = "Shifokor Admin"
admin.site.site_title = "Shifokor Admin Portal"
admin.site.index_title = "Добро пожаловать в админ-панель"

from .region import *
from .organization import *
from .user import *
from .admin_user import *
from .receipt import *
from .product import *
from .invite_link import *
from .giveaway import *
from .statistics import *
from .statistics_proxy import *
