from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from app.enums import UserType


def get_language_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Русский 🇷🇺"),
                KeyboardButton(text="O'zbek 🇺🇿")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard = True
    )
    return keyboard


def get_user_type_keyboard(lang: str) -> ReplyKeyboardMarkup:
    from app.enums import UserType
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=UserType.DOCTOR.label(lang)),
                KeyboardButton(text=UserType.PHARMACIST.label(lang))
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def get_regions_keyboard(regions) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[
            KeyboardButton(text=region.name_ru)] for region in regions
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def get_phone_request_keyboard(lang) -> ReplyKeyboardMarkup:
    text = "Отправить номер телефона"
    if lang == 'uz':
        text = "Telefon raqamini yuborish"

    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=text, request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_user_menu(user_type: str, lang: str = "ru") -> ReplyKeyboardMarkup:
    if user_type == UserType.DOCTOR.value:
        if lang == 'uz':
            label = "📄 Retseptni yuborish"
        else:
            label = "📄 Отправить рецепт"
    elif user_type == UserType.PHARMACIST.value:
        if lang == 'uz':
            label = "📄 Chekni yuborish"
        else:
            label = "🧾 Отправить чек"
    else:
        if lang == 'uz':
            label = "🔙 Orqaga"
        else:
            label = "🔙 Назад"

    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
            [KeyboardButton(text=label)]
        ])