from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import BigInteger, DateTime, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import Base


class ProjectInfo(Base):
    __tablename__ = 'project_info'
    __table_args__ = {'comment': 'project_info'}

    id: Mapped[int] = mapped_column('Id', Integer, primary_key=True, autoincrement=True)
    prjName: Mapped[Optional[str]] = mapped_column('PrjName', String(45), nullable=True)
    prjCode: Mapped[Optional[str]] = mapped_column('PrjCode', String(100), nullable=True)
    prjType: Mapped[Optional[int]] = mapped_column('PrjType', BigInteger, nullable=True)
    prjStatus: Mapped[Optional[str]] = mapped_column('PrjStatus', String(45), nullable=True)
    prjDesc: Mapped[Optional[str]] = mapped_column('PrjDesc', String(245), nullable=True)
    startDate: Mapped[Optional[datetime]] = mapped_column('StartDate', DateTime, nullable=True)
    endDate: Mapped[Optional[datetime]] = mapped_column('EndDate', DateTime, nullable=True)
    manager: Mapped[Optional[str]] = mapped_column('Manager', String(45), nullable=True)
    money: Mapped[Optional[Decimal]] = mapped_column('Money', Numeric(10, 0), nullable=True)
    remark: Mapped[Optional[str]] = mapped_column('Remark', String(245), nullable=True)
    createBy: Mapped[Optional[str]] = mapped_column('CreateBy', String(45), nullable=True)
    updateBy: Mapped[Optional[str]] = mapped_column('UpdateBy', String(45), nullable=True)
    create_time: Mapped[Optional[datetime]] = mapped_column('CreateTime', DateTime, nullable=True)
    update_time: Mapped[Optional[datetime]] = mapped_column('UpdateTime', DateTime, nullable=True)
    delete_time: Mapped[Optional[datetime]] = mapped_column('DeleteTime', DateTime, nullable=True)
