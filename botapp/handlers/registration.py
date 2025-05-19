import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recipe_track.settings')
django.setup()

from aiogram import Router, types, F
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from app.enums import UserType

from ..keyboards import get_user_type_keyboard, get_regions_keyboard, get_phone_request_keyboard
from ..states import Registration
from ..services import (
    get_all_regions, get_region_by_name, get_registered_user, get_active_invite_link, save_user
)

# ========== ROUTER ==========
registration_router = Router()

# ========== HANDLERS ==========
@registration_router.message(CommandStart(deep_link=True))
@registration_router.message(Command(commands=["start", "register"]))
async def start_registration(message: types.Message, command: CommandObject, state: FSMContext):
    token = command.args
    telegram_id = message.from_user.id
    lang = "ru"
    await state.update_data(lang=lang)

    existing_user = await get_registered_user(telegram_id)
    if existing_user:
        await message.answer(f"Добро пожаловать, {existing_user.full_name}!")
        await state.clear()
        return

    invite = await get_active_invite_link(token)
    if invite:
        await state.update_data(invite_token=token, organization_id=invite.organization_id)

    await message.answer("Добро пожаловать! Пожалуйста, выберите, кто вы? Врач или фармацевт?",
                         reply_markup=get_user_type_keyboard(lang))
    await state.set_state(Registration.choosing_user_type)


@registration_router.message(Registration.choosing_user_type)
async def user_type_selected(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data['lang']
    user_type = UserType.key_by_label(message.text, lang)
    if not user_type:
        await message.answer("Пожалуйста, выберите: Врач или Фармацевт.")
        return

    await state.update_data(user_type=user_type)
    await message.answer("Введите ваше ФИО:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Registration.entering_full_name)


@registration_router.message(Registration.entering_full_name)
async def full_name_entered(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    data = await state.get_data()

    if data.get("organization_id"):
        await message.answer("Пожалуйста, отправьте ваш номер телефона, используя кнопку ниже:",
                             reply_markup=get_phone_request_keyboard())
        await state.set_state(Registration.entering_phone)
    else:
        regions = await get_all_regions()
        await message.answer("Выберите ваш регион:", reply_markup=get_regions_keyboard(regions))
        await state.set_state(Registration.choosing_region)


@registration_router.message(Registration.choosing_region)
async def region_selected(message: types.Message, state: FSMContext):
    # Здесь можно проверить регион на валидность
    region = await get_region_by_name(message.text.strip())
    if not region:
        await message.answer("Пожалуйста, выберите регион из предложенных кнопок.")
        return

    await state.update_data(region_id=region.id)
    await message.answer("Введите название вашей организации:")
    await state.set_state(Registration.choosing_organization)


@registration_router.message(Registration.choosing_organization)
async def organization_entered(message: types.Message, state: FSMContext):
    await state.update_data(organization=message.text)
    await message.answer("Пожалуйста, отправьте ваш номер телефона, используя кнопку ниже:",
                         reply_markup=get_phone_request_keyboard())
    await state.set_state(Registration.entering_phone)


@registration_router.message(F.content_type == types.ContentType.CONTACT, Registration.entering_phone)
async def phone_received(message: types.Message, state: FSMContext):
    contact = message.contact
    if not contact or not contact.phone_number:
        await message.answer("Не удалось получить номер телефона. Пожалуйста, попробуйте снова.")
        return

    await state.update_data(
        phone=contact.phone_number,
        telegram_id = message.from_user.id
    )

    user_data = await state.get_data()
    await save_user(user_data)

    await message.answer(f"Спасибо за регистрацию! Вы успешно зарегистрированы.", reply_markup=ReplyKeyboardRemove())
    await state.clear()