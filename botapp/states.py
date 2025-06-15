import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recipe_track.settings')
django.setup()

from aiogram.fsm.state import State, StatesGroup

class Registration(StatesGroup):
    choosing_language = State()
    choosing_user_type = State()
    entering_full_name = State()
    choosing_region = State()
    choosing_organization = State()
    entering_phone = State()

class RecipeTrack(StatesGroup):
    request_recipe = State()
    sending_recipe = State()
    request_cheque = State()
    sending_cheque = State()