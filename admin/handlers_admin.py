import os

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from loguru import logger

from admin.markup_admin import admin_markup
from admin.requests_admin import count_users_is_sub, get_all_users_ids

admin_router = Router()

ADMIN_IDS = int(os.getenv('ADMIN_IDS'))



#####################################################

@admin_router.message(Command('admin'), F.from_user.id == ADMIN_IDS)
async def admin_start_command(message: Message):
    text = 'Welcome to Admin Panel. Choose an action:'
    await message.answer(text, reply_markup=admin_markup())

#####################################################

@admin_router.callback_query(F.data == 'admin_subs')
async def get_list_users_sub(callback: CallbackQuery):
    count = await count_users_is_sub()
    # count = 42  # Пример
    logger.info(f"Admin requested subs count: {count}")
    await callback.message.answer(f"Всего активных подписок: {count}")


#####################################################


class BroadcastStates(StatesGroup):
    wait_message = State()  # Состояние ожидания текста анонса


# 1. Админ нажал кнопку "Рассылка"
@admin_router.callback_query(F.data == 'admin_broadcast')
async def start_broadcast(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("⌨️ Введите текст объявления для всех пользователей:")
    await state.set_state(BroadcastStates.wait_message)


# 2. Бот поймал текст и начал рассылку
@admin_router.message(BroadcastStates.wait_message)
async def process_broadcast(message: Message, state: FSMContext):
    await state.clear()  # Сбрасываем состояние сразу

    # Получаем список всех пользователей из БД (только ID)
    users = await get_all_users_ids()

    count = 0
    await message.answer(f"🚀 Start sending to {len(users)} users...")

    for user_id in users:
        try:
            # Копируем сообщение админа (можно отправить текст, фото или видео)
            await message.send_copy(chat_id=user_id)
            count += 1
        except Exception as e:
            logger.error(f"Failed to send message to {user_id}: {e}")

    await message.answer(f"✅ Success! Received by {count} users.")
    logger.success(f"Admin {message.from_user.id} finished broadcast: {count} delivered.")


