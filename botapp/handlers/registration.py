import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recipe_track.settings')
django.setup()

from aiogram import Router, types, F
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from app.enums import UserType, ReceiptStatus

from ..keyboards import get_user_type_keyboard, get_regions_keyboard, get_phone_request_keyboard, get_language_keyboard, \
    get_user_menu
from ..states import Registration, RecipeTrack
from ..services import (
    get_all_regions, get_region_by_name, get_registered_user, get_active_invite_link, save_user,
    get_organization_by_name, save_receipt, parse_ofd_page, save_photo_to_storage
)
from tempfile import NamedTemporaryFile

registration_router = Router()


@registration_router.message(CommandStart(deep_link=True))
@registration_router.message(Command(commands=["start", "register"]))
async def start_registration(message: types.Message, command: CommandObject, state: FSMContext):
    ofd_url = "https://ofd.soliq.uz/check?t=VG343420028900&r=25708&c=20250514190427&s=312550081784"
    items = await parse_ofd_page(ofd_url)
    print(f"Товары: {items}")

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
    else:
        regions = await get_all_regions()
        await message.answer("Выберите ваш регион:", reply_markup=get_regions_keyboard(regions))
        await state.set_state(Registration.choosing_region)


@registration_router.message(Registration.choosing_region)
async def region_selected(message: types.Message, state: FSMContext):
    region = await get_region_by_name(message.text.strip())
    data = await state.get_data()
    lang = data['lang']
    if not region:
        if lang == "ru":
            await message.answer("Пожалуйста, выберите регион из предложенных кнопок.")
        else:
            await message.answer("Iltimos, taklif etilgan tugmalardan birini bosib, hududingizni tanlang.")
        return

    await state.update_data(region_id=region.id)
    if lang == "ru":
        await message.answer("Введите название вашей организации:")
    else:
        await message.answer("Tashkilotingiz nomini kiriting:")
    await state.set_state(Registration.choosing_organization)


@registration_router.message(Registration.choosing_organization)
async def organization_entered(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data['lang']
    await state.update_data(organization=message.text)
    organization = await get_organization_by_name(message.text.strip())
    if organization:
        await state.update_data(organization_id=organization.id)

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


@registration_router.message(RecipeTrack.request_recipe)
async def recipe_requested(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_type = data['user_type']
    lang = data['lang']
    if user_type == UserType.DOCTOR.value:
        if lang == "ru":
            await message.answer(f"Пожалуйста отправьте фотографию рецепта", reply_markup=ReplyKeyboardRemove())
        else:
            await message.answer(f"Iltimos retsept rasmini yuboring", reply_markup=ReplyKeyboardRemove())
        await state.set_state(RecipeTrack.sending_recipe)
    else:
        if lang == "ru":
            await message.answer(f"Пожалуйста отправьте фотографию чека", reply_markup=ReplyKeyboardRemove())
        else:
            await message.answer(f"Iltimos chek rasmini yuboring", reply_markup=ReplyKeyboardRemove())
        await state.set_state(RecipeTrack.sending_cheque)


@registration_router.message(RecipeTrack.sending_recipe, F.photo)
async def recipe_received(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'ru')

    if not message.photo:
        text = "Пожалуйста, отправьте фото." if lang == "ru" else "Iltimos, rasm yuboring."
        await message.answer(text)
        await state.set_state(RecipeTrack.sending_recipe)
        return

    photo = message.photo[-1]
    print(photo)

    try:
        user = await get_registered_user(message.from_user.id)
        if not user:
            text = "Пользователь не найден." if lang == "ru" else "Foydalanuvchi topilmadi."
            await message.answer(text)
            return

        photo_saved_path = await save_photo_to_storage(message.bot, photo, message.from_user.id)
        receipt = await save_receipt(photo_saved_path, None, user, ReceiptStatus.PENDING.value)

        role_menu = get_user_menu(user.user_type, user.language)
        text = (
            "Рецепт успешно получен и отправлен на модерацию."
            if lang == "ru"
            else "Retsept muvaffaqiyatli qabul qilindi va moderatsiya uchun yuborildi."
        )
        await message.answer(text, reply_markup=role_menu)

        await state.clear()
        await state.update_data(user_type=user.user_type, lang=user.language)
        await state.set_state(RecipeTrack.request_recipe)
    except Exception as e:
        await message.answer(
            "Ошибка при сохранении рецепта." if lang == "ru" else "Retseptni saqlashda xatolik yuz berdi.")
        print(f"❌ Ошибка: {e}")
        raise e


@registration_router.message(RecipeTrack.sending_cheque, F.photo)
async def cheque_received(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'ru')

    if not message.photo:
        text = "Пожалуйста, отправьте фото." if lang == "ru" else "Iltimos, rasm yuboring."
        await message.answer(text)
        await state.set_state(RecipeTrack.sending_cheque)
        return

    photo = message.photo[-1]

    try:
        user = await get_registered_user(message.from_user.id)
        if not user:
            text = "Пользователь не найден." if lang == "ru" else "Foydalanuvchi topilmadi."
            await message.answer(text)
            return

        role_menu = get_user_menu(user.user_type, user.language)

        saved_path = await save_photo_to_storage(message.bot, photo, user.id)
        # ofd_url = extract_qr_from_photo(saved_path)
        ofd_url = None

        if not ofd_url:
            cheque = await save_receipt(saved_path, None, user, ReceiptStatus.PENDING.value)
            text = (
                "QR-код не найден на фото. Чек отправлен на модерацию."
                if lang == "ru"
                else "QR-kod rasmda topilmadi. Chek moderatsiya uchun yuborildi."
            )
        else:
            cheque = await save_receipt(saved_path, ofd_url, user, ReceiptStatus.APPROVED.value)
            text = (
                "Чек успешно получен и QR-код распознан."
                if lang == "ru"
                else "Chek muvaffaqiyatli qabul qilindi va QR-kod tanildi."
            )

        await message.answer(text, reply_markup=role_menu)

        await state.clear()
        await state.update_data(user_type=user.user_type, lang=user.language)
        await state.set_state(RecipeTrack.request_cheque)

    except Exception as e:
        error_text = (
            "Ошибка при обработке чека." if lang == "ru" else "Chekni qayta ishlashda xatolik yuz berdi."
        )
        await message.answer(error_text)
        print(f"❌ Ошибка: {e}")
