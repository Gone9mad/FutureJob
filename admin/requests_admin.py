from sqlalchemy import func, select

from loguru import logger

from DB.settings_db import async_sessions
from DB.models.models_user import Subscription, User


# count is active subscription users
async def count_users_is_sub() -> int:
    """Возвращает количество пользователей с активной подпиской"""
    try:
        async with async_sessions() as sess:
            # Создаем запрос: SELECT count(id) FROM subscriptions
            stmt = select(func.count()).select_from(Subscription)

            # Выполняем и получаем число
            result = await sess.execute(stmt)
            count = result.scalar()

            logger.info(f"Database: counted {count} active subscriptions")
            return count or 0

    except Exception as e:
        logger.exception(f"Error while counting subscriptions: {e}")
        return 0

# list all users
async def get_all_users_ids() -> list:
    async with async_sessions()as sess:
        stmt = select(User.tg_id)
        result = await sess.execute(stmt)
        user_all = result.scalars().all()
        logger.info(f"Retrieved {len(user_all)} IDs for broadcast")
        return list(user_all)

