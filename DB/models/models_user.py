from typing import Optional
from sqlalchemy import BigInteger, String, ForeignKey, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import datetime

from DB.settings_db import Base


#####################################################
# model user
class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)  # index ускорит поиск
    username: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())  # Когда бот его впервые увидел

    # Связь с подпиской (Один-к-одному)
    # uselist=False делает связь именно 1-к-1, а не списком
    subscription: Mapped["Subscription"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f'<User tg_id={self.tg_id} username={self.username}>'

    def __str__(self):
        return f"@{self.username}" if self.username else f"ID: {self.tg_id}"


#####################################################
# model profile
class Profile(Base):
    __tablename__ = 'profiles'

    id: Mapped[int] = mapped_column(primary_key=True)
    role: Mapped[Optional[str]] = mapped_column(String(100), nullable=True) # Python-developer/Frontend/Backend
    level: Mapped[Optional[str]] = mapped_column(String(100), nullable=True) # Junior/Middle/Senior
    format: Mapped[Optional[str]] = mapped_column(String(100), nullable=True) # Remote/Hybrid/Office/Contract
    geolocation: Mapped[str] = mapped_column(String(100), default='Remote any') # Send Location/Remote any
    salary: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, default=None) # Salary optional
    user_id: Mapped[int] = mapped_column(BigInteger,ForeignKey('users.tg_id', ondelete='CASCADE'), unique=True)

    def __repr__(self):
        return f'{self.id}\n{self.role}\n{self.level}\n{self.format}\n{self.geolocation}\n{self.salary}\n'


#####################################################

class Subscription(Base):
    __tablename__ = 'subscriptions'

    id: Mapped[int] = mapped_column(primary_key=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('users.tg_id', ondelete='CASCADE'),
        unique=True
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Связь с моделью User (убедитесь, что в модели User есть back_populates="subscription")
    user: Mapped["User"] = relationship(back_populates="subscription")

    def __repr__(self):
        return f"<Subscription(id={self.id}, user_id={self.user_id}, active={self.is_active})>"

    def __str__(self):
        return f"Подписка #{self.id} (Пользователь: {self.user_id})"



