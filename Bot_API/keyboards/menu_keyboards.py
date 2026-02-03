from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton




# reply markup menu
menu_markup = ReplyKeyboardMarkup(keyboard=[
        [
            KeyboardButton(text='Главная'),
            KeyboardButton(text='Профиль'),
            KeyboardButton(text='Лента'),
        ],
        [
            KeyboardButton(text='Подписки'),
            KeyboardButton(text='Избранное'),
            KeyboardButton(text='Доп.сервис'),
        ],
        [
            KeyboardButton(text='help')
        ]
    ], resize_keyboard=True, one_time_keyboard=False)


