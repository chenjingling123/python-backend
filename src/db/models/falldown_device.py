"""
本文件定义了系统岗位表 (sys_posts) 的数据库模型。
"""
from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy import BigInteger, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import Base


class FalldownDevice(Base):
    """
    跌倒设备表 (falldown_device)
    """
    __tablename__ = 'falldown_device'
    __table_args__ = {'comment': '跌倒设备表'}

    # 主键
    Id: Mapped[int] = mapped_column('Id', BigInteger, primary_key=True, autoincrement=True, comment='设备ID')

    # 设备基本信息
    DeviceCode: Mapped[Optional[str]] = mapped_column('DeviceCode', String(128), comment='设备编码', nullable=True)
    Status: Mapped[Optional[str]] = mapped_column('Status', String(1), comment='状态', nullable=True)
    Model: Mapped[Optional[str]] = mapped_column('Model', String(128), comment='型号', nullable=True)
    ContactPhones: Mapped[Optional[str]] = mapped_column('ContactPhones', String(255), comment='家属电话',
                                                         nullable=True)
    Phone: Mapped[Optional[str]] = mapped_column('Phone', String(100), comment='电话', nullable=True)
    Flag: Mapped[Optional[str]] = mapped_column('Flag', String(128), comment='删除标识', nullable=True)

    # 审计字段
    CreateBy: Mapped[Optional[str]] = mapped_column('CreateBy', String(128), comment='创建者', nullable=True)
    CreateTime: Mapped[Optional[datetime]] = mapped_column('CreateTime', DateTime, comment='创建时间',
                                                           nullable=True)
    UpdateBy: Mapped[Optional[str]] = mapped_column('UpdateBy', String(128), comment='更新者', nullable=True)
    UpdateTime: Mapped[Optional[datetime]] = mapped_column('UpdateTime', DateTime, comment='更新时间',
                                                           nullable=True)
    DeleteTime: Mapped[Optional[datetime]] = mapped_column('DeleteTime', DateTime, comment='删除时间',
                                                           nullable=True)
    Remark: Mapped[Optional[str]] = mapped_column('Remark', String(255), comment='备注', nullable=True)