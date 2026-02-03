'''
    Module with callbacks
'''
import os
from aiogram.types import LabeledPrice, PreCheckoutQuery
from aiogram import Router, F, types
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from loguru import logger

from Bot_API.keyboards.active_keyboards import get_vacancy_keyboard
from DB.requests.requests import update_prof, delete_profile, get_profile_id_by_tg, get_profile, \
    check_user_subscription, activate_subscription
from DB.requests.requests_vacancies import del_from_favorite, add_to_favorites, check_if_favorite_exists, \
    get_vacancy
from Bot_API.utils import create_vacancy_text


router_callback = Router()



#####################################################
# Callbacks Profiles
#####################################################

class ProfileForm(StatesGroup):
    waiting_for_role = State()
    waiting_for_level = State()
    waiting_for_format = State()
    waiting_for_salary = State()


# 1. Start of survey (triggered by the 'update' button)
@router_callback.callback_query(F.data == 'update')
async def start_update(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Ответьте на вопросы:\n\na) What role are you looking for?')
    await state.set_state(ProfileForm.waiting_for_role)
    await callback.answer()


# 2. We are expecting a role and asking about the level.
@router_callback.message(ProfileForm.waiting_for_role)
async def process_role(message: Message, state: FSMContext):
    await state.update_data(role=message.text)
    await message.answer('b) What level (Junior, Middle, Senior)?')
    await state.set_state(ProfileForm.waiting_for_level)


# 3. We are expecting a level and asking about the format.
@router_callback.message(ProfileForm.waiting_for_level)
async def process_level(message: Message, state: FSMContext):
    await state.update_data(level=message.text)
    await message.answer('c) What format (Remote, Office, Hybrid)?')
    await state.set_state(ProfileForm.waiting_for_format)

# 4. We are expecting a format and asking about the salary.
@router_callback.message(ProfileForm.waiting_for_format)
async def process_format(message: Message, state: FSMContext):
    await state.update_data(format=message.text)
    await message.answer('c) What salary?')
    await state.set_state(ProfileForm.waiting_for_salary)

# 5. Last answer, save to DB and final.
@router_callback.message(ProfileForm.waiting_for_salary)
async def process_salary(message: Message, state: FSMContext):
    # We save the last response in the data state
    await state.update_data(salary=message.text)
    # We receive all collected data from the FSM memory
    user_data = await state.get_data()
    p_id = await get_profile_id_by_tg(tg_id=message.from_user.id)

    await update_prof(
        p_id,
        role=user_data['role'],
        level=user_data['level'],
        format=user_data['format'],
        salary=user_data['salary']
    )

    await message.answer('Данные обновлены ✅')
    logger.success('data Profile updated')
    await state.clear()  # Clearing the state


# callback delete profile from DB
@router_callback.callback_query(F.data == 'delete')
async def del_profile(callback: CallbackQuery):
    user_id = callback.from_user.id
    await delete_profile(user_tg_id=user_id)
    logger.info(f'Profile {user_id} deleted')
    await callback.message.answer('Профиль удален')


##############################################################
# Payment subscription
##############################################################

# callback to pay for a subscription
@router_callback.callback_query(F.data == "subscription")
async def send_invoice(callback: types.CallbackQuery):
    price_amount = 500  # 500 RUB

    await callback.message.answer_invoice(
        title="Premium Подписка",
        description="Доступ к контактам всех вакансий на 30 дней",
        payload="month_subscription",
        provider_token=os.getenv('PAYMENT_PROVIDER_TOKEN'),
        currency="RUB",
        prices=[LabeledPrice(label="Premium на 30 дней", amount=price_amount * 100)],  # Сумма в копейках
        start_parameter="sub-upgrade"
    )


# 2. Confirmation (mandatory step!)
@router_callback.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)

# 3. Final: activation in the database after successful payment
@router_callback.message(F.successful_payment)
async def success_payment_handler(message: Message):
    await activate_subscription(message.from_user.id)
    logger.success(f'Payment completed')
    await message.answer("✅ Оплата прошла! Контакты теперь открыты.")



#####################################################
# Callbacks Vacancies
#####################################################

# callback favorite or hide
@router_callback.callback_query(F.data.startswith('fav_') | F.data.startswith('hide_'))
async def next_vacancy_callback(callback: CallbackQuery, state: FSMContext):
    vacancy_id = int(callback.data.split('_')[1])
    user_id = callback.from_user.id
    is_premium = await check_user_subscription(user_id)
    already_exists = await check_if_favorite_exists(user_id, vacancy_id)
    if callback.data.startswith('fav_'):
        if already_exists:
            await callback.answer('Уже добавлена')
        else:
            await add_to_favorites(user_id, vacancy_id)
            await callback.answer("Добавлено в избранное ❤️")
    else:
        await callback.answer("Пропущено 👎")

    data = await state.get_data()
    current_offset = data.get("offset", 0)

    profile = await get_profile(callback.from_user.id)
    vacancy_obj = await get_vacancy(profile, limit=1, offset=current_offset)

    if not vacancy_obj:
        await callback.message.edit_text("✅ <b>На этом всё! Все вакансии просмотрены.</b>", parse_mode="HTML")
        return

    vacancy = vacancy_obj[0]

    await callback.message.edit_text(
        text=create_vacancy_text(vacancy, is_premium),
        reply_markup=get_vacancy_keyboard(vacancy.id),
        parse_mode="HTML"
    )

    # Увеличиваем offset
    await state.update_data(offset=current_offset + 1)


#####################################################
# Callback Favorites
#####################################################

# delete vacancy from favorite
@router_callback.callback_query(F.data.startswith('delete_'))
async def apply_vacancy(callback: CallbackQuery):
    user_id = callback.from_user.id
    vacancy_id = int(callback.data.split('_')[1])
    await del_from_favorite(user_id, vacancy_id)
    await callback.answer('Вакансия удалена из избранного ❌')
    await callback.message.delete()

#####################################################
