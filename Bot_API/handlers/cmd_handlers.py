'''
    Module with handlers commands
'''

import io
from pathlib import Path

from loguru import logger

from aiogram.filters import Command, CommandStart
from aiogram.types import Message, ContentType
from aiogram import Router, F

from Bot_API.keyboards.menu_keyboards import menu_markup
from DB.requests.requests import add_user, add_profile


router_commands = Router()

SAVE_PATH = Path.home() / 'PycharmProjects' / 'TG_Bot_Project_working_CV' / 'downloaded' / 'profile.csv'

SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)

#####################################################
# Handler commands start
@router_commands.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await add_user(tg_id=message.from_user.id, user_name=message.from_user.username)
    text = ('👋 <b>Добро пожаловать в FutureJob!</b>\n\n'
            '\tЯ помогу вам найти идеальную работу, основываясь на вашем опыте и навыках.\n'
            '\tБольше не нужно перелистывать сотни неактуальных вакансий!\n\n'
            'Чтобы начать:\n'
            '\t📝 Создайте профиль — это позволит мне\n'
            '\t\tподбирать вакансии лично под вас.\n'
            '\t📄 Загрузите свое CV (PDF/DOCX) — я\n'
            '\t\tмгновенно проанализирую ваши качества\n'
            '\t\tкачества и сформирую личный кабинет.\n\n'
            '🚀 <i>Готовы сделать шаг навстречу новой карьере? Просто отправьте мне ваш файл с резюме!</i>\n'
            )
    logger.success('the start command worked')
    await message.answer(text, parse_mode="HTML")


#####################################################
# Handler await DOCUMENT.csv
@router_commands.message(F.content_type == ContentType.DOCUMENT)
async def process_message(message: Message) -> None:
    user_id = message.from_user.id
    if message.document and message.document.file_name.endswith(".csv"):
        try:
            file_buffer = io.BytesIO()
            await message.bot.download(file=message.document.file_id, destination=file_buffer)
            file_buffer.seek(0)
            data = file_buffer.read().decode('utf-8')
            with open(SAVE_PATH, 'w') as file:
                file.write(data)
            file_buffer.close()
            add_prof = await add_profile(user_id)
            text = (f'✅ Документ успешно загружен!\n\n'
                    f'⚙️ Генерирую ваш цифровой профиль...\n'
                    f'🔎 Ищем лучшие совпадения по вакансиям.\n\n'
                    f'<i>Подождите еще мгновение...</i> ⏳\n')

            await message.answer(text, add_prof, reply_markup=menu_markup, parse_mode="HTML")
        except Exception as e:
            logger.exception(f"Download error CSV : {e}")
            await message.reply("⛔️Произошла ошибка при скачивании файла (404 Not Found).")
    else:
        await message.answer('Вы отправили документ не того формата')


