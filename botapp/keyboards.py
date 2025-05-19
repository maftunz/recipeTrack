from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

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


def get_phone_request_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Отправить номер телефона", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
