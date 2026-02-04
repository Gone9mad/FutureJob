from sqlalchemy import select, insert, delete

from loguru import logger

from DB.models.models_user import Profile
from DB.models.models_vacancies import Vacancy, Favorite
from DB.settings_db import async_sessions




#####################################################
# CREATE REQUESTS
#####################################################

# add data vacancies to DB
# async def add_vacancy() -> None:
#     try:
#         data = await async_settings_pw()
#         async with async_sessions() as sess:
#             vacancy = Vacancy(
#                                 name_vacancy=data[0],
#                                 name_company=data[1],
#                                 salary=data[2],
#                                 geolocation=data[3],
#                                 description=data[4],
#                                 requirement=data[5]
#                               )
#             sess.add(vacancy)
#             await sess.commit()
#     except Exception as ex:
#         logger.exception(f'Error: {ex}')

# add vacancy to favorites
async def add_to_favorites(user_id: int, vacancy_id: int):
    async with async_sessions() as sess:
        try:
            stmt = insert(Favorite).values(user_id=user_id, vacancy_id=vacancy_id)
            await sess.execute(stmt)
            await sess.commit()
        except Exception as e:
            logger.exception(f"Ошибка: {e}")
            return False

#####################################################
# READ REQUESTS
#####################################################

# get all vacancies
async def get_vacancy(profile, limit, offset=0):
    try:
        async with async_sessions() as sess:
            query = (
                select(Vacancy)
                .where(Vacancy.name_vacancy.ilike(f"%{profile.role}%"))
                .limit(limit)
                .offset(offset)  # Пропускаем уже просмотренные
                .order_by(Vacancy.id.desc())
            )
            result = await sess.execute(query)
            return result.scalars().all()
    except Exception as e:
        logger.exception(f"Error: {e}")
        return []


# get list from favorites
async def get_from_favorite(user_id):
    async with async_sessions() as sess:
        try:
            stmt = (
                select(Vacancy)
                .join(Favorite, Vacancy.id == Favorite.vacancy_id)
                .where(Favorite.user_id == user_id)
            )

            result = await sess.scalars(stmt)
            return result.all()
        except Exception as ex:
            logger.exception(f'Error: {ex}')
#
async def check_if_favorite_exists(user_id: int, vacancy_id: int):
    async with async_sessions() as sess:
        res = await sess.execute(
            select(Favorite).where(
                Favorite.user_id == user_id,
                Favorite.vacancy_id == vacancy_id
            )
        )
        return res.scalar_one_or_none() is not None

#####################################################
# DELETE REQUESTS
#####################################################

# delete from favorites
async def del_from_favorite(user_id, vacancy_id):
    try:
        async with async_sessions() as sess:
            stmt = (
                delete(Favorite)
                .where(Favorite.user_id == user_id)
                .where(Favorite.vacancy_id == vacancy_id)
            )
            result = await sess.execute(stmt)
            await sess.commit()
            if result.rowcount > 0:
                return
            else:
                return
    except Exception as ex:
        logger.exception(f"Error: {ex}")

# delete vacancy
async def del_vacancy_id(vacancy_id):
    try:
        async with async_sessions() as sess:
            stmt = (delete(Vacancy).where(Vacancy.id == vacancy_id))
            result = await sess.execute(stmt)
            await sess.commit()
            return result.rowcount > 0
    except Exception as e:
        logger.exception(f'error: {e}')

#####################################################
