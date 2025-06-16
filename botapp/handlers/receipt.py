import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recipe_track.settings')
django.setup()

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from app.enums import UserType, ReceiptStatus

from ..keyboards import get_user_menu
from ..states import RecipeTrack
from ..services import (
    get_registered_user, save_receipt, save_photo_to_storage
)

receipt_router = Router()


@receipt_router.message(RecipeTrack.request_recipe)
async def recipe_requested(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data['lang']
    if lang == "ru":
        await message.answer(f"Пожалуйста отправьте фотографию рецепта", reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer(f"Iltimos retsept rasmini yuboring", reply_markup=ReplyKeyboardRemove())
    await state.set_state(RecipeTrack.sending_recipe)

@receipt_router.message(RecipeTrack.sending_recipe, F.photo)
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

@receipt_router.message(RecipeTrack.request_cheque)
async def cheque_requested(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data['lang']
    if lang == "ru":
        await message.answer(f"Пожалуйста отправьте фотографию чека", reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer(f"Iltimos chek rasmini yuboring", reply_markup=ReplyKeyboardRemove())
    await state.set_state(RecipeTrack.sending_cheque)

@receipt_router.message(RecipeTrack.sending_cheque, F.photo)
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
