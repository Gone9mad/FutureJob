from aiogram.types import InlineKeyboardButton, KeyboardButton, InlineKeyboardMarkup


def admin_markup():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='👥 Кол-во подписанных', callback_data='admin_subs')],
        [InlineKeyboardButton(text='📢 Рассылка', callback_data='admin_broadcast')]
    ])


