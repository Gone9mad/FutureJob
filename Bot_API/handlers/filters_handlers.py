'''
    Modul with handlers filters
'''

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from loguru import logger

from Bot_API.keyboards.active_keyboards import get_vacancy_keyboard, favorites_keyboard, inline_markup_profile
from DB.requests.requests import get_profile, check_user_subscription, get_subscription_for_user
from DB.requests.requests_vacancies import get_vacancy, get_from_favorite
from Bot_API.utils import create_vacancy_text

router_filters = Router()

#####################################################
# Handler filter Home
@router_filters.message(F.text == "Главная")
async def command_home_handler(message: Message) -> None:
    caption = (
        f"<b>💼 FutureJob — Твой интеллектуальный HR-проводник</b>\n\n"
        f"Я не просто база вакансий, а умный алгоритм, который сокращает путь "
        f"от резюме до оффера в 10 раз.\n\n"
        f"<blockquote><b>Что я умею:</b>\n"
        f"• <b>Мгновенный анализ CV:</b> Просто пришли файл, и я сам заполню твой профиль.\n"
        f"• <b>Smart-подбор:</b> Показываю только те вакансии, которые подходят под твои навыки.\n"
        f"• <b>Уведомления 24/7:</b> Узнавай о новых вакансиях первым.</blockquote>\n\n"
        f"<b>Почему выбирают нас?</b>\n"
        f"✅ <b>Точность:</b> Никакого спама.\n"
        f"✅ <b>Скорость:</b> Отклик в один клик.\n"
        f"✅ <b>Конфиденциальность:</b> Твои данные в безопасности.\n\n"
        f"<i>Настрой свой профиль в меню ниже и начни получать лучшие офферы уже сегодня! 🚀</i>"
    )

    await message.answer(caption, parse_mode="HTML")


#####################################################
# Handler filter Profile
@router_filters.message(F.text == "Профиль")
async def command_profile_handler(message: Message) -> None:
    user_id = message.from_user.id
    profile = await get_profile(user_id)
    is_active = await check_user_subscription(user_id)
    if not profile:
        await message.answer('😔 У вас нет профиля, загрузите CSV')
    else:
        text = (
            f"<b>👤 Твой цифровой профиль</b>\n\n"
            f"<blockquote>"
            f"🎭 <b>Специализация:</b> <code>{profile.role}</code>\n"
            f"📈 <b>Уровень:</b> <code>{profile.level}</code>\n"
            f"💰 <b>Ожидания по ЗП:</b> <code>{profile.salary}</code>\n"
            f"📍 <b>Формат работы:</b> <code>{profile.format}</code>"
            f"</blockquote>\n\n"
            f"<i>Данные извлечены из твоего CV.\nТы можешь обновить их в любое время через меню настроек. ⚙️</i>"
        )

        await message.answer(text=text, reply_markup=inline_markup_profile(is_active), parse_mode='HTML')

#####################################################
# Handler filter Feed
@router_filters.message(F.text == "Лента")
async def command_ribbon_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(offset=0)
    user_id = message.from_user.id
    is_premium = await check_user_subscription(user_id)
    profile = await get_profile(user_id)
    vacancy_obj = await get_vacancy(profile, limit=1, offset=0)

    if not vacancy_obj:
        await message.answer('Для вас пока нет вакансий')
        return

    vacancy = vacancy_obj[0]
    await message.answer(
        text=create_vacancy_text(vacancy, is_premium),
        reply_markup=get_vacancy_keyboard(vacancy.id),
        parse_mode="HTML"
    )
    await state.update_data(offset=1)


#####################################################
# Handler filter Subscription
@router_filters.message(F.text == "Подписки")
async def command_subscription_handler(message: Message) -> None:
    user_id = message.from_user.id
    subscriptions = await get_subscription_for_user(user_id)

    if not subscriptions:
        logger.info(f"User {user_id} checked sub: No active subscriptions")
        await message.answer("😔 У вас нет ни одной активной подписки.")
        return

    # Если подписка есть (берем первую или проходим циклом)
    # Предположим, у подписки есть поля 'plan_name' и 'end_date'
    sub = subscriptions[0]

    text = (
        "💎 **Ваша подписка:**\n\n"
        f"Тип: Подписка на контакты\n"  # Твой Junior/Middle/Senior
        f"Статус: Активна ✅\n"
        f"Оформлена: {sub.created_at.strftime('%d.%m.%Y')}\n"
        f"Истекает: {sub.expires_at.strftime('%d.%m.%Y') if sub.expires_at else 'Бессрочно'}"
    )

    logger.info(f"User {user_id} checked sub: Found {len(subscriptions)} items")
    await message.answer(text, parse_mode="Markdown")


#####################################################
# Handler filter Saved
@router_filters.message(F.text == "Избранное")
async def command_save_handler(message: Message) -> None:
    user_id = message.from_user.id
    is_premium = await check_user_subscription(user_id)
    vacancies = await get_from_favorite(user_id)
    if not vacancies:
        await message.answer("😔У вас нет сохраненных вакансий.")
        return
    for vac in vacancies:
        await message.answer(
                text=create_vacancy_text(vac, is_premium),
                reply_markup=favorites_keyboard(vac.id),
                parse_mode="HTML"
            )

#####################################################
# Handler filter Tools
@router_filters.message(F.text == "Доп.сервис")
async def command_tools_handler(message: Message) -> None:
    text = (
        f"<blockquote>"
        f"• <b>AI resume creation and analysis - 5$</b>\n\n"
        f"• <b>енерация сопроводительного письма под вакансию - 5$</b>\n\n"
        f"• <b>Подготовка к интервью (вопросы + симуляция) - 20$</b>\n\n"
        f"• <b>Консультация HR (как отдельный оффер) - 50$</b>\n"
        f"</blockquote>")

    await message.answer(text, parse_mode='HTML')

#####################################################
# Handler commands help
@router_filters.message(F.text == "help")
async def command_help_handler(message: Message) -> None:
    text = (
         f"<blockquote><b>FAQ:</b>\n"
         f"• <b>About project</b>\n\n"
         f"• <b>Support</b>\n\n"
         f"• <b>Subscribe to our channel</b></blockquote>\n")

    await message.answer(text, parse_mode='HTML')

#####################################################