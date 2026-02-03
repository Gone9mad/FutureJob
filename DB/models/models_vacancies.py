from typing import Optional

from sqlalchemy import String, ForeignKey, BigInteger
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from datetime import datetime

from DB.settings_db import Base

#####################################################
# model vacanсy
class Vacancy(Base):
    __tablename__ = 'vacancies'

    id: Mapped[int] = mapped_column(primary_key=True)
    name_vacancy: Mapped[str] = mapped_column(String(40))
    name_company: Mapped[str] = mapped_column(String(40))
    salary: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    geolocation: Mapped[str] = mapped_column(String(40))
    description: Mapped[str] = mapped_column(String())
    requirement: Mapped[str] = mapped_column(String())
    contact: Mapped[str] = mapped_column(String())
    create_at: Mapped[datetime] = mapped_column(server_default=func.now())

    def __repr__(self):
        return f'{self.id}\n{self.name_vacancy}\n{self.name_company}\n{self.salary}'


#####################################################
# model favorite
class Favorite(Base):
    __tablename__ = 'favorites'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.tg_id', ondelete='CASCADE'))
    vacancy_id: Mapped[int] = mapped_column(ForeignKey('vacancies.id', ondelete='CASCADE'))

    def __repr__(self):
        return f'{self.id}\n{self.user_id}\n{self.vacancy_id}'
