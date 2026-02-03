from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


#####################################################
# inline markup profile
def inline_markup_profile(is_active: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text='🔁 Обновить', callback_data='update'),
        InlineKeyboardButton(text='🗑 Удалить', callback_data='delete')
    )

    if not is_active:
        builder.row(
            InlineKeyboardButton(text='🔖 Купить подписку', callback_data='subscription')
        )

    return builder.as_markup()


#####################################################
# inline keyboard under the vacancy
def get_vacancy_keyboard(vacancy_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='❤️', callback_data=f'fav_{vacancy_id}'),
            InlineKeyboardButton(text='👎', callback_data=f'hide_{vacancy_id}'),
        ]
    ])

#####################################################
# The function that generates the inline keyboard has an ID in each response.
def favorites_keyboard(vacancy_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
           [
              InlineKeyboardButton(text='🗑', callback_data=f'delete_{vacancy_id}')
           ]
    ])

#####################################################
