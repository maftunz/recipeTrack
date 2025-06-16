import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recipe_track.settings')
django.setup()

from aiogram import Router, types, F
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from app.enums import UserType

from ..keyboards import get_user_type_keyboard, get_phone_request_keyboard, get_language_keyboard, \
    get_user_menu
from ..states import Registration, RecipeTrack
from ..services import get_registered_user, get_active_invite_link, save_user

registration_router = Router()


@registration_router.message(CommandStart(deep_link=True))
@registration_router.message(Command(commands=["start", "register"]))
async def start_registration(message: types.Message, command: CommandObject, state: FSMContext):
    token = command.args
    telegram_id = message.from_user.id

    existing_user = await get_registered_user(telegram_id)
    if existing_user:
        role_menu = get_user_menu(existing_user.user_type, existing_user.language)

        if existing_user.language == "ru":
            await message.answer(f"Добро пожаловать, {existing_user.full_name}!", reply_markup=role_menu)
        else:
            await message.answer(f"Xush kelibsiz, {existing_user.full_name}!", reply_markup=role_menu)

        await state.clear()
        await state.update_data(user_type=existing_user.user_type, lang=existing_user.language)
        if existing_user.user_type == UserType.PHARMACIST:
            await state.set_state(RecipeTrack.request_cheque)
        else:
            await state.set_state(RecipeTrack.request_recipe)
        return

    if token:
        invite = await get_active_invite_link(token)
        if invite:
            await state.update_data(invite_token=token, organization_id=invite.organization_id)

        await message.answer("Пожалуйста, выберите язык:\nIltimos, tilni tanlang:", reply_markup=get_language_keyboard())
        await state.set_state(Registration.choosing_language)


@registration_router.message(Registration.choosing_language)
async def language_selected(message: types.Message, state: FSMContext):
    lang_map = {
        "Русский 🇷🇺": "ru",
        "O'zbek 🇺🇿": "uz"
    }

    lang = lang_map.get(message.text)
    if not lang:
        await message.answer("Пожалуйста, выберите язык с помощью кнопок.\nIltimos, tugmalar yordamida tilni tanlang.")
        return

    await state.update_data(lang=lang)

    if lang == "ru":
        await message.answer("Добро пожаловать! Пожалуйста, выберите, кто вы? Врач или фармацевт?",
                             reply_markup=get_user_type_keyboard(lang))
    else:
        await message.answer("Xush kelibsiz! Iltimos, tanlang siz kimsiz? Shifokor yoki farmatsevt?",
                             reply_markup=get_user_type_keyboard(lang))

    await state.set_state(Registration.choosing_user_type)


@registration_router.message(Registration.choosing_user_type)
async def user_type_selected(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data['lang']
    user_type = UserType.key_by_label(message.text, lang)
    if not user_type:
        if lang == "ru":
            await message.answer("Пожалуйста, выберите: Врач или Фармацевт.")
        else:
            await message.answer("Iltimos, tanlang: Shifokor yoki farmatsevt.")
        return

    await state.update_data(user_type=user_type)
    if lang == "ru":
        await message.answer("Введите ваше ФИО:", reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer("Toʻliq ism familiyangizni kiriting:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Registration.entering_full_name)


@registration_router.message(Registration.entering_full_name)
async def full_name_entered(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    data = await state.get_data()
    lang = data['lang']

    if data.get("organization_id"):
        if lang == "ru":
            await message.answer("Пожалуйста, отправьте ваш номер телефона, используя кнопку ниже:",
                             reply_markup=get_phone_request_keyboard(lang))
        else:
            await message.answer("Iltimos, quyidagi tugma orqali telefon raqamingizni yuboring:",
                                 reply_markup=get_phone_request_keyboard(lang))
        await state.set_state(Registration.entering_phone)


@registration_router.message(F.content_type == types.ContentType.CONTACT, Registration.entering_phone)
async def phone_received(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data['lang']
    contact = message.contact
    if not contact or not contact.phone_number:
        if lang == "ru":
            await message.answer("Не удалось получить номер телефона. Пожалуйста, попробуйте снова.")
        else:
            await message.answer("Telefon raqamingizni olishning imkoni bo‘lmadi. Iltimos, qayta urinib ko‘ring.")
        return

    await state.update_data(
        phone=contact.phone_number,
        telegram_id = message.from_user.id
    )

    user_data = await state.get_data()
    user = await save_user(user_data)

    role_menu = get_user_menu(user.user_type, user.language)

    if lang == "ru":
        await message.answer(f"Спасибо! Вы успешно зарегистрированы.", reply_markup=role_menu)
    else:
        await message.answer(f"Rahmat! Siz muvaffaqiyatli ro‘yxatdan o‘tdingiz.",
                             reply_markup=role_menu)
    await state.clear()
    await state.update_data(user_type=user.user_type, lang=user.language)
    await state.set_state(RecipeTrack.request_recipe)
