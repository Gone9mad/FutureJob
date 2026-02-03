from sqlalchemy import select, update, delete, and_, or_

from datetime import datetime, timedelta

from loguru import logger

from DB.settings_db import async_sessions, async_engine, Base
from DB.models.models_user import User, Profile, Subscription
from Bot_API.utils import pars_profile



#####################################################
# The function first drops and then creates tables
async def init_db() -> None:
    async with async_engine.begin() as conn:
        # Используем warning, так как действие деструктивное (удаление данных)
        logger.warning("Removing old tables from the database...")
        await conn.run_sync(Base.metadata.drop_all)
        # Используем success, чтобы подчеркнуть успешный этап инициализации
        logger.info("Creating new tables...")
        await conn.run_sync(Base.metadata.create_all)

        logger.success("Database initialized successfully!")

#####################################################
# CREATE REQUESTS
#####################################################

# async func add user to DB
async def add_user(tg_id, user_name) -> None:
    async with async_sessions() as sess:
        user_name = User(tg_id=tg_id, username=user_name)
        sess.add(user_name)
        await sess.commit()

# async func add profile to DB
async def add_profile(user_id: int) -> bool:
    try:
        profiles_data = pars_profile()
        if not profiles_data:
            logger.warning("WARNING: The pars_profile function returned an empty list.")
            return False
        data = profiles_data[0]
        async with async_sessions() as sess:
            profile = Profile(**data, user_id=user_id)
            sess.add(profile)
            await sess.commit()
            return True
    except Exception as ex:
        logger.exception(f'CRITICAL ERROR IN add_profile: {ex}')
        return False


#####################################################
# READ REQUESTS
#####################################################

# an asynchronous function that retrieves a profile from the database
async def get_profile(user_tg_id):
    try:
        async with async_sessions() as sess:
            stmt = await sess.scalar(select(Profile).where(Profile.user_id == user_tg_id))
            return stmt
    except AttributeError:
        logger.exception(f'Data profile None')

# searches for and returns the profile ID of a specific user
async def get_profile_id_by_tg(tg_id: int) -> int:
    async with async_sessions() as sess:
        result = await sess.execute(
            select(Profile.id).where(Profile.user_id == tg_id)
        )
        profile_id = result.scalar_one_or_none()
        return profile_id

# The function checks whether the user has a subscription.
async def check_user_subscription(user_id: int) -> bool:
    async with async_sessions() as sess:
        query = select(Subscription).where(
            and_(
                Subscription.user_id == user_id,
                Subscription.is_active == True,
                # Подписка активна, если expires_at еще не наступил
                # или если он вообще не указан (бессрочно)
                or_(
                    Subscription.expires_at > datetime.now(),
                    Subscription.expires_at.is_(None)
                )
            )
        )
        result = await sess.execute(query)
        sub = result.scalar_one_or_none()
        return sub is not None

# The function activates the subscription for the user
async def activate_subscription(user_id: int, days: int = 30) -> None:
    async with async_sessions() as sess:
        # Считаем дату окончания
        expire_date = datetime.now() + timedelta(days=days)

        # Запрос: если есть - обнови, если нет - создай (Upsert)
        query = select(Subscription).where(Subscription.user_id == user_id)
        result = await sess.execute(query)
        sub = result.scalar_one_or_none()

        if sub:
            sub.is_active = True
            sub.expires_at = expire_date
        else:
            new_sub = Subscription(user_id=user_id, is_active=True, expires_at=expire_date)
            sess.add(new_sub)

        await sess.commit()


async def get_subscription_for_user(user_id: int) -> list[Subscription]:
    async with async_sessions() as sess:
        stmt = select(Subscription).where(Subscription.user_id == user_id)

        result = await sess.execute(stmt)
        subscriptions = result.scalars().all()  # Получаем чистый список объектов

        if not subscriptions:
            logger.warning(f"No subscriptions found for user_id: {user_id}")
            return []  # Возвращаем пустой список, это удобнее для циклов

        logger.info(f"Retrieved {len(subscriptions)} subscriptions for user_id: {user_id}")
        return subscriptions



#####################################################
# UPDATE REQUESTS
#####################################################

# update all data profile
async def update_prof(profile_id: int, **update_date) -> None:
    try:
        if not update_date:
            logger.warning('Problem updating profile')
            return

        async with async_sessions() as sess:
            stmt = (update(Profile).where(Profile.id == profile_id).values(**update_date))
            await sess.execute(stmt)
            await sess.commit()
    except Exception as ex:
        logger.exception(f'Error: {ex}')

#####################################################
# DELETE REQUESTS
#####################################################

# delete profile
async def delete_profile(user_tg_id: int):
    try:
        async with async_sessions() as sess:
            stmt = delete(Profile).where(Profile.user_id == user_tg_id)

            result = await sess.execute(stmt)
            await sess.commit()

            if result.rowcount > 0:
                return
            else:
                logger.warning(f'Профиль пользователя {user_tg_id} не найден')
                return

    except Exception as ex:
        logger.exception(f"Error: {ex}")

# delete user
async def del_user(user_id: int) -> bool:
    try:
        async with async_sessions() as sess:
            stmt = delete(User).where(User.tg_id == user_id)
            result = await sess.execute(stmt)
            await sess.commit()

            if result.rowcount > 0:
                return True
            else:
                return False
    except Exception as ex:
        logger.exception(f"Error: {ex}")
        return False

#####################################################



'''
async def cmd_start(message: Message, repo: UserRepo):

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

class UserRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, tg_id: int, username: str):
        user = User(tg_id=tg_id, username=username)
        self.session.add(user)
        await self.session.commit()

    async def delete(self, tg_id: int) -> bool:
        stmt = delete(User).where(User.tg_id == tg_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

class ProfileRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, user_id: int, data: dict):
        profile = Profile(**data, user_id=user_id)
        self.session.add(profile)
        await self.session.commit()
        return True

    async def get_by_tg_id(self, tg_id: int):
        result = await self.session.execute(
            select(Profile).where(Profile.user_id == tg_id)
        )
        return result.scalar_one_or_none()
'''
